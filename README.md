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

Start the server

```
flask run
```

Visit the webpage

```
firefox http://localhost:5000
```
