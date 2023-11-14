from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import sessionmaker

# This file is for initializing the database and
# creating new database sessions

# Initialize the database
db = SQLAlchemy()

# function to create new database sessions
def create_session():
    Session = sessionmaker(bind=db.engine)
    return Session()
