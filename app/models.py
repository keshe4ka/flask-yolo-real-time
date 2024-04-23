from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from sqlalchemy import inspect
from sqlalchemy.orm import DeclarativeBase


class BaseMixin(DeclarativeBase):
    __abstract__ = True

    def update(self, **kwargs) -> None:
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)

    def to_dict(self):
        return {c.key: getattr(self, c.key) for c in
                inspect(self).mapper.column_attrs}


class User(BaseMixin):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str]
    password_hash: Mapped[str]
