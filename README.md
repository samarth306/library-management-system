
# Library Management System API (FastAPI + SQLAlchemy + MySQL)

This project is a RESTful API built with **FastAPI**, **SQLAlchemy**, and **MySQL**. Dependency management is handled by **Poetry**.

## 📁 Project Structure

```
project-root/
│
├── app/
│   ├── database.py       # Update your DATABASE_URL here
│   └── ...
├── alembic.ini           # Update sqlalchemy.url here
├── pyproject.toml        # Poetry configuration file
├── poetry.lock           # Poetry lock file
├── .gitignore            # Ignores .venv, __pycache__, etc.
└── README.md             # This file
```

---

## ⚙️ Setup Instructions

### 1. Clone the repository

```bash
git clone https://github.com/company/repo-name.git
cd repo-name
```

### 2. Install Poetry

```bash
pip install poetry
```

### 3. Install dependencies

```bash
poetry install
```

### 4. Create `.env` file

Create a `.env` file in the project root and add the following environment variables:

```
SECRET_KEY=
DATABASE_URL="mysql+pymysql://<username>:<password>@localhost:3306/<database_name>"
ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_ALGORITHM=
TOKEN_SCHEME=
HONEYCOMB_API_KEY=
OTEL_EXPORTER_OTLP_ENDPOINT=https://api.honeycomb.io
OTEL_SERVICE_NAME=library-management-api
```

Example:

```
DATABASE_URL=mysql+pymysql://root:varun@localhost:3306/python
```

---

## 🚀 Running the App

Start the FastAPI app using Poetry:

```bash
poetry run uvicorn app.main:app --reload
```

---

## 🧪 Testing the API

Test the API endpoints using:
- Postman
- Swagger UI: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- Any REST client

---

## 📦 Notes

- This project uses `poetry` for dependency management.
- `.venv` and `__pycache__` are ignored from Git.
- Ensure `main.py` is in the correct path (`app/main.py`).
