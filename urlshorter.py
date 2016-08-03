# -*- coding: utf-8 -*-

import os
import string
import random
from datetime import datetime
from urlparse import urlparse

from flask import Flask, request, render_template, redirect, abort
from flask.ext.sqlalchemy import SQLAlchemy

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'data.db')

db = SQLAlchemy(app)

class URLShortener(db.Model):
    __tablename__ = 'url'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    code = db.Column(db.String(10), unique=True)
    url = db.Column(db.String(500), unique=True)
    created = db.Column(db.DateTime, default=datetime.now)
    visit_count = db.Column(db.Integer, default=0)

    def __init__(self, url):
        self.url = url
        code = self.get_code(5)
        self.code = code

    @staticmethod
    def get_code(size):
        return "".join(random.sample(string.ascii_letters + string.digits, size))


@app.route('/', methods=['GET', 'POST'])
def home():
    short_url = ''
    if request.method == 'POST':
        original_url = request.form.get("url")
        if urlparse(original_url).scheme == '':
            original_url = 'http://' + original_url
        tmp = URLShortener.query.filter_by(url=original_url).first()
        if tmp:
            url = tmp
        else:
            url = URLShortener(url=original_url)
            db.session.add(url)
            db.session.commit()
        short_url = request.host + '/' + url.code
    return render_template('home.html', short_url = short_url)

@app.route('/<string:code>')
def get_original_url(code):
    original_url = URLShortener.query.filter_by(code=code).first()
    if not original_url:
        abort(404)
    original_url.visit_count += 1
    db.session.add(original_url)
    db.session.commit()
    return redirect(original_url.url)

if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)
