from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import sessionmaker

# Initialize the database
db = SQLAlchemy()

def create_session():
    Session = sessionmaker(bind=db.engine)
    return Session()
