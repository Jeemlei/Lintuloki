CREATE TABLE Users (
    id SERIAL PRIMARY KEY,
    realname VARCHAR(32),
    username VARCHAR(16) UNIQUE NOT NULL,
    psswrdhash TEXT NOT NULL,
    admin_status BOOLEAN NOT NULL DEFAULT false
);

CREATE TABLE Locations (
    id SERIAL PRIMARY KEY,
    muni TEXT UNIQUE NOT NULL,
    prov TEXT,
    country TEXT NOT NULL
);

CREATE TABLE Birds (
    id SERIAL PRIMARY KEY,
    sci TEXT UNIQUE NOT NULL,
    fi TEXT UNIQUE NOT NULL,
    sv TEXT UNIQUE,
    en TEXT UNIQUE
);

CREATE TYPE banded_status AS ENUM ('true', 'false', 'not_known');

CREATE TABLE Observations (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES Users (id),
    location_id INTEGER NOT NULL REFERENCES Locations (id),
    bird_id INTEGER NOT NULL REFERENCES Birds (id),
    bird_count INTEGER NOT NULL,
    observation_date DATE NOT NULL,
    banded banded_status NOT NULL DEFAULT 'not_known',
    band_serial TEXT
);

CREATE TABLE Comments (
    id SERIAL PRIMARY KEY,
    observation_id INTEGER NOT NULL REFERENCES Observations (id),
    user_id INTEGER NOT NULL REFERENCES Users (id),
    content TEXT NOT NULL,
    posting_time TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP(0)
);

CREATE TABLE Images (
    id SERIAL PRIMARY KEY,
    observation_id INTEGER NOT NULL REFERENCES Observations (id),
    user_id INTEGER NOT NULL REFERENCES Users (id),
    imagename TEXT NOT NULL,
    binarydata BYTEA NOT NULL
);