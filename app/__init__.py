from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect, generate_csrf
from flask_msearch import Search

app = Flask(__name__)
db = SQLAlchemy(app)
search = Search(app)
csrf = CSRFProtect(app)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///test.db"
app.config["ENCRYPT_IV"] = b"rtuewq237mlkds1\xff"


@app.after_request
def csrf_token_set(response):
    """
    Set CSRF token.
    """
    response.set_cookie("CSRF-TOKEN", generate_csrf())
    return response
