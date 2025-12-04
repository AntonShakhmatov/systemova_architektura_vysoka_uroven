# app/Controllers/LoanDecision/inbox_decisions.py

import imaplib
import email
import os
import re
import time
from typing import Optional

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError, OperationalError

from database.database_connector import get_engine

ALLOWED_SENDERS = set(
    s.strip().lower()
    for s in os.getenv("DECISION_ALLOWED_SENDERS", "").split(",")
    if s.strip()
)

def _db_exec(query: str, params: dict) -> None:
    sql = text(query)
    for attempt in range(10):
        try:
            with get_engine().begin() as conn:
                conn.execute(sql, params)
            return
        except (OperationalError, SQLAlchemyError) as e:
            print(f"[warn] DB error (attempt {attempt+1}/10): {e}")
            time.sleep(1.0)
    raise RuntimeError("DB is unavailable after retries")


def _db_fetch_one(query: str, params: dict):
    sql = text(query)
    for attempt in range(10):
        try:
            with get_engine().connect() as conn:
                return conn.execute(sql, params).first()
        except (OperationalError, SQLAlchemyError) as e:
            print(f"[warn] DB error (attempt {attempt+1}/10): {e}")
            time.sleep(1.0)
    return None


def parse_user_id(subject: str) -> Optional[int]:
    """
    Берём последнее число из subject (на случай: "Decision user_id=123").
    """
    if not subject:
        return None
    nums = re.findall(r"\d+", subject)
    return int(nums[-1]) if nums else None


def parse_decision(body: str) -> Optional[int]:
    """
    Ищем отдельный токен 0 или 1 (например письмо может содержать подпись).
    """
    if not body:
        return None
    m = re.search(r"\b([01])\b", body.strip())
    return int(m.group(1)) if m else None


def get_text_body(msg: email.message.Message) -> str:
    if msg.is_multipart():
        for part in msg.walk():
            ctype = part.get_content_type()
            disp = str(part.get("Content-Disposition") or "")
            if ctype == "text/plain" and "attachment" not in disp.lower():
                payload = part.get_payload(decode=True) or b""
                charset = part.get_content_charset() or "utf-8"
                return payload.decode(charset, errors="replace")
        for part in msg.walk():
            if part.get_content_maintype() == "text":
                payload = part.get_payload(decode=True) or b""
                charset = part.get_content_charset() or "utf-8"
                return payload.decode(charset, errors="replace")
        return ""
    else:
        payload = msg.get_payload(decode=True) or b""
        charset = msg.get_content_charset() or "utf-8"
        return payload.decode(charset, errors="replace")


def already_processed(message_id: str) -> bool:
    if not message_id:
        return False
    row = _db_fetch_one(
        "SELECT email_message_id FROM processed_emails WHERE email_message_id = :mid",
        {"mid": message_id},
    )
    return bool(row)


def mark_processed(message_id: str) -> None:
    if not message_id:
        return
    _db_exec(
        "INSERT OR IGNORE INTO processed_emails(email_message_id) VALUES (:mid)",
        {"mid": message_id},
    )


def save_decision(
    user_id: int,
    decision: int,
    from_email: str,
    message_id: str,
    subject: str,
) -> None:
    _db_exec(
        """
        INSERT INTO loan_decisions(user_id, decision, decided_from, email_message_id, email_subject)
        VALUES (:uid, :decision, :from_email, :mid, :subject)
        """,
        {
            "uid": user_id,
            "decision": decision,
            "from_email": from_email,
            "mid": message_id,
            "subject": subject,
        },
    )

    _db_exec(
        """
        UPDATE loan_request
        SET status = :status
        WHERE user_id = :uid AND status = 'pending'
        """,
        {"uid": user_id, "status": "approved" if decision == 1 else "rejected"},
    )


def user_exists(user_id: int) -> bool:
    row = _db_fetch_one(
        "SELECT 1 FROM users WHERE user_id = :uid LIMIT 1",
        {"uid": user_id},
    )
    return bool(row)


def connect_imap() -> imaplib.IMAP4_SSL:
    host = os.getenv("IMAP_HOST", "")
    user = os.getenv("IMAP_USER", "")
    password = os.getenv("IMAP_PASSWORD", "")
    if not host or not user or not password:
        raise RuntimeError("Set IMAP_HOST, IMAP_USER, IMAP_PASSWORD env vars")

    port = int(os.getenv("IMAP_PORT", "993"))
    imap = imaplib.IMAP4_SSL(host, port)
    imap.login(user, password)
    return imap


def process_inbox_once() -> None:
    imap = connect_imap()
    try:
        imap.select("INBOX")

        status, data = imap.search(None, "UNSEEN")
        if status != "OK":
            print("[warn] IMAP search failed")
            return

        ids = data[0].split()
        if not ids:
            print("No new decision emails.")
            return

        for msg_id in ids:
            status, fetched = imap.fetch(msg_id, "(RFC822)")
            if status != "OK":
                continue

            raw = fetched[0][1]
            msg = email.message_from_bytes(raw)

            subject = str(email.header.make_header(email.header.decode_header(msg.get("Subject", ""))))
            from_header = msg.get("From", "") or ""
            message_id = (msg.get("Message-ID", "") or "").strip()

            if message_id and already_processed(message_id):
                imap.store(msg_id, "+FLAGS", "\\Seen")
                continue

            from_email_match = re.search(r"<([^>]+)>", from_header)
            from_email = (from_email_match.group(1) if from_email_match else from_header).strip().lower()

            if ALLOWED_SENDERS and from_email not in ALLOWED_SENDERS:
                print(f"[skip] sender not allowed: {from_email}")
                imap.store(msg_id, "+FLAGS", "\\Seen")
                if message_id:
                    mark_processed(message_id)
                continue

            body_text = get_text_body(msg)

            uid = parse_user_id(subject)
            decision = parse_decision(body_text)

            if uid is None or decision is None:
                print(f"[skip] cannot parse uid/decision. subject='{subject}'")
                imap.store(msg_id, "+FLAGS", "\\Seen")
                if message_id:
                    mark_processed(message_id)
                continue

            if not user_exists(uid):
                print(f"[skip] user_id not found: {uid}")
                imap.store(msg_id, "+FLAGS", "\\Seen")
                if message_id:
                    mark_processed(message_id)
                continue

            try:
                save_decision(uid, decision, from_email, message_id, subject)
                if message_id:
                    mark_processed(message_id)
                imap.store(msg_id, "+FLAGS", "\\Seen")
                print(f"[ok] saved decision user_id={uid} decision={decision}")
            except Exception as e:
                print(f"[error] saving decision failed: {e}")
                continue

    finally:
        try:
            imap.close()
        except Exception:
            pass
        imap.logout()


if __name__ == "__main__":
    process_inbox_once()
