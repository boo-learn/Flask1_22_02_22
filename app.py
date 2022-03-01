# client --> Request(HTTP) --> request -->
# server Response --> HTTP
import flask
import os
import sqlite3
from pathlib import Path
from flask import Flask, jsonify, request, g
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

BASE_DIR = Path(__file__).parent
PATH_TO_DB = BASE_DIR / "test.db"
# Request(HTTP) --> request
app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL').replace("://", "ql://", 1) or f"sqlite:///{BASE_DIR / 'main.db'}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)


class AuthorModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), unique=True)
    quotes = db.relationship('QuoteModel', backref='author', lazy='dynamic')

    def __init__(self, name):
        self.name = name

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name
        }


class QuoteModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey(AuthorModel.id))
    text = db.Column(db.String(255), unique=False)

    def __init__(self, author, text):
        self.author_id = author.id
        self.text = text

    def to_dict(self):
        return {
            "id": self.id,
            "author": self.author.to_dict(),
            "text": self.text
        }

# AUTHORS

@app.route("/authors")
def authors_list():
    authors_obj = AuthorModel.query.all()
    authors_dict = []
    for author in authors_obj:
        authors_dict.append(author.to_dict())
    return jsonify(authors_dict), 200


@app.route("/authors", methods=['POST'])
def create_authors():
    data = request.json
    try:
        author = AuthorModel(**data)
    except KeyError:
        return "required data None", 400
    db.session.add(author)
    db.session.commit()
    return jsonify(author.to_dict()), 201

# QUOTES

@app.route("/quotes")
def quote():
    quotes_obj = QuoteModel.query.all()  # SQL: SELECT * from ...
    quotes_dict = []
    for quote in quotes_obj:
        quotes_dict.append(quote.to_dict())
    return jsonify(quotes_dict), 200


# /quotes/1
# /quotes/2
# /quotes/12
@app.route("/quotes/<int:quote_id>")
def show_quote(quote_id):
    quote = QuoteModel.query.get(quote_id)
    if quote is None:
        return f"Quote with id {quote_id} not found", 404
    return jsonify(quote.to_dict())


@app.route("/authors/<int:author_id>/quotes", methods=['POST'])
def create_quote(author_id):
    data = request.json
    author = AuthorModel.query.get(author_id)
    try:
        quote = QuoteModel(author, **data)
    except KeyError:
        return "required data None", 400
    db.session.add(quote)
    db.session.commit()
    return jsonify(quote.to_dict()), 201


@app.route("/quotes/<int:quote_id>", methods=['PUT'])
def edit_quote(quote_id):
    data = request.json
    quote = QuoteModel.query.get(quote_id)
    if quote is None:
        return f"Quote with id {quote_id} not found", 404

    for key, value in data.items():
        setattr(quote, key, value)

    db.session.commit()
    return jsonify(quote.to_dict()), 200


@app.route("/quotes/<int:quote_id>", methods=['DELETE'])
def delete(quote_id):
    # delete quote with id
    return f"Quote with id {id} is deleted.", 200


if __name__ == "__main__":
    app.run(debug=True)
