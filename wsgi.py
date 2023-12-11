# Citation for Flask Starter file:
# Date: 11/16/2023
# Adapted from Starter App Guide
# Use: Starter for Layout and Routing Function Headers, wsgi.py to run gunicorn.
# Source URL: https://github.com/osu-cs340-ecampus/flask-starter-app

# File to run gunicorn.

from app import app

if __name__ == "__main__":
    app.run()