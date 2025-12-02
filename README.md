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

## Spuštění projektu (Docker)

1) Build (v souboru `kredit`)
```bash
docker compose up --build

2) Spuštění na pozadí
docker compose up -d

3)Přístup do MariaDB (všechny tabulky, se kterými systém pracuje)
docker exec -it kredit-database-1 sh
mariadb -u test -ptest
USE test;
SHOW TABLES;

4) Testování scoring endpointu (v demo je vytvořen user s user_id=1)
curl http://localhost:8000/score/1
```
Demo data:

DB se inicializuje přes: /app/db/init.sql
Demo CSV soubory jsou v: app/uploads/*.csv
Pro testování je připraven demo uživatel s user_id=1