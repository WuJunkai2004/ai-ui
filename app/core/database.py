import datetime
import os

from peewee import (
    CharField,
    DateTimeField,
    ForeignKeyField,
    Model,
    SqliteDatabase,
    TextField,
)

from app.core.logging import logger

# Ensure the app directory exists for the db file if we put it there,
# put at ./tempData/genui.db for now
if not os.path.exists("./tempData/"):
    os.makedirs("./tempData/")
db = SqliteDatabase("./tempData/genui.db")


class BaseModel(Model):
    class Meta:
        database = db


class User(BaseModel):
    username = CharField(unique=True)
    password_hash = CharField()
    token = CharField(null=True, index=True)
    token_expires = DateTimeField(null=True)


class Chat(BaseModel):
    user = ForeignKeyField(User, backref="chats")
    title = CharField(default="New Chat")
    created_at = DateTimeField(default=datetime.datetime.now)


class Message(BaseModel):
    chat = ForeignKeyField(Chat, backref="messages")
    role = CharField()  # 'user' or 'assistant'
    content = TextField()  # JSON string or plain text
    created_at = DateTimeField(default=datetime.datetime.now)


def init_db():
    logger.info("Initializing database and creating tables if not exist...")
    db.connect()
    tables = BaseModel.__subclasses__()
    db.create_tables(tables, safe=True)
    db.close()
