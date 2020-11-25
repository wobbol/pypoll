import sqlite3
from flask import Flask
app = Flask(__name__)

navigation = '''
<h3>endpoints</h3>
    <ul>
        <li> <a href="/"      >/</a>       </li>
        <li> <a href="/create">/create</a> </li>
        <li> <a href="/insert">/insert</a> </li>
        <li> <a href="/select">/select</a> </li>
    </ul>
    '''

@app.route('/')
def home():
    return navigation

@app.route('/create')
def create_test():
    conn = sqlite3.connect('stonks.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE stonks
    (date text, trans text, symbol, text qty real, price real)''')
    c.execute("INSERT INTO stonks VALUES ('20-01-2020', 'BUY', 'RHAT', 100, 35.14)")
    conn.commit()
    conn.close()
    return navigation

@app.route('/insert')
def insert_test():
    conn = sqlite3.connect('stonks.db')
    c = conn.cursor()
    c.execute("INSERT INTO stonks VALUES ('20-01-2020', 'BUY', 'RHAT', 100, 35.14)")
    conn.commit()
    conn.close()
    return navigation + '<p>done</p>'

@app.route('/select')
def select_test():
    conn = sqlite3.connect('stonks.db')
    c = conn.cursor()
    t = ('RHAT',)
    ret = ""
    for row in c.execute('SELECT * FROM stonks WHERE symbol=?', t):
        ret += str(row)
        ret += '<br>\n'
    conn.close()
    return navigation + ret

