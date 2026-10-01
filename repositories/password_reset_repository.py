from sqlalchemy.orm import Session

from models.password_reset_model import (
    PasswordResetToken
)


class PasswordResetRepository:

    @staticmethod
    def get_valid_token(
        db: Session,
        token_hash: str
    ) -> PasswordResetToken | None:

        return db.query(
            PasswordResetToken
        ).filter(
            PasswordResetToken.token_hash == token_hash,
            PasswordResetToken.used == False
        ).first()

    @staticmethod
    def create(
        db: Session,
        reset_token: PasswordResetToken
    ) -> PasswordResetToken:

        db.add(reset_token)
        db.commit()
        db.refresh(reset_token)

        return reset_token

    @staticmethod
    def update(
        db: Session,
        reset_token: PasswordResetToken
    ) -> PasswordResetToken:

        db.commit()
        db.refresh(reset_token)

        return reset_token