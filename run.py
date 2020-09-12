#!venv/bin/python
from app import os
from app import app, build_sample_db

if __name__ == '__main__':

    # Build a sample db on the fly, if one does not exist yet.
    app_dir = os.path.realpath(os.path.dirname(__file__))

    database_path = os.path.join(app_dir, "app", app.config['DATABASE_FILE'])
    if not os.path.exists(database_path):
        build_sample_db()
    
    # Start app
    app.run(host="0.0.0.0", debug=True)