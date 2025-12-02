# Kredit FastAPI – Demo flow (README)

Tento projekt demonstruje zpracování úvěrové žádosti od podání až po finální rozhodnutí kreditního specialisty přes e-mail.

---

## Flow systému (1–7)

### 1) Signup (v demo může chybět jako endpoint)
Uživatel již existuje v databázi v tabulce **`users`**. Povinná pole:

- `name`, `lastname`, `birthdate`, `rodne_cislo`
- `phone`, `email`, `address`
- `employment_place`, `employment_type`, `monthly_income`

Tato data se používají pro validaci a scoring.

---

### 2) Podání online žádosti (`/app/request/loan.py`)
Klient odešle úvěrovou žádost.

**Vstupní pole:**
- `loan_amount`
- `percent`
- `term`
- `total_monthly_installment`

Po odeslání se `user_id` uloží do tabulky **`loan_request_ids`**.  
Dále systém pracuje **pouze** s uživateli, jejichž `user_id` je v tabulce `loan_request_ids`.

(Pro demo není potřeba rozšířená data – stačí tato základní data.)

---

### 3) Validace (`/app/request/validator.py`)
Probíhá kontrola:
- formátu a povinnosti signup dat (např. phone/email)
- parametrů úvěru (`loan_amount`, `term`, `percent`, `total_monthly_installment`)
- jednoduchého business pravidla (např. splátka nesmí být příliš vysoká vzhledem k příjmu)

Validace se provádí na základě dat uložených při signup + parametrů konkrétní žádosti.

---

### 4) Kreditní registr → CSV (`/app/api_registr/loan_history.py`)
Systém se spojí s fiktivním registrem:

`https://registry.example.com/api/credit-check/{name}/{lastname}/{birthdate}/{rodne_cislo}`

Získaný JSON uloží jako CSV do složky:

`/app/uploads`

Soubor se vytváří pod individuálním názvem, např.:

`{name}_{lastname}_{birthdate}_loan_history.csv`

---

### 5) Výpočet scoringu (`/app/calculate/main.py`)
Systém vypočítá úvěrový scoring (loan score) a rizikovou kategorii.

**Použité zdroje:**
- data z DB (`users`)
- kreditní historie z CSV (`/app/uploads`)

Vše se načítá/spravuje **podle `user_id`**.  
Výsledek se uloží do databáze a vrátí přes API.

---

### 6) Odeslání výsledku specialistovi e-mailem (`/app/mailing/mailing.py`)
Systém odešle e-mail kreditnímu specialistovi s:
- profilem klienta
- parametry úvěru
- `loan_score`, `risk_level`, `reason`

---

### 7) Rozhodnutí specialisty přes e-mail → zápis do DB (`/app/decision/inbox_decision.py`)
Specialista odpoví na e-mail:

**Příklad:**
- Subject: `1` *(user_id)* nebo `Decision user_id=1`
- Body: `1` *(approved)* nebo `0` *(rejected)*

Skript:
- najde nové zprávy (`UNSEEN`)
- vytáhne `user_id` ze subjectu
- vytáhne `0/1` z těla
- zapíše rozhodnutí do `loan_decisions`
- aktualizuje `loan_request.status` na `approved/rejected`
- chrání se proti duplicitám přes `Message-ID`

---

@startuml
title Kredit FastAPI — Sequence (end-to-end flow)

actor Client as C
participant "FastAPI\n/app/request/loan.py" as LoanAPI
participant "Validator\n/app/request/validator.py" as V
database "DB" as DB
participant "LoanHistory\n/app/api_registr/loan_history.py" as LH
participant "Registry API\nregistry.example.com" as REG
collections "Filesystem\n/app/uploads" as FS
participant "Scoring API\n/app/calculate/main.py" as ScoreAPI
participant "Mailer\n/app/mailing/mailing.py" as Mailer
participant "SMTP server" as SMTP
actor "Credit specialist" as CS
participant "IMAP Inbox\n(mailbox)" as IMAP
participant "Inbox decision script\n/app/decision/inbox_decision.py" as Decision

== 1) Signup (already done in demo) ==
note over DB
users:
- user_id
- name, lastname, birthdate, rodne_cislo
- phone, email, address
- employment_place, employment_type, monthly_income
end note

== 2) Client submits loan request ==
C -> LoanAPI: POST /loan-requests\n{user_id, loan_amount, percent, term, total_monthly_installment}
LoanAPI -> V: validate_loan_request(user_id + params)
V -> DB: SELECT user profile by user_id
DB --> V: user data
V --> LoanAPI: ok / ValueError

LoanAPI -> DB: INSERT INTO loan_request_ids(user_id)
DB --> LoanAPI: aggregate_id
LoanAPI --> C: 200 OK\n(accepted + aggregated)

== 4) Fetch credit history & save CSV ==
LH -> DB: SELECT DISTINCT user_id FROM loan_request_ids
DB --> LH: [user_ids]
LH -> DB: SELECT name, lastname, birthdate, rodne_cislo FROM users WHERE user_id=...
DB --> LH: profile
LH -> REG: GET /credit-check/{name}/{lastname}/{birthdate}/{rodne_cislo}
REG --> LH: JSON {loans:[...]}
LH -> FS: write CSV /app/uploads/{...}_loan_history.csv

== 5) Calculate score ==
C -> ScoreAPI: GET /score/{user_id}
ScoreAPI -> DB: read users + loan params
ScoreAPI -> FS: read CSV for user_id
ScoreAPI -> DB: INSERT scoring_response/loan_scores(...)
ScoreAPI --> C: ScoreResponse {loan_score, risk_level, reason[]}

== 6) Email to credit specialist ==
Mailer -> DB: collect user + loan + latest score
Mailer -> SMTP: send email "Scoring result: <name lastname>"
SMTP --> CS: delivered email

== 7) Specialist replies with decision ==
CS -> IMAP: Reply email\nSubject: "Decision user_id=123"\nBody: "1" or "0"
Decision -> IMAP: search UNSEEN
IMAP --> Decision: email(s)
Decision -> Decision: parse user_id from Subject\nparse decision 0/1 from Body
Decision -> DB: INSERT loan_decisions(user_id, decision, email_message_id,...)
Decision -> DB: UPDATE loan_request.status = approved/rejected
Decision -> IMAP: mark Seen + dedupe by Message-ID

@enduml
