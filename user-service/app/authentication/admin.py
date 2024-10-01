from app.authentication.auth import hash_password
from app.models.user_model import User, Role
from sqlmodel import Session,select
from app.user_db import engine
import os

def create_initial_admin():
    with Session(engine) as session:
        existing_admin = session.exec(select(User).where(User.role == Role.ADMIN)).first()
        if not existing_admin:
            admin_username = os.getenv("ADMIN_USERNAME", "admin")
            admin_email = os.getenv("ADMIN_EMAIL", "admin@example.com")
            admin_password = os.getenv("ADMIN_PASSWORD", "adminpassword")
            
            admin_user = User(
                username=admin_username,
                email=admin_email,
                password=hash_password(admin_password),
                role=Role.ADMIN
            )
            session.add(admin_user)
            session.commit()