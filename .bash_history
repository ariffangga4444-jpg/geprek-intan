ssh -R 80:127.0.0.1:5000 serveo.net
termux-wake-lock
ssh -o ServerAliveInterval=60 -R 80:127.0.0.1:5000 serveo.net
ssh -o ServerAliveInterval=30 -R geprekintan:80:127.0.0.1:5000 serveo.net
npm install -g localtunnel
curl ipv4.icanhazip.com
lt --port 5000
lt --port 5000 --no-open
sed -i "s/openurl = require('openurl')/openurl = { open: () => {} }/" $PREFIX/lib/node_modules/localtunnel/bin/lt.js
lt --port 5000
cd geprek-intan
lt --port 5000
exit
ssh -R 80:127.0.0.1:5000 serveo.net
python app.py
lt --port 5000
python app.py
exit
ssh -R 80:127.0.0.1:5000 serveo.net
python app.py
nano app.py
pkill -f python; pkill -f ssh
python app.py
exit
python app.py
exit
lt --port 5000
ssh -R 80:127.0.0.1:5000 serveo.net
pkg install openssh -y
ssh -R 80:127.0.0.1:5000 serveo.net
exit
pkg update && pkg upgrade
[200~pkg clean
~
pkg clean
python3 -m pip install flask
[200~pkg update && pkg install python~
pkg update && pkg install python
python -m pip install flask
python -c "import flask; print(flask.__version__)"
mkdir geprek-intan
cd geprek-intan
nano app.py
python app.py
nano app.py
python app.py
nano app.py
nano app.pypy
python app.py
nano app.py
nano apk.py
nano app.py
cd geprek-intan
python app.py
nano app.py
python app.py
nano app.py
export SECRET_KEY="$(python -c 'import secrets; print(secrets.token_hex(32))')"
export ADMIN_PASSWORD="GantiDenganPasswordKuat"
python app.py
nano app.py
nano app.
python app.py
rm geprek_intan.db
python app.py
nano app.py
import os
import sqlite3
from datetime import datetime
from flask import Flask, g, redirect, render_template_string, request, url_for
from werkzeug.utils import secure_filename
app = Flask(__name__)
DATABASE = "geprek_intan.db"
UPLOAD_FOLDER = "static/uploads"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
# Buat folder upload jika belum ada
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
def allowed_file(filename):
def get_db():
@app.teardown_appcontext
def close_connection(exception):
MENU = {
}
@app.route("/", methods=["GET", "POST"])
def index():
rm geprek_intan.db
python app.py
nano app.py
python app.py
pkg install nodejs -y
npm install -g localtunnel
python app.py
exit
