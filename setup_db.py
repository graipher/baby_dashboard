#!/usr/bin/env python3
from project import db, create_app

db.create_all(app=create_app())
