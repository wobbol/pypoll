import sqlite3
import os
import time
import base64
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
        <li> <a href="/poll"  >/poll</a>   </li>
        <li> <a href="/add-q"  >/add-q</a> </li>
        <li> <a href="/insert">/insert</a> </li>
        <li> <a href="/select">/select</a> </li>
    </ul>
'''
def make_unique_id():
    #TODO: report birthday paradox numbers here
    return os.urandom(9)

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

def create_tables():
    conn = get_db()
    with app.open_resource('tables.sql', mode='r') as t:
        conn.cursor().executescript(t.read())
        # if this fails it will raise sqlite3.OperationalError
    conn.commit()

def query_db(query, args=()):
    return get_db().execute(query, args)

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def authorized_row(token):
    count = 0
    rowid = ()
    for row in get_db().execute('SELECT * FROM poll WHERE token=?', (token, )):
        rowid = row['id']
        count += 1
    if count == 1:
        return rowid
    return None

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

@app.route('/add-p', methods=['GET', 'POST'])
def add_poll():
    if request.method == 'POST':
        conn = get_db()
        c = conn.cursor()
        token = base64.b64encode(make_unique_id()).decode()
        val = (request.form['pollname'], token)
        c.execute("INSERT INTO poll (name, token) VALUES (?,?)", val)
        return redirect(url_for('add_question', auth=token))
    return '''
    <h2>Name your poll</h2>
    <form method="post">
    <p><input type=text name=pollname>
    <p><input type=submit name=okay>
    </form>
    '''

@app.route('/add-q', methods=['GET', 'POST'])
def add_question():
    token = request.args.get('auth')
    poll_id = authorized_row(token)
    if not poll_id:
        return redirect(url_for('home'))
    if request.method == 'POST':
        conn = get_db()
        c = conn.cursor()
        question = request.form['question']
        print(type(poll_id))
        print('this this')
        c.execute('''INSERT INTO radio_questions
                            (question, poll_id) VALUES (?,?)''', (question, poll_id))
        return redirect(url_for('add_answer', auth=token, quest=c.lastrowid))
    return '''
    <h2>Add a question</h2>
    <form method="post">
    <p><input type=text name=question>
    <p><input type=submit name=ok value="Okay">
    </form>
    '''
@app.route('/add-a', methods=['GET', 'POST'])
def add_answer():
    token = request.args.get('auth')
    if not authorized_row(token):
        return redirect(url_for('home'))
    q_id = request.args.get('quest', '')
    question = query_db('SELECT * from radio_questions WHERE id=?', q_id)
    # if no row redirect to add_question()
    if request.method == 'POST':
        conn = get_db()
        c = conn.cursor()
        answer = request.form['answer']
        c.execute('''INSERT INTO radio_question_answers
                (radio_question_id, answer) VALUES (?, ?)''', (q_id, answer))
        for item in request.form.items():
            if item[0] == 'okay':
                return redirect(url_for('add_answer', auth=token, quest=q_id))
            elif item[0] == 'another':
                return redirect(url_for('add_question', auth=token))
            elif item[0] == 'finish':
                return redirect(url_for('poll_status', auth=token))
            print(tuple(item))
        #unknown error
        return redirect(url_for('home'))

    ret ="<h2>Add an answer to a question</h2>"
    ret += 'Question: "'
    ret += question.fetchone()['question']
    ret += '"<br>'
    for row in query_db('SELECT answer FROM radio_question_answers WHERE radio_question_id=?', q_id):
        ret += 'q '
        ret += row['answer']
        ret += '<br>'
    ret += '''
    <form method="post">
    <p><input type=text name=answer>
    <p><input type=submit name=okay value="Okay">
    <p><input type=submit name=another value="Add another question">
    <p><input type=submit name=finish value="Finish poll">
    </form>
    '''
    return ret

@app.route('/status-p', methods=['GET'])
def poll_status():
    token = request.args.get('auth')
    p_id = authorized_row(token)
    if not p_id:
        return redirect(url_for('home'))
    ret = ""
    print(type(p_id))
    for que in query_db('SELECT * FROM radio_questions WHERE poll_id=?', str(p_id)):
        ret += que['question'] + "<br>"
        for user_ans in query_db('SELECT * FROM user_answers WHERE question_id=?', str(que['id'])):
            ret += "user" + str(tuple(user_ans)) + "<br>"
        for poss_ans in query_db('SELECT * FROM radio_question_answers WHERE radio_question_id=?', str(que['id'])):
            ret += "poss" + str(tuple(poss_ans)) + "<br>"
    return ret


@app.route('/insert')
def insert_test():
    conn = get_db()
    c = conn.cursor()
    values = (time.time(), make_unique_id(), '127.0.0.1')
    c.execute("INSERT INTO users (date, cookie, ip) VALUES (?, ?, ?)", values)
    return navigation + '<p>done</p>'

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

