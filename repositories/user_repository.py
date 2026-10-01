from sqlalchemy.orm import Session

from models.user_model import User


class UserRepository:

    @staticmethod
    def get_by_id(
        db: Session,
        user_id: int
    ) -> User | None:

        return db.query(User).filter(
            User.id == user_id
        ).first()

    @staticmethod
    def get_by_email(
        db: Session,
        email: str
    ) -> User | None:

        return db.query(User).filter(
            User.email == email.lower()
        ).first()

    @staticmethod
    def create(
        db: Session,
        user: User
    ) -> User:

        db.add(user)
        db.commit()
        db.refresh(user)

        return user

    @staticmethod
    def update(
        db: Session,
        user: User
    ) -> User:

        db.commit()
        db.refresh(user)

        return user

    @staticmethod
    def delete(
        db: Session,
        user: User
    ) -> None:

        db.delete(user)
        db.commit()