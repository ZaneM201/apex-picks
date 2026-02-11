Apex Picks – F1 Pick’em Web App
Apex Picks is a web-based Formula 1 prediction game where users compete by predicting race results before each Grand Prix. Users can create accounts, submit picks for upcoming races, and track performance on a season-long leaderboard.
​

Features
User registration, login, and logout.
​
​

Make picks for normal and sprint race weekends (podium, pole, fastest lap, Driver of the Day, sprint podium).
​

Custom scoring system for race and sprint weekends, including DNF penalties.
​

Global season leaderboard with tiebreakers (correct wins, then correct poles).
​

Personal “My Picks” page with past and upcoming races and basic season stats.
​

Admin panel for managing races, results, and scoring data.
​
​

Technology Stack
Backend: Python, Django 6.0.
​
​

Database: SQLite (default Django development database).
​
​

Frontend: HTML, CSS, Bootstrap.
​
​

Media: Local file storage for images (track maps, logos, etc.).
​

Prerequisites
Make sure you have the following installed:

Python 3.10+

pip (Python package manager)

Git (optional but recommended)

On Windows, use py instead of python if that’s how your Python is configured.
​

Getting Started (Local Development)
1. Clone the Repository
bash
git clone https://github.com/ZaneM201/capstone.git
cd capstone
If your project folder name is different (e.g., apex-picks), update the commands accordingly.
​

2. Create and Activate a Virtual Environment
bash
# Create virtual environment
python -m venv venv

# Activate on macOS / Linux
source venv/bin/activate

# Activate on Windows (Command Prompt)
venv\Scripts\activate

# Activate on Windows (PowerShell)
venv\Scripts\Activate.ps1
You should see the environment name (for example, (venv)) in your terminal prompt once it is activated.
​

3. Install Dependencies
If you already have a requirements.txt file:

bash
pip install -r requirements.txt
If not, install Django (and any other packages you need) and then freeze them:

bash
pip install "django==6.*"
pip freeze > requirements.txt
This keeps your environment reproducible for other developers and deployment.
​

4. Configure Environment Variables (Optional)
If your project uses a .env file (for example, for SECRET_KEY, debug flags, or future database settings), create it now in the project root:

text
DEBUG=True
SECRET_KEY=your-dev-secret-key
ALLOWED_HOSTS=127.0.0.1,localhost
Make sure .env is added to .gitignore so you don’t commit secrets.
​

Database Setup
5. Apply Migrations
Run Django’s migrations to create the SQLite database and tables:
​

bash
python manage.py migrate
6. Create a Superuser (Admin)
To log into the Django admin panel and manage races, results, and scoring data:
​

bash
python manage.py createsuperuser
Follow the prompts to set a username, email, and password.

Running the App
7. Start the Development Server
bash
python manage.py runserver
By default, the app will be available at:

http://127.0.0.1:8000/

You can log into the admin panel at:

http://127.0.0.1:8000/admin/
​

8. Populate Initial Data
To use Apex Picks as intended, you’ll need to create some initial data through the admin:

Teams (name, base, principal, logo).

Drivers (number, first name, last name, team, stats fields as desired).

Schedule entries (race name, date, sprint flag, track map).

Optional: initial RaceResult entries for testing the scoring logic.
​
​

Once races exist, users can create accounts, navigate to “Make Picks,” and start submitting predictions.
​

Project Structure (High-Level)
Your exact structure may vary, but a typical layout looks like:
​

text
capstone/               # Repo root
├─ manage.py
├─ requirements.txt
├─ apex_picks/          # Django project folder (settings, urls, wsgi/asgi)
│  ├─ settings.py
│  ├─ urls.py
│  └─ ...
├─ picks/               # Example app (picks, results, leaderboard logic)
│  ├─ models.py         # UserSeasonStats, RacePick, RaceResult, etc.
│  ├─ views.py          # My Picks, Make Picks, Leaderboard, etc.
│  ├─ urls.py
│  ├─ templates/
│  └─ ...
└─ static/              # CSS, images, etc. (if configured)
Adjust app names to match your project (for example, picks, core, accounts).
​

Running Tests (If Configured)
If you’ve added Django tests, run them with:
​

bash
python manage.py test
Common Issues
Migrations errors: Try deleting the SQLite database file and migration files (in each app’s migrations folder except __init__.py), then run makemigrations and migrate again.
​

Static files not loading: Ensure STATIC_URL, STATICFILES_DIRS (if used), and template tags {% load static %} are configured correctly.
​

Media files not loading in development: Check MEDIA_URL and MEDIA_ROOT and that urlpatterns includes the proper static() helper for media in settings.DEBUG mode.
​