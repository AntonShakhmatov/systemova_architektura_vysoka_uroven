CREATE DATABASE IF NOT EXISTS test CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE test;


CREATE TABLE IF NOT EXISTS users (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NOT NULL UNIQUE,
  name VARCHAR(255) NOT NULL,
  lastname VARCHAR(255) NOT NULL,
  phone VARCHAR(255) NOT NULL,
  birthdate DATETIME NOT NULL,
  rodne_cislo VARCHAR(255) NOT NULL,
  email VARCHAR(255) NOT NULL,
  address VARCHAR(255) NOT NULL,
  employment_place VARCHAR(255) NOT NULL,
  employment_type VARCHAR(255) NOT NULL,
  monthly_income DECIMAL (15,2) NOT NULL,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS bank_profile (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NOT NULL UNIQUE,
  name VARCHAR(255) NOT NULL,
  lastname VARCHAR(255) NOT NULL,
  phone VARCHAR(255) NOT NULL,
  birthdate DATETIME NOT NULL,
  rodne_cislo VARCHAR(255) NOT NULL,
  email VARCHAR(255) NOT NULL,
  address VARCHAR(255) NOT NULL,
  employment_place VARCHAR(255) NOT NULL,
  employment_type VARCHAR(255) NOT NULL,
  monthly_income DECIMAL (15,2) NOT NULL,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS loan_request(
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NOT NULL,
  loan_amount DECIMAL(15, 2) NOT NULL,
  percent DECIMAL(15,2) NOT NULL,
  term INT NOT NULL,
  total_monthly_installment DECIMAL(15, 2) NOT NULL,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  
  INDEX idx_loan_request_user_id (user_id),
  CONSTRAINT fk_loan_request_user
    FOREIGN KEY (user_id) REFERENCES users(user_id)
    ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS loan_request_ids(
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NOT NULL,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS loan_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    loan_id VARCHAR(255) NOT NULL,
    loan_type VARCHAR(255) NOT NULL,
    opened_date DATETIME NOT NULL,
    closed_date DATETIME NOT NULL, 
    remaining_balance INT NOT NULL,
    monthly_installment INT NOT NULL,
    credit_limit INT,
    status VARCHAR(255) NOT NULL,
    current_arrears_days INT NOT NULL,
    max_arrears_last_12m INT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    INDEX idx_loan_history_user_id (user_id),
    CONSTRAINT fk_loan_history_user
      FOREIGN KEY (user_id) REFERENCES users(user_id)
      ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS scoring_response (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NOT NULL,
  loan_score DECIMAL(15, 2) NOT NULL,
  risk_level VARCHAR(255) NOT NULL,
  reason TEXT NOT NULL,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  
  INDEX idx_loan_history_user_id (user_id),
  CONSTRAINT fk_scoring_response_user
    FOREIGN KEY (user_id) REFERENCES users(user_id)
    ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


INSERT INTO users (
    user_id, 
    name, 
    lastname, 
    phone, 
    birthdate, 
    rodne_cislo,
    email,
    address,
    employment_place,
    employment_type, 
    monthly_income
) VALUES (
    1, 
    'Anton', 
    'Shakhmatov', 
    '+420773694287', 
    '1992-03-19', 
    '920319/1234',
    'anton@example.com',
    'Prague, Czech Republic',
    'Self-employed',
    'self-employed', 
    80000
);

INSERT INTO loan_request (
    user_id,
    loan_amount,
    percent, 
    term,
    total_monthly_installment
) VALUES (
    1, 
    10000000,
    12,
    36,
    145000
);

-- rozhodnuti
CREATE TABLE IF NOT EXISTS loan_decisions (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER NOT NULL,
  decision INTEGER NOT NULL CHECK (decision IN (0,1)),
  decided_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  decided_from TEXT,
  email_message_id TEXT UNIQUE,
  email_subject TEXT
);


CREATE TABLE IF NOT EXISTS processed_emails (
  email_message_id TEXT PRIMARY KEY,
  processed_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);