from sqlalchemy.orm import Session

from models.token_model import RevokedToken


class TokenRepository:

    @staticmethod
    def get_by_jti(
        db: Session,
        jti: str
    ) -> RevokedToken | None:

        return db.query(RevokedToken).filter(
            RevokedToken.jti == jti
        ).first()

    @staticmethod
    def revoke(
        db: Session,
        revoked_token: RevokedToken
    ) -> RevokedToken:

        db.add(revoked_token)
        db.commit()
        db.refresh(revoked_token)

        return revoked_token