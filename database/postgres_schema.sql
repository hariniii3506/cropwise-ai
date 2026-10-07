-- CROPWISE AI - PostgreSQL Database Schema (Neon / Supabase / PostgreSQL)
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    mobile TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    farm_location TEXT NOT NULL,
    land_area DOUBLE PRECISION NOT NULL,
    land_unit TEXT DEFAULT 'Acres',
    preferred_soil TEXT DEFAULT 'Loamy',
    avatar TEXT DEFAULT 'farmer1',
    is_verified INTEGER DEFAULT 1,
    otp_hash TEXT DEFAULT NULL,
    otp_expiry DOUBLE PRECISION DEFAULT NULL,
    otp_attempts INTEGER DEFAULT 0,
    otp_sent_at DOUBLE PRECISION DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS recommendations (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    soil_type TEXT NOT NULL,
    ph DOUBLE PRECISION NOT NULL,
    temperature DOUBLE PRECISION NOT NULL,
    humidity DOUBLE PRECISION NOT NULL,
    rainfall DOUBLE PRECISION NOT NULL,
    recommended_crop TEXT NOT NULL,
    variety TEXT DEFAULT 'Standard',
    alternative_crops TEXT DEFAULT '[]',
    decision_notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS expenses (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    expense_date DATE NOT NULL,
    category TEXT NOT NULL,
    amount DOUBLE PRECISION NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS notes (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    tag TEXT DEFAULT 'General',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS reminders (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    reminder_date DATE NOT NULL,
    reminder_time TIME NOT NULL DEFAULT '00:00',
    description TEXT DEFAULT '',
    crop TEXT DEFAULT '',
    variety TEXT DEFAULT '',
    category TEXT DEFAULT 'General',
    is_completed INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
