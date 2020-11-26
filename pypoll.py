import sqlite3
import os
import time
from flask import Flask, session, redirect, url_for, request, g
from socket import inet_pton, inet_ntop
from struct import unpack, pack
app = Flask(__name__)
app.secret_key = os.urandom(16) # TODO: store this in a file

database = 'data.db'
navigation = '''
<h3>endpoints</h3>
    <ul>
        <li> <a href="/"      >/</a>       </li>
        <li> <a href="/create">/create</a> </li>
        <li> <a href="/insert">/insert</a> </li>
        <li> <a href="/select">/select</a> </li>
    </ul>
'''
def make_unique_id():
    #TODO: report birthday paradox numbers here
    return os.urandom(8)

def ip2bytes(ip):
    try:
        return inet_pton(AF_INET, ip)
    except OSError:
        try:
            return inet_pton(AF_INET6, ip)
        except OSError:
            return None
def bytes2ip(ip_bytes):
    try:
        return inet_ntop(AF_INET, ip_bytes)
    except (ValueError, OSError):
        try:
            return inet_ntop(AF_INET6, ip_bytes)
        except (ValueError, OSError):
            return None

#isolation_level=None leaves sqlite3 in autcommit mode
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(database, isolation_level=None)
        db.row_factory = sqlite3.Row
        db.execute('PRAGMA foreign_keys = 1')
    return db

def query_db(query, args=()):
    return get_db().execute(query, args)

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@app.route('/')
def home():
    return navigation

@app.route('/poll', methods=['GET', 'POST'])
def poll_test():
    if request.method == 'POST':
        if 'unique_id' in session:
            return 'thonk'
        session['unique_id'] = make_unique_id()
        now = time.time()
        conn = get_db()
        c = conn.cursor()
        values = (now, session['unique_id'], request.remote_addr)
        c.execute("INSERT INTO users (date, cookie, ip) VALUES (?, ?, ?)", values)


        return redirect(url_for('home'))
    return '''
    <form method="post">
    <p><input type=text name=username>
    <p><input type=submit name=whatever>
    </form>
    '''


@app.route('/create')
def create_test():
    conn = get_db()
    #try:
    with app.open_resource('tables.sql', mode='r') as t:
        conn.cursor().executescript(t.read())
    #except sqlite3.OperationalError:
    #    print('Database exists already')
    #    raise
    conn.commit()
    return navigation

@app.route('/insert')
def insert_test():
    conn = get_db()
    c = conn.cursor()
    values = (time.time(), make_unique_id(), '127.0.0.1')
    c.execute("INSERT INTO users (date, cookie, ip) VALUES (?, ?, ?)", values)
    return navigation + '<p>done</p>'

@app.route('/sel')
def sel():
    for trans in query_db('SELECT * from users WHERE ip="127.0.0.1"'):
        print(trans['date'])
        print(str(tuple(trans)))
    return 'ha'


@app.route('/select')
def select_test():
    conn = get_db()
    c = conn.cursor()
    t = ('127.0.0.1',)
    ret = ""
    for row in c.execute('SELECT * FROM users WHERE ip=?', t):
        ret += str(row['id']) + ", "
        ret += time.asctime(time.localtime(row['date'])) + ", "
        ret += "0x" + row['cookie'].hex() + ", "
        ret += str(row['ip']) + ""
        ret += '<br>\n'
    conn.close()
    return navigation + ret

