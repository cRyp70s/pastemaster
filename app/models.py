from datetime import datetime

from .utils import hashify
from . import db


class Paste(db.Model):
    __tablename__ = "pastes"
    __searchable__ = ["title"]
    id = db.Column(db.Integer, primary_key=True)
    views = db.Column(db.Integer, default=0)
    title = db.Column(db.String(100))
    edit_key = db.Column(db.String(100), default=hashify)
    content = db.Column(db.LargeBinary)
    created = db.Column(db.DateTime, default=datetime.utcnow)
    last_edit = db.Column(db.DateTime, default=datetime.utcnow)
    public = db.Column(db.Boolean, default=False)


class View(db.Model):
    __tablename__ = "views"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(256), index=True)
    last_view = db.Column(db.DateTime, default=datetime.utcnow)
    paste_id = db.Column(db.String(256), index=True, unique=True)
