# ITL313-18 (SIA 2 LAB) - Final Term Mini Project

**Category:** 3B Utilities (Python + Tkinter + SQLite)

## Features
- Login / Register (SQLite, salted PBKDF2 password hashing via `hashlib`)
- 3B.1 URL Shortener
- 3B.2 SMS and Email (Gmail SMTP, Semaphore SMS API)
- 3B.3 Fake Data Generator (10 fields, 10+ records, stored in SQLite, CSV export)

## Setup
```
pip install -r requirements.txt
python utilities_app.py
```

## Notes
- Email needs a Gmail App Password. SMS needs a Semaphore API key.
- Never commit passwords or API keys. The database file is git-ignored.

## Team
- Rayah Jenine Paje
- Raven Rillera
