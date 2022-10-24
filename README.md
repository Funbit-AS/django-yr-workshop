# django-yr-workshop
An introduction to Django workshop using Yr's open API.

## Instructions

### Setup

1. Fork this repo
2. Navigate into the weather folder
```bash
cd weather
```
3. Create a virtual env and activate it
```bash
# Create virtualenv (All platforms)
python -m venv env
# Activate: Macos / Linux
source env/bin/activate
# Activate: Windows cmd.exe
source env/Scripts/activate.bat
# Activate: Windows Powershell
source env/Scripts/Activate.ps1
```
4. Install requirements
```bash
pip install -r requirements.txt
```

### Prepare database

```
# From inside your virtualenv
python manage.py migrate
```

### Run the built-in development server

```
# From inside your virtualenv
python manage.py runserver
```