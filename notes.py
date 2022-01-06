from pathlib import Path
from sqlite3 import dbapi2 as sqlite3

from quart import g, Quart, redirect, render_template, request, url_for

app = Quart(__name__)

app.config.update({
    'DATABASE': app.root_path / 'notes.db',
    'DEBUG': True,
})


@app.route('/', methods=['GET'])
async def notes():
    db = get_db()
    cur = db.execute('SELECT id, title, text FROM note')
    notes = cur.fetchall()
    return await render_template('notes_home.html', notes=notes)

@app.route('/delete/', methods=['POST'])
async def delete():
    db = get_db()
    form = await request.form
    print("delete",form)
    db.execute(
        "DELETE FROM note WHERE id= ? ",
        [form['note_id']],
    )
    db.commit()
    return redirect(url_for('notes'))

@app.route('/create/', methods=['POST'])
async def create():
    db = get_db()
    form = await request.form
    print("create",form)
    db.execute(
        "INSERT INTO note (title, text) VALUES (?, ?)",
        [form['title'], form['text']],
    )
    db.commit()
    return redirect(url_for('notes'))

def connect_db():
    engine = sqlite3.connect(app.config['DATABASE'])
    engine.row_factory = sqlite3.Row
    return engine


@app.cli.command('init_db')
def init_db():
    _init_db()


def _init_db():
    db = connect_db()
    with open(Path(__file__).parent / 'schema.sql', mode='r') as file_:
        db.cursor().executescript(file_.read())
    db.commit()


def get_db():
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db