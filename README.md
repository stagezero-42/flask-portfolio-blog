includes detailed sections on local setup, production deployment on Ubuntu with Gunicorn and PostgreSQL (using Caddy for HTTPS as a common advanced setup example), and specifics related to your project structure.

Markdown

# Flask Portfolio & Blog

This project is a dynamic portfolio and blog application built with Flask, SQLAlchemy for database interaction, and Flask-Migrate for database migrations. It features an administrative backend for managing posts (categorized as blog, portfolio, or home page content), footer icons, and site configuration like copyright messages. The frontend displays these posts in respective sections with pagination and uses a Trix editor for rich text content creation, including image uploads with automatic thumbnail generation.

## Table of Contents

1.  [Features](#features)
2.  [Project Structure](#project-structure)
3.  [Local Development Setup](#local-development-setup)
    * [Prerequisites](#prerequisites)
    * [Cloning the Repository](#cloning-the-repository)
    * [Virtual Environment](#virtual-environment)
    * [Installing Dependencies](#installing-dependencies)
    * [Environment Variables (.env)](#environment-variables-env)
    * [Database Initialization (SQLite)](#database-initialization-sqlite)
    * [Creating the Initial Admin User](#creating-the-initial-admin-user)
    * [Running the Development Server](#running-the-development-server)
    * [Accessing the Application](#accessing-the-application)
4.  [Production Deployment (Ubuntu 22.04)](#production-deployment-ubuntu-2204)
    * [Prerequisites for Production](#prerequisites-for-production)
    * [Server Preparation](#server-preparation)
    * [PostgreSQL Database Setup](#postgresql-database-setup)
    * [Cloning Code from Git to Server](#cloning-code-from-git-to-server)
    * [Python Virtual Environment on Server](#python-virtual-environment-on-server)
    * [Installing Production Dependencies](#installing-production-dependencies)
    * [Configuring Production Environment Variables](#configuring-production-environment-variables)
    * [Database Migrations (PostgreSQL)](#database-migrations-postgresql)
    * [Creating Production Admin User](#creating-production-admin-user)
    * [Testing with Gunicorn](#testing-with-gunicorn)
    * [Setting up Gunicorn with systemd](#setting-up-gunicorn-with-systemd)
    * [Setting up Caddy as a Reverse Proxy (for HTTPS)](#setting-up-caddy-as-a-reverse-proxy-for-https)
    * [Final Checks and Troubleshooting](#final-checks-and-troubleshooting)
5.  [Key Configuration Points for Production](#key-configuration-points-for-production)
    * [Database URL](#database-url)
    * [SECRET_KEY](#secret_key)
    * [FLASK_CONFIG](#flask_config)
    * [Static and Media Files](#static-and-media-files)
6.  [Contributing](#contributing)
7.  [License](#license)

## Features

* **Dynamic Content Management**: Admin interface to create, edit, and delete posts.
* **Post Categorization**: Posts can be assigned as 'blog', 'portfolio', or 'home' (for the featured homepage post).
* **Rich Text Editor**: Trix editor for creating post content with formatting and image uploads.
* **Image Handling**: Automatic extraction of the first image from a post for display and thumbnail generation for previews.
* **Footer Customization**: Manage footer social media icons (name, URL, image) and their display order.
* **Site Configuration**: Update site-wide settings like the copyright message (with dynamic year support).
* **User Authentication**: Secure admin login.
* **Database Migrations**: Flask-Migrate for managing database schema changes.
* **Responsive Design**: Basic responsive styling with Bootstrap.
* **Pagination**: For blog and portfolio listings.

## Project Structure

      flask-portfolio-blog/
          ├── app/                      # Main application package
          │   ├── init.py               # Application factory
          │   ├── admin/                # Admin blueprint (routes, forms, templates)
          │   │   ├── init.py
          │   │   ├── forms.py
          │   │   ├── routes.py
          │   │   └── templates/
          │   ├── main/                 # Main site blueprint (routes, templates)
          │   │   ├── init.py
          │   │   ├── routes.py
          │   │   └── templates/
          │   ├── static/               # Static files (CSS, JS, images, uploaded media)
          │   │   ├── css/
          │   │   ├── img/              # For footer icons
          │   │   ├── js/
          │   │   └── media_files/      # For Trix editor uploads
          │   ├── templates/            # Base and error templates
          │   │   ├── errors/
          │   │   └── base.html
          │   ├── config.py             # Configuration classes (Dev, Prod, Test)
          │   ├── extensions.py         # Flask extension initializations (db, migrate, etc.)
          │   └── models.py             # SQLAlchemy database models
          ├── migrations/               # Flask-Migrate migration scripts
          ├── instance/                 # Instance folder (for SQLite DB, sensitive configs - gitignored)
          │   └── app.db                # SQLite database file (for local dev)
          ├── .env                      # Environment variables (gitignored)
          ├── .flaskenv                 # Flask environment variables (e.g., FLASK_APP, FLASK_DEBUG)
          ├── .gitignore
          ├── requirements.txt          # Python dependencies
          ├── run.py                    # Script to run the application
          └── README.md



## Local Development Setup

This section guides you through setting up the project for local development.

### Prerequisites

* Python 3.8+
* `pip` (Python package installer)
* `git`
* A code editor (e.g., VS Code, PyCharm)

### Cloning the Repository

1.  Open your terminal or command prompt.
2.  Clone the repository:
    ```bash
    git clone <your-repository-url> flask-portfolio-blog
    cd flask-portfolio-blog
    ```
    (Replace `<your-repository-url>` with the actual URL of your Git repository)

### Virtual Environment

It's highly recommended to use a virtual environment.

1.  Create a virtual environment:
    ```bash
    # For Linux/macOS
    python3 -m venv venv

    # For Windows
    python -m venv venv
    ```
2.  Activate the virtual environment:
    ```bash
    # For Linux/macOS
    source venv/bin/activate

    # For Windows
    .\venv\Scripts\activate
    ```

### Installing Dependencies

Install the required Python packages from `requirements.txt` (source: `requirements.txt`):
```bash
pip install -r requirements.txt
Environment Variables (.env)
Create a .env file in the project root directory. This file stores environment-specific configurations and should be added to .gitignore.

Example .env for local development (SQLite):

Code snippet

# flask-portfolio-blog/.env

# Flask Configuration
FLASK_CONFIG='development'  # Or 'default'
FLASK_APP='run.py'          # Tells Flask how to load the app
FLASK_DEBUG=1               # Enables debug mode

# Secret Key: Generate a random string.
# Example: python -c 'import secrets; print(secrets.token_hex(32))'
SECRET_KEY='your_strong_development_secret_key'

# Database URL for local SQLite
# This path resolves to project_root/instance/app.db as per app/config.py
DATABASE_URL='sqlite:///../instance/app.db'
The application (app/config.py) is set up to create the instance/ folder if it doesn't exist when using SQLite.

Database Initialization (SQLite)
Run Flask-Migrate commands to set up your local SQLite database schema.

Initialize Migrations (if the migrations folder doesn't exist or is empty):
Bash

flask db init
Create an Initial Migration (or after any model changes):
Bash

flask db migrate -m "Initial database schema and models"
Apply the Migration to the Database:
Bash

flask db upgrade
This will create the instance/app.db file with all the tables defined in app/models.py.
Creating the Initial Admin User
You need an admin user to access the /admin section. Use the Flask shell.

Start the Flask shell:
Bash

flask shell
In the shell, run the following Python code:
Python

from app.models import User
from app.extensions import db  # Or from app import db
# from werkzeug.security import generate_password_hash # Not needed if User.set_password handles it

admin_username = 'admin'
admin_email = 'admin@example.com'
admin_password = 'your_secure_dev_password' # Change this!

# Check if user already exists
existing_user = User.query.filter_by(username=admin_username).first()
if existing_user:
    print(f"User '{admin_username}' already exists. Updating password.")
    existing_user.set_password(admin_password)
    db.session.add(existing_user)
else:
    new_admin = User(username=admin_username, email=admin_email)
    new_admin.set_password(admin_password) # This method hashes the password
    db.session.add(new_admin)
    print(f"Admin user '{admin_username}' created.")

db.session.commit()
print("Admin user setup complete.")
exit()
Your User model's set_password method (app/models.py) should handle the password hashing.
Running the Development Server
Start the Flask development server:

Bash

flask run
By default, it should be accessible at http://127.0.0.1:5000.

Accessing the Application
Main Site: http://127.0.0.1:5000
Admin Login: http://127.0.0.1:5000/admin/login (Use the credentials created above)
Production Deployment (Ubuntu 22.04)
This section details deploying the application to an Ubuntu 22.04 server using PostgreSQL as the database and Gunicorn as the WSGI HTTP server. It also includes instructions for using Caddy as a reverse proxy for automatic HTTPS.

Prerequisites for Production
An Ubuntu 22.04 server.
Root or sudo access to the server.
PostgreSQL server installed and running.
git installed on the server (sudo apt install git).
Python 3.10+ (or the version used in development) and python3-venv installed (sudo apt install python3.10-venv or similar).
A domain name (e.g., yourdomain.com) pointed to your server's public IP address (DNS A record).
Your project code hosted in a Git repository.
Server Preparation
Connect to your server via SSH:
Bash

ssh your_username@your_server_ip
Update server packages:
Bash

sudo apt update && sudo apt upgrade -y
Install essential build tools and PostgreSQL client development headers: (Required for psycopg2, the Python PostgreSQL adapter)
Bash

sudo apt install -y python3-venv build-essential libpq-dev
Create a dedicated non-root user for the application (recommended):
Bash

sudo adduser appuser
# Optionally, grant sudo rights if needed for specific tasks by this user,
# but generally, the application itself should not run with sudo.
# sudo usermod -aG sudo appuser

# Switch to the new user for subsequent steps
su - appuser
PostgreSQL Database Setup
Connect to PostgreSQL:
You might need to switch to the postgres system user first if you haven't configured other PostgreSQL admin users.

Bash

sudo -u postgres psql
Inside the psql prompt, create a database and a dedicated user:
Replace your_app_db, your_app_db_user, and your_very_strong_db_password with your choices.

SQL

-- Create the database
CREATE DATABASE your_app_db;

-- Create a user for your application
CREATE USER your_app_db_user WITH PASSWORD 'your_very_strong_db_password';

-- Configure user defaults (recommended)
ALTER ROLE your_app_db_user SET client_encoding TO 'utf8';
ALTER ROLE your_app_db_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE your_app_db_user SET timezone TO 'UTC';

-- Grant all privileges on the new database to your application user
GRANT ALL PRIVILEGES ON DATABASE your_app_db TO your_app_db_user;

-- Exit psql
\q
Your production DATABASE_URL for PostgreSQL will be:
postgresql://your_app_db_user:your_very_strong_db_password@localhost:5432/your_app_db

Cloning Code from Git to Server
As appuser (or your deployment user), navigate to the desired directory: A common location is /var/www/ or the user's home directory.
Bash

# Example: Using /var/www/
# sudo mkdir -p /var/www/yourprojectname
# sudo chown appuser:appuser /var/www/yourprojectname
# cd /var/www/yourprojectname

# Example: Using home directory
cd ~
mkdir yourprojectname
cd yourprojectname
Clone your project from Git:
Bash

git clone <your-repository-url> .
(The . clones into the current directory yourprojectname)
Python Virtual Environment on Server
Create and activate a virtual environment within your project directory: (Ensure you are appuser and in the project root: ~/yourprojectname or /var/www/yourprojectname)
Bash

python3 -m venv venv
source venv/bin/activate
Installing Production Dependencies
Install Python packages, including Gunicorn and psycopg2-binary: (Ensure your requirements.txt is up-to-date, and add Gunicorn and psycopg2 if not already present)
Bash

pip install -r requirements.txt
pip install gunicorn psycopg2-binary  # psycopg2-binary for PostgreSQL
It's good practice to add gunicorn and psycopg2-binary to your requirements.txt and commit the change.
Configuring Production Environment Variables
For production, it's crucial to manage sensitive information like SECRET_KEY and DATABASE_URL securely. You can use a .env file (read by python-dotenv in app/config.py) or set environment variables directly in your systemd service file (more secure for production).

Create or edit the .env file in your project root on the server: (e.g., ~/yourprojectname/.env or /var/www/yourprojectname/.env) Make sure this file is in your .gitignore.
Code snippet

# ~/yourprojectname/.env

FLASK_CONFIG='production'
FLASK_APP='run.py'
# FLASK_DEBUG should NOT be 1 in production

# Generate a NEW, strong, random secret key for production
SECRET_KEY='your_unique_and_strong_production_secret_key'

# PostgreSQL Database URL
DATABASE_URL='postgresql://your_app_db_user:your_very_strong_db_password@localhost:5432/your_app_db'

# Add any other production-specific variables
# Example: UPLOAD_FOLDER (if different or needs explicit path)
# UPLOAD_FOLDER='/home/appuser/yourprojectname/app/static/media_files'
Important: The SECRET_KEY must be different from your development key and very strong. The UPLOAD_FOLDER path in app/config.py uses relative paths; ensure these resolve correctly in your production environment or set an absolute path here if needed.
Database Migrations (PostgreSQL)
Apply your database migrations to the production PostgreSQL database.

(Ensure your virtual environment is activated: source venv/bin/activate)

Bash

flask db upgrade
This will create the tables in your PostgreSQL database (your_app_db).

Creating Production Admin User
Use the Flask shell on the server to create the admin user in the production PostgreSQL database.

Start the Flask shell:
Bash

flask shell
In the shell:
Python

from app.models import User
from app.extensions import db # Or from app import db

admin_username_prod = 'admin_prod' # Choose a secure admin username
admin_email_prod = 'admin@yourdomain.com' # Your admin email
admin_password_prod = 'an_extremely_strong_and_unique_password' # CHANGE THIS!

existing_user = User.query.filter_by(username=admin_username_prod).first()
if existing_user:
    print(f"User '{admin_username_prod}' already exists. If needed, update password manually or choose a different username.")
else:
    prod_admin = User(username=admin_username_prod, email=admin_email_prod)
    prod_admin.set_password(admin_password_prod) # Hashes the password
    db.session.add(prod_admin)
    db.session.commit()
    print(f"Production admin user '{admin_username_prod}' created successfully.")
exit()
Testing with Gunicorn
Before setting up systemd or Caddy, test if Gunicorn can serve your application.

(Ensure virtual environment is activated)

Bash

# Bind to a port, e.g., 8000, on localhost as Caddy will proxy to this.
# 'run:app' refers to the app instance in your run.py file.
gunicorn --workers 3 --bind localhost:8000 run:app
--workers 3: A common starting point is 2 * number_of_cpu_cores + 1. Adjust as needed.
--bind localhost:8000: Gunicorn listens on port 8000 on the server's loopback interface.
You won't be able to access this directly from the internet yet. Stop Gunicorn (Ctrl+C). If there are errors, check Gunicorn's output.

Setting up Gunicorn with systemd
To manage Gunicorn as a service (start on boot, restart on failure), create a systemd service file.

Create the service file (you'll need sudo privileges for this):

Bash

sudo nano /etc/systemd/system/yourprojectname.service
(Replace yourprojectname with a suitable name for your service, e.g., flaskportfolio)

Paste the following configuration, adjusting paths and user:

Ini, TOML

[Unit]
Description=Gunicorn instance for YourProjectName Flask App
After=network.target # Ensures network is up before starting

[Service]
User=appuser # The user you created to run the application
Group=appuser # Or www-data if preferred for web server integration
# Adjust WorkingDirectory to your project's root path
WorkingDirectory=/home/appuser/yourprojectname
# Path to Gunicorn within the virtual environment
ExecStart=/home/appuser/yourprojectname/venv/bin/gunicorn --workers 3 --bind localhost:8000 run:app
Restart=always # Restart the service if it fails

# Environment variables can be set here if not using a .env file or to override .env
# This is generally more secure for production secrets than a .env file in the repo.
# Environment="FLASK_CONFIG=production"
# Environment="SECRET_KEY=your_actual_production_secret_key_from_env_or_set_here"
# Environment="DATABASE_URL=postgresql://user:pass@host:port/db_from_env_or_set_here"
# Ensure the PATH includes the venv's bin directory if needed for any subprocesses
Environment="PATH=/home/appuser/yourprojectname/venv/bin"

[Install]
WantedBy=multi-user.target
Notes:

Replace appuser and /home/appuser/yourprojectname with your actual user and project path.
If you set environment variables directly in the [Service] block, they will be available to your Flask app. This is often preferred for sensitive data in production over relying solely on a .env file within the project directory.
Reload systemd, enable, and start your Gunicorn service:

Bash

sudo systemctl daemon-reload
sudo systemctl start yourprojectname.service
sudo systemctl enable yourprojectname.service # To start on boot
sudo systemctl status yourprojectname.service # Check its status
If there are issues, check the journal: sudo journalctl -u yourprojectname.service -f

Setting up Caddy as a Reverse Proxy (for HTTPS)
Caddy is a modern web server that can automatically handle HTTPS for your domain.

Install Caddy:
Follow the official Caddy installation instructions for Ubuntu: https://caddyserver.com/docs/install#debian-ubuntu-raspbian
The typical commands are:

Bash

sudo apt install -y debian-keyring debian-archive-keyring apt-transport-https
curl -1sLf '[https://dl.cloudsmith.io/public/caddy/stable/gpg.key](https://dl.cloudsmith.io/public/caddy/stable/gpg.key)' | sudo gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg
curl -1sLf '[https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt](https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt)' | sudo tee /etc/apt/sources.list.d/caddy-stable.list
sudo apt update
sudo apt install caddy
Configure Caddy (Caddyfile):
Edit Caddy's main configuration file:

Bash

sudo nano /etc/caddy/Caddyfile
Replace the entire content with the following, adjusting yourdomain.com and the Gunicorn port (localhost:8000):

Code snippet

# /etc/caddy/Caddyfile

yourdomain.com [www.yourdomain.com](https://www.yourdomain.com) {
    # Set this path to your site's directory for optimal logging.
    # root * /var/www/html # Default, can be changed or removed if not serving static files directly via Caddy

    # Reverse proxy requests to your Gunicorn instance
    # Gunicorn should be listening on localhost:8000 (or the port you chose in gunicorn.service)
    reverse_proxy localhost:8000

    # Optional: Configure logging for Caddy (Caddy logs to journal by default)
    log {
      output file /var/log/caddy/yourdomain.com.log {
          roll_size 10mb
          roll_keep 5
          roll_local_time
      }
    }

    # Optional: Enable Gzip/Brotli compression for better performance (Caddy often does this by default)
    encode gzip zstd

    # Optional: Define where Caddy can serve static files directly
    # This can offload static file serving from Flask/Gunicorn.
    # Ensure the path /home/appuser/yourprojectname/app/static is correct.
    # Adjust if your static files are served from a different URL path.
    handle_path /static/* {
        root * /home/appuser/yourprojectname/app
        file_server
    }
    # If you use the above handle_path for /static/*, ensure your Flask app's
    # UPLOAD_FOLDER for media_files is also correctly configured if Caddy should serve them.
    # Example for media_files (Trix uploads):
    # handle_path /static/media_files/* {
    #    root * /home/appuser/yourprojectname/app
    #    file_server
    # }
    # For simplicity, the initial setup proxies everything, letting Flask handle /static.
    # If you let Caddy handle static files, ensure permissions allow Caddy to read them.
}

# You can add other site configurations here, or manage them in separate files
# using Caddy's import directive.
Explanation:

yourdomain.com www.yourdomain.com: Replace with your domain(s). Caddy will automatically obtain SSL certificates.
reverse_proxy localhost:8000: Forwards requests to your Gunicorn service.
handle_path /static/*: (Optional) If you want Caddy to serve static files directly, this is more efficient. Adjust the root * path to point to the directory containing your static folder (i.e., your app directory).
Reload or Restart Caddy:

Bash

sudo systemctl reload caddy  # To apply changes if Caddy is already running
# or
# sudo systemctl restart caddy # To restart Caddy
sudo systemctl status caddy    # To check its status
Caddy will automatically attempt to get SSL certificates from Let's Encrypt. This requires your domain's DNS A/AAAA records to be correctly pointed to your server's public IP, and ports 80/443 must be open and accessible to Caddy.

Final Checks and Troubleshooting
Access Your Site: Open your browser and navigate to https://yourdomain.com. It should serve your Flask application over HTTPS.
Check Logs:
Caddy: sudo journalctl -u caddy -f or /var/log/caddy/yourdomain.com.log (if configured).
Gunicorn/Flask (systemd service): sudo journalctl -u yourprojectname.service -f.
PostgreSQL: Logs are typically in /var/log/postgresql/.
Firewall: Ensure your server's firewall (e.g., ufw) allows traffic on ports 80 (HTTP) and 443 (HTTPS).
Bash

sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
sudo ufw status
Permissions: Ensure appuser has read/write permissions to necessary directories (e.g., instance folder if still used for something, app/static/media_files for uploads, migrations folder if flask db commands are run by this user).
Key Configuration Points for Production
Database URL (DATABASE_URL)
Local (SQLite): sqlite:///../instance/app.db (relative to project root, stored in instance/)
Production (PostgreSQL): postgresql://your_app_db_user:your_very_strong_db_password@localhost:5432/your_app_db
Update this in your production .env file or systemd service file.
SECRET_KEY
Must be a long, random, and unique string for production.
Set in .env or systemd service file. Do not commit the production key to Git.
FLASK_CONFIG
Set to 'development' for local development (enables debug mode, etc.).
Set to 'production' for production (disables debug mode, may enable other production settings).
This is managed in app/config.py and selected via the environment variable.
Static and Media Files
UPLOAD_FOLDER: Defined in app/config.py, used by Trix for storing uploaded images (app/static/media_files/).
MEDIA_FILES_URL: URL path for accessing these files.
Ensure the UPLOAD_FOLDER path is correct for your production environment and that the appuser (or the user Gunicorn runs as) has write permissions to this directory.
Footer icons are stored in app/static/img/.
For production, consider configuring Caddy (or your reverse proxy) to serve static files directly for better performance.
Contributing
Contributions are welcome! Please follow these steps:   

Fork the repository.
Create a new branch (git checkout -b feature/your-feature-name).
Make your changes and commit them (git commit -m 'Add some feature').   
Push to the branch (git push origin feature/your-feature-name).
Open a Pull Request.
License
This project is licensed under the MIT License - see the LICENSE file for details (if applicable, create a LICENSE file).


**Key changes and considerations in this README:**

* **Detailed PostgreSQL Setup:** Clear steps for creating the database and user in PostgreSQL.
* **Gunicorn and systemd:** Comprehensive instructions for running Gunicorn as a systemd service for robust process management.
* **Caddy for HTTPS:** Modern approach for reverse proxy and automatic SSL.
* **Environment Variable Management:** Emphasizes secure handling of `SECRET_KEY` and `DATABASE_URL` for production, suggesting systemd for better security.
* **File Paths:** Highlights the importance of correct paths for `UPLOAD_FOLDER`, `WorkingDirectory`, etc., in different environments.
* **Dependencies:** Mentions adding `gunicorn` and `psycopg2-binary` to `requirements.txt`.
* **Project Structure:** Added for clarity.
* **Clarity and Order:** Reorganized sections for better flow from local setup to production deployment.
* **Placeholders:** Uses clear placeholders like `<your-repository-url>`, `yourdomain.com`, `appuser`, `yourprojectname`, etc., that need to be replaced by the user.
* **Security Notes:** Sprinkled throughout, especially regarding passwords and secret keys.

Remember to replace all placeholder values with your actual project details.
