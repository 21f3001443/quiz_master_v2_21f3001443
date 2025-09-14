from modules import db
from modules import (
    User,
    Role
)

from datetime import datetime

def setRole(role_id):
    try:
        role_exists = Role.query.filter_by(role_id=role_id).first()
        if role_exists:
            print("Role already exists.")
            return None
        s = Role(role_id=role_id)
        db.session.add(s)
        db.session.commit()
        return s.role_id
    except Exception as e:
        db.session.rollback()
        print(f"Error: {e}")
        raise


def setUsers(user_id, role_id):
    try:
        user_exists = User.query.filter_by(user_id=user_id, user_fname=user_id, user_lname=user_id).first()
        if user_exists:
            print("User already exists.")
            return None
        print(datetime.today().date())
        s = User(
            user_id=user_id,
            password=user_id,
            user_fname=user_id,
            user_lname=user_id,
            role_id=role_id,
            user_qualification="NA",
            user_dob=datetime.today().date(),
        )
        db.session.add(s)
        db.session.commit()
        return s.user_id
    except Exception as e:
        db.session.rollback()
        print(f"Error: {e}")
        raise


def SetupDB():

    # Drop all tables (cleanup)
    db.drop_all()
    print("All tables dropped.")

    db.create_all()  # Create tables if they don't already exist
    print("All tables created.")

    admin = setRole("admin")
    user = setRole("user")
    userID = setUsers("admin", admin)
    print("Admin login ID: ", "admin")
    print("Admin Password: ", "admin")
    print("Admin Role: ", admin)
    print("User Role: ", user)
    print("Setup completed.")