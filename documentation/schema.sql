CREATE TABLE Users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(16) UNIQUE,
    realname VARCHAR(16),
    psswrdhash TEXT
);

CREATE TABLE Locations (
    id SERIAL PRIMARY KEY,
    muni TEXT UNIQUE,
    prov TEXT,
    country TEXT
);

CREATE TABLE Birds (
    id SERIAL PRIMARY KEY,
    sci TEXT,
    fi TEXT,
    sv TEXT,
    en TEXT
);

CREATE TYPE banded_status AS ENUM ('true', 'false', 'not_known');

CREATE TABLE Observations (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES Users (id),
    location_id INTEGER REFERENCES Locations (id),
    bird_id INTEGER REFERENCES Birds (id),
    bird_count INTEGER,
    banded banded_status,
    band_serial TEXT
);

CREATE TABLE comments (
    id SERIAL PRIMARY KEY,
    observation_id INTEGER REFERENCES Observations (id),
    user_id INTEGER REFERENCES Users (id),
    content TEXT
);

CREATE TABLE images (
    id SERIAL PRIMARY KEY,
    observation_id INTEGER REFERENCES Observations (id),
    user_id INTEGER REFERENCES Users (id),
    data BYTEA
);