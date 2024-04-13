# models.py
from sqlalchemy import Column, Integer, String, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from typing import Dict

Base = declarative_base()


class Account(Base):
    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    account_id = Column(String, unique=True, index=True)
    account_name = Column(String)
    app_secret_token = Column(String)
    website = Column(String, nullable=True)

    destinations = relationship(
        "Destination", back_populates="account", cascade="all, delete-orphan"
    )


class Destination(Base):
    __tablename__ = "destinations"

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String)
    http_method = Column(String)
    headers = Column(JSON)
    account_id = Column(Integer, ForeignKey("accounts.id"))

    account = relationship("Account", back_populates="destinations")
