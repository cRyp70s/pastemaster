import os

from app import app, db
from app.models import Paste, View
from app.views import *

app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY") or "XedneworheofSFDfvbdierhu4e43434()#@@("
db.create_all()

if __name__ == "__main__":
    app.run(debug=True)
