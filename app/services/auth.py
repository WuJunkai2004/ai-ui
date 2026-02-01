import datetime
import hashlib
import secrets
from typing import Optional

from app.core.database import User, db


class AuthService:
    def hash_password(self, password: str) -> str:
        return hashlib.sha256(password.encode()).hexdigest()

    def login_or_register(self, username, password) -> str:
        pwd_hash = self.hash_password(password)

        with db.atomic():
            user = User.get_or_none(User.username == username)

            if user:
                # Login
                if user.password_hash != pwd_hash:
                    return ""  # Invalid password
            else:
                # Register
                user = User.create(username=username, password_hash=pwd_hash)

            # Generate Token
            token = secrets.token_hex(32)
            expires = datetime.datetime.now() + datetime.timedelta(days=7)

            user.token = token
            user.token_expires = expires
            user.save()

            return token

    def verify_token(self, token: str) -> Optional[User]:
        if not token:
            return None

        try:
            user = User.get(User.token == token)
            if user.token_expires < datetime.datetime.now():
                return None  # Expired
            return user
        except User.DoesNotExist:
            return None


auth_service = AuthService()
