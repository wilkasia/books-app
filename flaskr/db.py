import mysql.connector


import click
from flask import current_app, g
from flask.cli import with_appcontext


def get_db():
    print("get_db")
    if 'db' not in g:
        # g.db = sqlite3.connect(
        #     current_app.config['DATABASE'],
        #     detect_types=sqlite3.PARSE_DECLTYPES
        # )
        g.db = mysql.connector.connect(
            user='booksapp',
            password='az14Gcjs',
            host='localhost',
            port=13306,
            database='booksapp'
        )
        # g.db.row

    return g.db


def close_db(e=None):
    print("close_db")
    db = g.pop('db', None)

    if db is not None:
        db.close()


def init_db():
    print("init_db")
    db = get_db()

    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))


@click.command('init-db')
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)


# import mysql.connector
#
# cnx = mysql.connector.connect(user='scott', password='password',
#                               host='127.0.0.1',
#                               database='employees')
# cnx.close()