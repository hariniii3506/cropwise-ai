-- =============================================================================
-- CROPWISE AI - Relational Database Schema Definition
-- =============================================================================
-- This file defines the core SQLite relational database tables used by CropWise AI.
-- It establishes primary keys, unique constraints, foreign key relationships with
-- cascading deletes, and default timestamp tracking for all agricultural entities.
-- =============================================================================
-- CROPWISE AI - Database Schema (SQLite / Standard SQL)
-- -----------------------------------------------------------------------------
-- Table: users
-- Stores registered farmer credentials, contact details, farm profile, and OTP verification state.
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    mobile TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    farm_location TEXT NOT NULL,
    land_area REAL NOT NULL,
    land_unit TEXT DEFAULT 'Acres',
    preferred_soil TEXT DEFAULT 'Loamy',
    avatar TEXT DEFAULT 'farmer1',
    is_verified INTEGER DEFAULT 1,
    otp_hash TEXT DEFAULT NULL,
    otp_expiry REAL DEFAULT NULL,
    otp_attempts INTEGER DEFAULT 0,
    otp_sent_at REAL DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- -----------------------------------------------------------------------------
-- Table: recommendations
-- Stores AI-generated crop recommendations, farmer input parameters, and agronomic reasoning.
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS recommendations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    soil_type TEXT NOT NULL,
    ph REAL NOT NULL,
    temperature REAL NOT NULL,
    humidity REAL NOT NULL,
    rainfall REAL NOT NULL,
    recommended_crop TEXT NOT NULL,
    variety TEXT DEFAULT 'Standard',
    alternative_crops TEXT DEFAULT '[]',
    decision_notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- -----------------------------------------------------------------------------
-- Table: expenses
-- Stores farm financial ledger records including inputs (seeds, fertilizer, labor), amounts, and dates.
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS expenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    expense_date DATE NOT NULL,
    category TEXT NOT NULL,
    amount REAL NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- -----------------------------------------------------------------------------
-- Table: notes
-- Stores agricultural field notes, observations, and agronomic reminders tagged by category.
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS notes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    tag TEXT DEFAULT 'General',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- -----------------------------------------------------------------------------
-- Table: reminders
-- Stores interactive farming calendar tasks, scheduled activities, and completion flags.
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS reminders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    reminder_date DATE NOT NULL,
    reminder_time TIME NOT NULL DEFAULT '00:00',
    description TEXT DEFAULT '',
    crop TEXT DEFAULT '',
    variety TEXT DEFAULT '',
    category TEXT DEFAULT 'General',
    is_completed INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
