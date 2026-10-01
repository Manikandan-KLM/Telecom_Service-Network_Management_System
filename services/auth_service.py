from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from config import settings
from models.password_reset_model import PasswordResetToken
from models.token_model import RevokedToken
from models.user_model import User

from repositories.user_repository import UserRepository
from repositories.token_repository import TokenRepository
from repositories.password_reset_repository import (
    PasswordResetRepository
)

from utils.security import (
    create_token,
    generate_reset_token,
    hash_password,
    hash_reset_token,
    verify_password,
)


class AuthService:

    @staticmethod
    def register(
        db: Session,
        full_name: str,
        email: str,
        password: str
    ):

        existing_user = UserRepository.get_by_email(
            db,
            email
        )

        if existing_user:

            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered"
            )

        user = User(
            full_name=full_name,
            email=email.lower(),
            hashed_password=hash_password(password),
            role="Customer",
            is_active=True
        )

        return UserRepository.create(
            db,
            user
        )

    @staticmethod
    def authenticate(
        db: Session,
        email: str,
        password: str
    ):

        user = UserRepository.get_by_email(
            db,
            email
        )

        if not user:

            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )

        if not verify_password(
            password,
            user.hashed_password
        ):

            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )

        if not user.is_active:

            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is deactivated"
            )

        return user

    @staticmethod
    def create_tokens(user: User):

        access_token, _ = create_token(
            subject=str(user.id),
            token_type="access",
            expires_delta=timedelta(
                minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
            )
        )

        refresh_token, _ = create_token(
            subject=str(user.id),
            token_type="refresh",
            expires_delta=timedelta(
                days=settings.REFRESH_TOKEN_EXPIRE_DAYS
            )
        )

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }

    @staticmethod
    def revoke_token(
        db: Session,
        token: str
    ):

        from utils.security import decode_token

        try:
            payload = decode_token(token)

        except ValueError:

            raise HTTPException(
                status_code=401,
                detail="Invalid token"
            )

        jti = payload.get("jti")
        exp = payload.get("exp")

        if not jti or not exp:

            raise HTTPException(
                status_code=401,
                detail="Invalid token"
            )

        existing = TokenRepository.get_by_jti(
            db,
            jti
        )

        if existing:
            return

        revoked_token = RevokedToken(
            jti=jti,
            expires_at=datetime.fromtimestamp(
                exp,
                tz=timezone.utc
            )
        )

        TokenRepository.revoke(
            db,
            revoked_token
        )

    @staticmethod
    def create_password_reset(
        db: Session,
        email: str
    ):

        user = UserRepository.get_by_email(
            db,
            email
        )

        if not user:
            return None

        raw_token = generate_reset_token()

        token_hash = hash_reset_token(
            raw_token
        )

        expires_at = (
            datetime.now(timezone.utc)
            + timedelta(
                minutes=settings.PASSWORD_RESET_EXPIRE_MINUTES
            )
        )

        reset_token = PasswordResetToken(
            user_id=user.id,
            token_hash=token_hash,
            expires_at=expires_at,
            used=False
        )

        PasswordResetRepository.create(
            db,
            reset_token
        )

        return raw_token

    @staticmethod
    def reset_password(
        db: Session,
        token: str,
        new_password: str
    ):

        token_hash = hash_reset_token(
            token
        )

        reset_record = (
            PasswordResetRepository.get_valid_token(
                db,
                token_hash
            )
        )

        if not reset_record:

            raise HTTPException(
                status_code=400,
                detail="Invalid reset token"
            )

        if reset_record.expires_at < datetime.now(
            timezone.utc
        ):

            raise HTTPException(
                status_code=400,
                detail="Reset token expired"
            )

        user = UserRepository.get_by_id(
            db,
            reset_record.user_id
        )

        if not user:

            raise HTTPException(
                status_code=404,
                detail="User not found"
            )

        user.hashed_password = hash_password(
            new_password
        )

        reset_record.used = True

        UserRepository.update(
            db,
            user
        )

        PasswordResetRepository.update(
            db,
            reset_record
        )

        return user