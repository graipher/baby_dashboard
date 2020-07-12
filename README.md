## Baby Dashboard

A simple dashboard for data related to your baby's growth.

Uses flask and SQLAlchemy for the webapp and bokeh for data visualization.

Note that this currenlty uses HTTP, so e.g. your password are transmitted in clear text. **Do not use this app as is on the web**. If it is running behind a NAT on your home network it should be fine.

## Setup

Clone the repository to a local folder

```
git clone URL
```

Create a virtual environment

```
python3 -m venv venv
source venv/bin/activate
```

Install required files

```
pip install -r requirements.txt
```

Initialize the database

```
./setup_db.py
```

Start the local development server

```
flask run
```

Visit the webpage

```
http://localhost:5000
```

## Future

Use a dockerized nginx instance instead of the built-in webserver.
