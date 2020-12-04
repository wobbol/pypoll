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
        <li> <a href="/add-p"  >/add-p</a> </li>
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

def get_user_id(request, session, makenew=True):
    c = get_db().cursor()
    u_row = None
    if 'unique_id' in session:
        u_row = c.execute("SELECT id FROM users WHERE cookie=?",(session['unique_id'], )).fetchone()
    else:
        session['unique_id'] = make_unique_id()
    if u_row:
        print("users row=" + str(u_row['id']) + " retreved")
        return u_row['id']
    if not makenew:
        return None
    now = time.time()
    values = (now, session['unique_id'], request.remote_addr)
    c.execute("INSERT INTO users (date, cookie, ip) VALUES (?, ?, ?)", values)
    print("users row=" + str(c.lastrowid) + " created")
    return c.lastrowid

def get_next_question_id(poll, ques):
    #TODO
    return
@app.route('/thanks')
def poll_end():
    conn = get_db()
    c = conn.cursor()
    p_id = request.args.get('poll')
    if not get_user_id(request, session, makenew=False):
        return redirect(url_for('home'))
    ret = ""
    ret += "<h2>Thanks for your time</h2>"
    ret += '<a href="' + url_for('home') + '">back</a>'
    return ret

@app.route('/poll', methods=['GET', 'POST'])
def poll_test():
    conn = get_db()
    c = conn.cursor()
    p_id = request.args.get('poll')
    q_id = request.args.get('ques')
    if request.method == 'POST':
        u_id = get_user_id(request, session)
        if 'answer' not in request.form:
            return redirect(url_for('poll_test', poll=p_id, ques=q_id))
        a_id = request.form['answer']
        vals = (u_id, q_id, a_id)
        answered_before = c.execute('SELECT id FROM user_answers WHERE user_id=? AND question_id=?',(u_id, q_id)).fetchone()
        if not answered_before:
            print("new")
            c.execute('INSERT INTO user_answers (user_id, question_id, answer_id) VALUES (?,?,?)', vals)
        else:
            print("old")
        ret_next = False
        for question in c.execute("SELECT * FROM radio_questions WHERE poll_id=?", (p_id, )):
            #print(tuple(question))
            if ret_next:
                return redirect(url_for('poll_test', poll=p_id, ques=question['id']))
            print(type(q_id))
            print(type(question['id']))
            if question['id'] == int(q_id):
                ret_next = True
        if ret_next:
            return redirect(url_for('poll_end', poll=p_id))

        return redirect(url_for('poll_test', poll=p_id, ques=q_id))

    poll_name = c.execute("SELECT name FROM poll WHERE id=?", (p_id, )).fetchone()['name']
    row = None
    if q_id:
        row = c.execute("SELECT * FROM radio_questions WHERE poll_id=? AND id=?", (p_id, q_id)).fetchone()
    else:
        #TODO: proper data ordering
        row = c.execute("SELECT * FROM radio_questions WHERE poll_id=?", (p_id,)).fetchone()
        q_id = c.lastrowid
    ret = "qid " + str(row['id']) + "<br>"
    ret += "question: " + row['question'] + "<br>"
    ret += '<form method="post" action="' + url_for('poll_test',poll=p_id,ques=str(row['id'])) + '">'
    for r in c.execute("SELECT * FROM radio_question_answers WHERE radio_question_id=?", (row['id'], )):
        ret += '<p><input type="radio" id="' + str(r['id']) + '" name="answer" value="' + str(r['id']) + '">' + str(r['answer']) +'</p>'
    ret += '''
    <p><input type=submit name=whatever>
    </form>
    '''
    return ret

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
    p_url = url_for('poll_test', poll=p_id)
    s_url = url_for('poll_status', auth=token)
    ret = ""
    ret += "<h2>Poll status page</h2>"
    ret += "<p>poll url:<br><a href=" + p_url + ">" + p_url + "</a></p><br>"
    ret += "<p>poll results url(keep this safe):<br><a href=" + s_url + ">" + s_url + "</a></p><br>"
    print(type(p_id))
    for que in query_db('SELECT * FROM radio_questions WHERE poll_id=?', str(p_id)):
        ret += 'id '+str(que['id'])+' question: "' + que['question'] + '"'
        ret += '<ul>'
        for poss_ans in query_db('SELECT * FROM radio_question_answers WHERE radio_question_id=?', str(que['id'])):
            ret += "<li>id "+str(poss_ans['id'])+' answer: "' + (poss_ans['answer']) + '"'
            count = 0
            for user_ans in query_db('SELECT * FROM user_answers WHERE question_id=? AND answer_id=?', (str(que['id']), poss_ans['id'])):
                count += 1
            ret += " tally: " + str(count) + "<ul>"
            for user_ans in query_db('SELECT * FROM user_answers WHERE question_id=? AND answer_id=?', (str(que['id']), poss_ans['id'])):
                u = query_db('SELECT * FROM users WHERE id=?', (user_ans['user_id'], )).fetchone()
                token = base64.b64encode(u['cookie']).decode()
                ret += "<li>" +u['ip']  + " " + token + "</li>"
            ret += "</ul></li>"
        ret += '</ul>'
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

