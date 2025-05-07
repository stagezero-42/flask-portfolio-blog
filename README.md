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

## Deployment

When moving this application to a production environment, several critical steps must be taken to ensure security, performance, and reliability. Firstly, **disable debug mode** by setting `FLASK_DEBUG=0` or ensuring `FLASK_ENV=production` in your environment; this prevents exposure of sensitive debugging information. Secondly, the Flask development server is not suitable for production use. Instead, deploy your application using a **production-grade WSGI server** such as Gunicorn (which is already in `requirements.txt`) or uWSGI. These servers are designed to handle multiple concurrent requests efficiently. It's also highly recommended to place a **reverse proxy like Nginx** in front of your WSGI server. Nginx can handle tasks like SSL/TLS termination (for HTTPS), serving static files directly (which is more efficient than Flask doing it), request caching, load balancing (if you scale to multiple app instances), and provide an additional layer of security. Finally, all **sensitive configurations** (like `SECRET_KEY`, `DATABASE_URL`, API keys) must be managed securely as environment variables in your production server, never hardcoded or committed to version control. Consider using your hosting provider's mechanisms for setting environment variables or a dedicated secrets management tool.

* Ensure `FLASK_DEBUG` is `0` or `FLASK_ENV` is `production`.
* Use a production-grade WSGI server like Gunicorn or uWSGI.
* Consider using a reverse proxy like Nginx.
* Set environment variables (like `SECRET_KEY`, `DATABASE_URL`) securely in your production environment.