from datetime import datetime, timedelta

from flask import (
    render_template,
    request,
    abort,
    jsonify,
    redirect,
    url_for,
    current_app,
    make_response,
)

# from marshmallow import Schema, fields

from .models import Paste, View
from . import app, db
from .utils import encrypt, decrypt, hashify


@app.route("/")
def index():
    print(request.headers)
    return render_template("index.html", home=True)


@app.route("/paste/<int:id>/<token>")
def paste(id, token):
    print(request.headers)
    paste = Paste.query.filter_by(id=id).first_or_404()
    cookie_set = False
    viewed = False
    cookie = request.cookies.get("user_id")
    if cookie:
        view = View.query.filter_by(user_id=cookie, paste_id=paste.id).first()
        if not view:
            view = View(user_id=cookie, paste_id=paste.id)
        else:
            print(datetime.utcnow().timestamp() - view.last_view.timestamp())
            if (
                datetime.utcnow().timestamp() - view.last_view.timestamp()
            ) // 86400 <= 1:
                print("Viewww")
                viewed = True
            else:
                view.last_view = datetime.utcnow()
    else:
        cookie_set = hashify(10)
        view = View(
            user_id=cookie_set,
            paste_id=paste.id,
        )
    db.session.add(view)
    top_pastes = (
        Paste.query.filter_by(public=True).order_by(Paste.views.desc()).limit(4).all()
    )
    content = paste.content
    header = request.headers
    to_hash = header.get("Host") + header.get("User-Agent")
    if not paste.public:
        iv = current_app.config["ENCRYPT_IV"]
        key = token
        # print(key.encode(), iv)
        # print(content, "\n\nn")
        content = decrypt(key.encode(), iv, content)
        print(content)
        for i in content:

            if not chr(i).isprintable() and chr(i) != "\0" and not "\r".isspace():
                print(chr(i), "not")
                abort(404)
            print(chr(i), "is")
        if not viewed:
            paste.views += 1
        db.session.add(paste)
        db.session.commit()
        temp = render_template(
            "read.html",
            paste=paste,
            content=content.decode(),
            readonly=True,
            top_pastes=top_pastes,
        )
        if cookie_set:
            resp = make_response(temp)
            resp.set_cookie(
                "user_id", cookie_set, expires=datetime.utcnow() + timedelta(weeks=100)
            )
            return resp
        return temp
    if not viewed:
        paste.views += 1
    db.session.add(paste)
    db.session.commit()
    temp = render_template(
        "read.html",
        paste=paste,
        content=content.decode(),
        readonly=True,
        top_pastes=top_pastes,
    )
    if cookie_set:
        resp = make_response(temp)
        resp.set_cookie(
            "user_id", cookie_set, expires=datetime.utcnow() + timedelta(weeks=100)
        )
        return resp
    return temp


@app.route("/paste/<int:id>/<token>/<edit_token>", methods=["GET", "POST"])
def editpaste(id, token, edit_token):
    top_pastes = (
        Paste.query.filter_by(public=True).order_by(Paste.views.desc()).limit(4).all()
    )
    if request.method == "POST":
        paste = Paste.query.filter_by(edit_key=edit_token).first_or_404()
        ctnt = request.form.get("content")
        title = request.form.get("title")
        if not ctnt:
            abort(400)
        if not public:
            iv = current_app.config["ENCRYPT_IV"]
            ctnt = encrypt(token.encode(), iv, ctnt)
            for i in ctnt:
                if not chr(i).isprintable() and chr(i) != "\0" and not "\r".isspace():
                    abort(404)
        paste.content = ctnt
        paste.title = title
        paste.last_edit = datetime.utcnow()
        db.session.add(paste)
        db.session.commit()
        return render_template("edit.html", paste=paste, top_pastes=top_pastes)
    if edit_token:
        paste = Paste.query.filter_by(edit_key=edit_token).first_or_404()
        content = paste.content
        if not paste.public:
            iv = current_app.config["ENCRYPT_IV"]
            content = decrypt(token.encode(), iv, content)
            for i in content:
                if not chr(i).isprintable() and chr(i) != "\0" and not "\r".isspace():
                    abort(404)
            return render_template(
                "create.html",
                paste=paste,
                content=content.decode(),
                top_pastes=top_pastes,
            )
        return render_template(
            "create.html", paste=paste, content=content.decode(), top_pastes=top_pastes
        )
    abort(404)


@app.route("/new", methods=["GET", "POST"])
def create():
    print(request.method)
    top_pastes = (
        Paste.query.filter_by(public=True).order_by(Paste.views.desc()).limit(4).all()
    )
    if request.method == "POST":
        print(request.form)
        ctnt = request.form.get("content")
        if not ctnt:
            abort(400)
        # ctnt = ctnt.replace("\r\n", "<br>")
        # ctnt = ctnt.replace("\n", "<br>")
        # ctnt = ctnt.replace("\r", "<br>")
        public = bool(request.form.get("public"))
        title = request.form.get("title")
        if not public:
            iv = current_app.config["ENCRYPT_IV"]
            key = hashify(32)
            encrypted_ctnt = encrypt(key, iv, ctnt)
            paste = Paste(content=encrypted_ctnt, title=title, public=public)
            db.session.add(paste)
            db.session.commit()
            print("\n\n\n\n", paste.id, paste.edit_key, "\n\n\n\n")
            edit_url = url_for(
                "editpaste",
                id=paste.id,
                token=key,
                edit_token=paste.edit_key,
                _external=True,
            )
            read_url = url_for("paste", id=paste.id, token=key, _external=True)
        else:
            paste = Paste(content=ctnt.encode(), title=title, public=public)
            db.session.add(paste)
            db.session.commit()
            edit_url = url_for(
                "editpaste",
                id=paste.id,
                token="1",
                edit_token=paste.edit_key,
                _external=True,
            )
            read_url = url_for("paste", id=paste.id, token="1", _external=True)

        return render_template(
            "create.html",
            read_url=read_url,
            edit_url=edit_url,
            top_pastes=top_pastes,
            paste=paste,
        )
    return render_template("create.html", top_pastes=top_pastes)


@app.route("/public")
def public():
    page = request.args.get("page", 1, int)
    top_pastes = (
        Paste.query.filter_by(public=True).order_by(Paste.views.desc()).limit(4).all()
    )
    paginated = Paste.query.filter_by(public=True)
    search = request.args.get("s")
    if search:
        paginated = paginated.msearch(search)
    paginated = paginated.paginate(page, per_page=8)
    print(paginated.items)
    return render_template("public.html", paginated=paginated, top_pastes=top_pastes)


@app.route("/gg")
def gg():
    for i in range(400):
        paste = Paste(
            content=b"""Mauris non semper metus, nec egestas felis. Quisque rutrum risus vitae magna commodo, eu pharetra mi vulputate. Nunc interdum lectus hendrerit ligula lobortis, tristique ornare urna placerat. Nulla mauris mauris, eleifend id dictum sed, feugiat in nisl. Aliquam viverra, risus a placerat accumsan, ipsum ante tempor enim, non pellentesque est enim vel enim. Fusce commodo hendrerit nibh, eget scelerisque nunc sagittis vitae. Mauris vitae ullamcorper nulla, nec scelerisque eros. Nunc fermentum commodo risus, vel rutrum nulla dictum id.""",
            title="Lore",
            public=True,
        )
        db.session.add(paste)
    db.session.commit()
    return redirect(url_for("index"))
