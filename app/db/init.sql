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

CREATE TABLE IF NOT EXISTS loan_request(
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NOT NULL,
  loan_amount DECIMAL(15, 2) NOT NULL,
  percent DECIMAL(15,2) NOT NULL,
  total_monthly_installment DECIMAL(15, 2) NOT NULL,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  
  INDEX idx_loan_request_user_id (user_id),
  CONSTRAINT fk_loan_request_user
    FOREIGN KEY (user_id) REFERENCES users(user_id)
    ON DELETE CASCADE ON UPDATE CASCADE
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
    total_monthly_installment
) VALUES (
    1, 
    10000000,
    12,
    145000
);


-- CREATE TABLE IF NOT EXISTS loan_history_active (
--     id INT AUTO_INCREMENT PRIMARY KEY,
--     user_id INT NOT NULL,
--     opened_date DATETIME NOT NULL,
--     remaining_balance DECIMAL(15,2) NOT NULL,
--     monthly_installment DECIMAL(15,2) NOT NULL,
--     status VARCHAR(50) NOT NULL,
--     created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
--     updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
--     INDEX idx_loan_history_user_id (user_id),
--     CONSTRAINT fk_loan_history_profile
--       FOREIGN KEY (user_id) REFERENCES profiles(user_id)
--       ON DELETE CASCADE ON UPDATE CASCADE
-- ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- CREATE TABLE IF NOT EXISTS loan_history_closed (
--     id INT AUTO_INCREMENT PRIMARY KEY,
--     user_id INT NOT NULL,
--     opened_date DATETIME NOT NULL,
--     closed_date DATETIME NOT NULL,
--     total_paid DECIMAL(15,2) NOT NULL,
--     status VARCHAR(50) NOT NULL,
--     created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
--     updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
--     INDEX idx_loan_history_user_id (user_id),
--     CONSTRAINT fk_loan_history_profile
--       FOREIGN KEY (user_id) REFERENCES profiles(user_id)
--       ON DELETE CASCADE ON UPDATE CASCADE
-- ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- CREATE TABLE IF NOT EXISTS delinquency_dates (
--     id INT AUTO_INCREMENT PRIMARY KEY,
--     user_id INT NOT NULL,
--     current_arrears_days INT NOT NULL,
--     max_arrears_12_months INT NOT NULL,
--     max_arrears_lifetime INT NOT NULL,
--     arrearc_dates_12_months LONGTEXT NOT NULL,
--     has_written_off_loans BOOLEAN NOT NULL,
--     has_restructurings BOOLEAN NOT NULL,
--     created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
--     updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
--     INDEX idx_delinquency_user_id (user_id),
--     CONSTRAINT fk_delinquency_profile
--       FOREIGN KEY (user_id) REFERENCES profiles(user_id)
--       ON DELETE CASCADE ON UPDATE CASCADE
-- ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- CREATE TABLE IF NOT EXISTS financial_obligations (
--   id INT AUTO_INCREMENT PRIMARY KEY,
--   user_id INT NOT NULL,
--   monthly_obligations DECIMAL(15,2) NOT NULL,
--   total_outstanding_loans DECIMAL(15,2) NOT NULL,
--   number_of_active_loans INT NOT NULL,
--   number_of_closed_loans INT NOT NULL,
--   created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
--   updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
--   INDEX idx_users_profile_id (user_id),
--   CONSTRAINT fk_users_profile
--     FOREIGN KEY (user_id) REFERENCES profiles(user_id)
--     ON DELETE CASCADE ON UPDATE CASCADE
-- ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- CREATE TABLE IF NOT EXISTS enquiries (
--   id INT AUTO_INCREMENT PRIMARY KEY,
--   user_id INT NOT NULL,
--   enquiries_last_6_months INT NOT NULL,
--   enquiries_last_12_months INT NOT NULL,
--   enquiries_rejected_applications INT NOT NULL,
--   recent_inquiries_details LONGTEXT NOT NULL,
--   created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
--   updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
--   INDEX idx_enquiries_user_id (user_id),
--   CONSTRAINT fk_enquiries_profile
--     FOREIGN KEY (user_id) REFERENCES profiles(user_id)
--     ON DELETE CASCADE ON UPDATE CASCADE
-- ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- CREATE TABLE IF NOT EXISTS risk_flags (
--   id INT AUTO_INCREMENT PRIMARY KEY,
--   user_id INT NOT NULL,
--   risk_score DECIMAL(5,2) NOT NULL,
--   risk_bands VARCHAR(50) NOT NULL,
--   fraud_flags LONGTEXT NOT NULL,
--   adress_missmatch BOOLEAN NOT NULL,
--   identity_consistency_score DECIMAL(5,2) NOT NULL,
--   created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
--   updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
--   INDEX idx_risk_flags_user_id (user_id),
--   CONSTRAINT fk_risk_flags_profile
--     FOREIGN KEY (user_id) REFERENCES profiles(user_id)
--     ON DELETE CASCADE ON UPDATE CASCADE
-- ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;