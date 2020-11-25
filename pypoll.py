import sqlite3
import os
from flask import Flask, session, redirect, url_for, request, g
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

#isolation_level=None leaves sqlite3 in autcommit mode
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(database, isolation_level=None)
        db.row_factory = sqlite3.Row
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
        session['unique_id'] = os.urandom(8)
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
    conn.execute('''
    CREATE TABLE user (
            id     integer  NOT NULL PRIMARY KEY ASC,
            date   text NOT NULL,
            cookie text NOT NULL,
            ip     text NOT NULL
    )
    ''')
    #except sqlite3.OperationalError:
    #    print('Database exists already')
    #    raise
    conn.commit()
    return navigation

@app.route('/insert')
def insert_test():
    conn = get_db()
    c = conn.cursor()
    values = ('20-01-2020', 'cookie', '127.0.0.1')
    c.execute("INSERT INTO user (date, cookie, ip) VALUES (?, ?, ?)", values)
    return navigation + '<p>done</p>'

@app.route('/sel')
def sel():
    for trans in query_db('SELECT * from user WHERE ip="127.0.0.1"'):
        print(trans['date'])
        print(str(tuple(trans)))
    return 'ha'


@app.route('/select')
def select_test():
    conn = get_db()
    c = conn.cursor()
    t = ('127.0.0.1',)
    ret = ""
    for row in c.execute('SELECT * FROM user WHERE ip=?', t):
        ret += str(tuple(row))
        ret += '<br>\n'
    conn.close()
    return navigation + ret

