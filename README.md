Local DEV setup with admin user creation, and a detailed guide for production deployment on Ubuntu 22.04 using PostgreSQL and Caddy for automatic HTTPS.

````markdown
# Flask Portfolio & Blog

This project is a dynamic portfolio and blog application built with Flask, SQLAlchemy for database interaction, and Flask-Migrate for database migrations. It features an administrative backend for managing posts (categorized as blog, portfolio, or home page content), footer icons, and site configuration like copyright messages. The frontend displays these posts in respective sections with pagination and uses a Trix editor for rich text content creation.

## Part 1: Local Development Setup

This section guides you through setting up the project for local development on your machine using an IDE like VS Code or PyCharm.

### Prerequisites

* Python 3.8+
* pip (Python package installer)
* Git
* Your preferred IDE (e.g., VS Code, PyCharm)

### 1. Clone the Repository

Open your terminal or command prompt and clone the repository:

```bash
git clone <your-repository-url> flask-portfolio-blog
cd flask-portfolio-blog
````

### 2. Create and Activate a Virtual Environment

It's highly recommended to use a virtual environment to manage project dependencies.

```bash
# For Linux/macOS
python3 -m venv venv
source venv/bin/activate

# For Windows
python -m venv venv
.\venv\Scripts\activate
```

### 3. Install Dependencies

Install the required Python packages:

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables (.env file)

Create a .env file in the root directory of the project. This file will store your environment-specific configurations. This .env file should be listed in your .gitignore file to prevent committing sensitive information.

Copy the example or create a new one:

```
# .env

# Generate a strong, random string for production. For development, a simpler one is okay.
# Example for generation: python -c 'import secrets; print(secrets.token_hex(32))'
SECRET_KEY='your_development_secret_key'

# For local development, we'll use SQLite.
# The path should resolve to project_root/instance/app.db as configured in config.py
DATABASE_URL='sqlite:///../instance/app.db'

# Set to 'development' for local development features (like debug mode)
FLASK_CONFIG='development'
# FLASK_DEBUG=1 (Alternatively, if FLASK_CONFIG=development isn't enough for your debugger)
```

The application is configured (in app/config.py) to create an instance folder in the project root if it doesn't exist, where the SQLite database app.db will be stored.

### 5. Initialize the Database

Run the following Flask-Migrate commands to initialize your database schema. If you are using SQLite as per the .env example above, this will create the instance/app.db file.

```bash
# If this is the very first time and the 'migrations' folder doesn't exist or is empty:
flask db init

# Create an initial migration (or if you've made model changes)
flask db migrate -m "Initial database schema"

# Apply the migration to the database
flask db upgrade
```

### 6. Create the Initial Admin User

You need an admin user to log into the /admin section. Use the Flask shell to create one:

```bash
flask shell
```

Once in the Flask shell (you'll see >>>), type the following Python commands:

```python
from app.models import User
from app.extensions import db  # db should be available from the shell context processor in run.py
from werkzeug.security import generate_password_hash # If User model doesn't auto-hash on set_password

# Replace with your desired admin credentials I use this with a single admin password as there are no other users.
admin_username = 'admin'
admin_email = 'admin@example.com'
admin_password = 'a_very_secure_password' # Change this!

exit()
```

Note: Ensure your User model in app/models.py has a set_password(self, password) method that properly hashes the password (which it does in this project using generate_password_hash).

### 7. Run the Development Server

Start the Flask development server:

```bash
flask run
```

By default, it should be accessible at http://127.0.0.1:5000 or http://localhost:5000.

### 8. Access the Application

* Main Site: Open http://127.0.0.1:5000 in your web browser.
* Admin Section: Navigate to http://127.0.0.1:5000/admin/login and log in with the admin credentials you created.

You can now manage posts, footer icons, and other settings through the admin dashboard.

---

## Part 2: Production Deployment (Ubuntu 22.04, PostgreSQL, Caddy)

This section provides a step-by-step tutorial to deploy the application to a production Ubuntu 22.04 server using PostgreSQL as the database and Caddy as the web server (which will handle automatic HTTPS).

### Assumptions

Before you begin, ensure you have the following:

1. An Ubuntu 22.04 server provisioned (e.g., from a cloud provider like DigitalOcean, AWS, Linode, etc.).
2. Root or sudo access to the server.
3. PostgreSQL server installed and running on your Ubuntu server.
4. Git installed on the server (sudo apt install git).
5. Python 3.10+ (or the version used in development) installed on the server.
6. python3-venv package installed (sudo apt install python3-venv).
7. A domain name (e.g., A-record - yourdomain.com) pointed to your server's public IP address via DNS A records. This is necessary for Caddy to obtain SSL certificates automatically.
8. Your project code is hosted in a Git repository (e.g., GitHub, GitLab).

### Step-by-Step Deployment 

#### 1. Server Preparation

Log into your server via SSH.

```bash
ssh your_username@your_server_ip
```

First, update your server's package list and upgrade existing packages:

```bash
sudo apt update && sudo apt upgrade -y
```

Install necessary build tools and the PostgreSQL client development headers (required for psycopg2):

```bash
sudo apt install -y python3-venv build-essential libpq-dev
```

Create a dedicated non-root user to run your application (replace appuser with your desired username):

```bash
sudo adduser appuser
sudo usermod -aG sudo appuser # Optionally grant sudo rights if needed for this user
# Switch to the new user
su - appuser
```

It's generally better if appuser does not have sudo rights for running the application itself. Perform sudo operations as your main admin user.

#### 2. PostgreSQL Database Setup

Connect to PostgreSQL (you might need to switch to the postgres user first if you haven't set up other admin users: sudo -u postgres psql).

Create a database for your application:

```sql
CREATE DATABASE your_app_db;
```

Create a dedicated PostgreSQL user for your application with a strong password:

```sql
CREATE USER your_app_db_user WITH PASSWORD 'your_very_strong_db_password';
```

Grant necessary privileges to this user on the new database:

```sql
ALTER ROLE your_app_db_user SET client_encoding TO 'utf8';
ALTER ROLE your_app_db_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE your_app_db_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE your_app_db TO your_app_db_user;
```

Exit psql (\\q).

Your PostgreSQL DATABASE_URL will be in the format:
postgresql://your_app_db_user:your_very_strong_db_password@localhost:5432/your_app_db

#### 3. Download Code from Git

As appuser (or your deployment user), navigate to your home directory (or preferred location like /var/www/) and clone your project:

```bash
cd ~ # or cd /var/www/
git clone <your-repository-url> yourprojectname
cd yourprojectname
```

#### 4. Setup Python Virtual Environment

Create and activate a virtual environment within your project directory:

```bash
python3 -m venv venv
source venv/bin/activate
```

#### 5. Install Dependencies

Install Python packages, including gunicorn for serving the app and psycopg2-binary for PostgreSQL connectivity:

```bash
pip install -r requirements.txt
pip install gunicorn psycopg2-binary # Add psycopg2-binary if not in requirements.txt
```

(Ensure gunicorn and psycopg2-binary are added to your requirements.txt for future deployments).

#### 6. Configure Environment Variables for Production

You need to set environment variables for your production application. You can place these in a .env file within your project directory (ensure it's in .gitignore) for python-dotenv to pick up, or more securely, manage them via the systemd service file (shown later).

Create or edit .env:

```
# yourprojectname/.env
FLASK_CONFIG=production
SECRET_KEY='your_new_strong_production_secret_key' # Generate a new unique one
DATABASE_URL='postgresql://your_app_db_user:your_very_strong_db_password@localhost:5432/your_app_db'
# Any other production-specific environment variables
```

Important: The SECRET_KEY must be a new, strong, random string, different from your development key.

#### 7. Database Migrations (Production)

Apply your database migrations to the production PostgreSQL database:

```bash
flask db upgrade
```

This will create the tables based on your app/models.py.

#### 8. Create Initial Admin User (Production)

Use the Flask shell to create your admin user in the production database:

```bash
flask shell
```

Then, in the Python shell:

```python
from app.models import User
from app.extensions import db

admin_username_prod = 'admin_prod' # Or your desired production admin username
admin_email_prod = 'admin_prod@yourdomain.com'
admin_password_prod = 'a_very_strong_and_unique_production_password' # CHANGE THIS!

existing_user = User.query.filter_by(username=admin_username_prod).first()
if existing_user:
    print(f"User {admin_username_prod} already exists.")
else:
    prod_admin = User(username=admin_username_prod, email=admin_email_prod)
    prod_admin.set_password(admin_password_prod)
    db.session.add(prod_admin)
    db.session.commit()
    print(f"Production admin user '{admin_username_prod}' created successfully.")

exit()
```

Use an extremely strong and unique password for the production admin user.

#### 9. Test Application with Gunicorn (HTTP)

Before setting up Caddy, test if Gunicorn can serve your application. From your project directory, with the virtual environment activated:

```bash
gunicorn --workers 3 --bind 0.0.0.0:8000 run:app
```

(The run:app refers to the app instance created by create_app() in your run.py file).

Open a web browser and try to access your application at http://<your_server_ip>:8000. If it works, stop Gunicorn (Ctrl+C). If not, check Gunicorn's output for errors.

#### 10. Install and Configure Caddy Web Server

Caddy will act as a reverse proxy and automatically handle HTTPS.

Install Caddy (check Caddy's official documentation for the most up-to-date instructions for Ubuntu):

```bash
# These commands are typical but verify with official Caddy docs
sudo apt install -y debian-keyring debian-archive-keyring apt-transport-https
curl -1sLf '[https://dl.cloudsmith.io/public/caddy/stable/gpg.key](https://dl.cloudsmith.io/public/caddy/stable/gpg.key)' | sudo gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg
curl -1sLf '[https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt](https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt)' | sudo tee /etc/apt/sources.list.d/caddy-stable.list
sudo apt update
sudo apt install caddy
```

Configure Caddy:
Caddy's main configuration file is /etc/caddy/Caddyfile. Edit it with sudo nano /etc/caddy/Caddyfile (or your preferred editor).

Replace the entire content of the Caddyfile with the following, adjusting yourdomain.com and the proxy port if Gunicorn uses something other than 8000:

```caddyfile
# /etc/caddy/Caddyfile

yourdomain.com [www.yourdomain.com](https://www.yourdomain.com) {
    # Reverse proxy requests to your Gunicorn instance
    # Gunicorn should be listening on localhost:8000 (or the port you chose)
    reverse_proxy localhost:8000

    # Optional: Configure logging for Caddy (Caddy logs to journal by default)
    # log {
    #   output file /var/log/caddy/yourdomain.com.log {
    #       roll_size 10mb
    #       roll_keep 5
    #   }
    # }

    # Optional: Enable Gzip compression for better performance
    # encode gzip

    # Optional: Define where Caddy can serve static files directly
    # This can offload static file serving from Flask/Gunicorn
    # Ensure the path /path/to/yourproject/app/static is correct
    # handle_path /static/* {
    #    root * /path/to/yourproject/app # Note: Caddy's root is different from Nginx's alias
    #    file_server
    # }
    # If you use the above handle_path, ensure Gunicorn is not also trying to serve static
    # For simplicity, the initial setup proxies everything, letting Flask handle /static.
}
```

Explanation of Caddyfile:

* yourdomain.com www.yourdomain.com: Replace these with your actual domain and any subdomains you want to serve.
* reverse_proxy localhost:8000: Tells Caddy to forward incoming web requests to Gunicorn, which should be listening on localhost:8000.
* Automatic HTTPS: Caddy will automatically detect your domain(s) in the Caddyfile, obtain SSL/TLS certificates from Let's Encrypt (or ZeroSSL), and renew them. This requires your domain's DNS A/AAAA records to point to this server's public IP, and ports 80/443 must be accessible to Caddy.

Start/Reload Caddy:
After saving the Caddyfile:

```bash
sudo systemctl reload caddy  # To apply changes if Caddy is already running
# or
sudo systemctl restart caddy # To restart Caddy
sudo systemctl status caddy  # To check its status
```

At this point, if Gunicorn were running on localhost:8000 and your DNS is set up, Caddy would serve your site over HTTPS.

#### 11. Configure Gunicorn with systemd

To ensure Gunicorn runs robustly (starts on boot, restarts on failure), create a systemd service file.

Create /etc/systemd/system/yourprojectname.service (replace yourprojectname):

```bash
sudo nano /etc/systemd/system/yourprojectname.service
```

Paste the following, adjusting paths, user, group, and Gunicorn command as needed:

```ini
[Unit]
Description=Gunicorn instance for YourProjectName
After=network.target

[Service]
User=appuser # The user you created to run the application
Group=appuser # Or a group like www-data if preferred for permissions
WorkingDirectory=/home/appuser/yourprojectname # Or /var/www/yourprojectname
# Path to virtual environment's Gunicorn and Python
Environment="PATH=/home/appuser/yourprojectname/venv/bin"
# Environment variables for Flask (can also be loaded from .env by python-dotenv)
# For production, explicitly setting here is often more secure than relying on a .env file in the repo.
# Environment="FLASK_CONFIG=production"
# Environment="SECRET_KEY=your_actual_production_secret_key"
# Environment="DATABASE_URL=postgresql://your_app_db_user:your_very_strong_db_password@localhost:5432/your_app_db"

# Command to start Gunicorn.
# Bind to localhost:8000 as Caddy will proxy to this.
ExecStart=/home/appuser/yourprojectname/venv/bin/gunicorn --workers 3 --bind localhost:8000 run:app

Restart=always

[Install]
WantedBy=multi-user.target
```

Notes for systemd service:

* Replace yourprojectname and appuser with your actual project name and user.
* Adjust WorkingDirectory and PATH to your project and virtual environment.
* If you set environment variables directly in the \[Service\] block (like SECRET_KEY, DATABASE_URL), you don't strictly need the .env file to be read by the application for these specific variables when run via systemd. This is generally more secure. If you rely on .env being read by python-dotenv in app/config.py, ensure WorkingDirectory is correct.

Enable and Start the Gunicorn Service:

```bash
sudo systemctl daemon-reload
sudo systemctl start yourprojectname
sudo systemctl enable yourprojectname # To start on boot
sudo systemctl status yourprojectname # Check its status
```

#### 12. Final Checks and Troubleshooting

* Access Your Site: Open your browser and navigate to https://yourdomain.com. It should now be serving your Flask application over HTTPS, managed by Caddy.
* Check Logs: 
  * Caddy logs: sudo journalctl -u caddy -f
  * Your Gunicorn/Flask application service logs: sudo journalctl -u yourprojectname -f
  * Application-specific logs (if configured, e.g., in yourprojectname/logs/).
* Troubleshooting Caddy HTTPS: If Caddy fails to get a certificate, ensure: 
  * Your domain's DNS A/AAAA records are correctly pointing to your server's public IP.
  * Ports 80 and 443 are open in your server's firewall and not blocked by your cloud provider's firewall.
  * Caddy has permissions to write to its data directory (usually /var/lib/caddy).

Congratulations! Your Flask application should now be deployed to production with PostgreSQL and automatic HTTPS via Caddy. Remember that ongoing maintenance, security updates, and monitoring are crucial for a healthy production application.