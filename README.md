# My Flask Portfolio & Blog

A simple blog and portfolio application built with Flask.

## Setup

1.  Clone the repository.
2.  Create a virtual environment: `python -m venv venv`
3.  Activate it: `source venv/bin/activate` (Linux/macOS) or `venv\Scripts\activate` (Windows)
4.  Install dependencies: `pip install -r requirements.txt`
5.  Copy `.env.example` to `.env` and update the variables (especially `SECRET_KEY` and `DATABASE_URL`).
6.  Initialize the database: `flask db init`, `flask db migrate -m "Initial migration"`, `flask db upgrade`
7.  Run the application: `flask run`