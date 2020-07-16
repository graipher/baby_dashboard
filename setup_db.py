#!/usr/bin/env python3
from pathlib import Path
try:
    # Docker
    from app import db, create_app
except ImportError:
    # Local
    from project import db, create_app


root = Path("project")

if not (root / "db/db.sqlite").exists():
    print("Create DB")
    db.create_all(app=create_app())
