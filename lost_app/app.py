import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, g


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
    )

    if test_config is None:
        # default database in the instance folder
        app.config['DATABASE'] = os.path.join(app.instance_path, 'items.db')
    else:
        app.config.update(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path, exist_ok=True)
    except OSError:
        pass

    def get_db():
        if 'db' not in g:
            g.db = sqlite3.connect(
                app.config['DATABASE'], detect_types=sqlite3.PARSE_DECLTYPES
            )
            g.db.row_factory = sqlite3.Row
        return g.db

    def close_db(e=None):
        db = g.pop('db', None)
        if db is not None:
            db.close()

    def init_db():
        db = get_db()
        db.execute(
            '''
            CREATE TABLE IF NOT EXISTS items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                location TEXT,
                date_lost TEXT,
                contact TEXT,
                created TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            '''
        )
        db.commit()

    @app.cli.command('init-db')
    def init_db_command():
        """Create the database tables."""
        init_db()
        print('Initialized the database.')

    @app.teardown_appcontext
    def teardown_db(exception):
        close_db()

    @app.route('/')
    def index():
        db = get_db()
        items = db.execute('SELECT * FROM items ORDER BY created DESC').fetchall()
        return render_template('index.html', items=items)

    @app.route('/report', methods=['GET', 'POST'])
    def report():
        if request.method == 'POST':
            title = request.form.get('title')
            description = request.form.get('description')
            location = request.form.get('location')
            date_lost = request.form.get('date_lost')
            contact = request.form.get('contact')

            if not title:
                return render_template('report.html', error='Title is required')

            db = get_db()
            db.execute(
                'INSERT INTO items (title, description, location, date_lost, contact) VALUES (?, ?, ?, ?, ?)',
                (title, description, location, date_lost, contact),
            )
            db.commit()
            return redirect(url_for('index'))

        return render_template('report.html')

    @app.route('/item/<int:item_id>')
    def item(item_id):
        db = get_db()
        item = db.execute('SELECT * FROM items WHERE id = ?', (item_id,)).fetchone()
        if item is None:
            return ('Not found', 404)
        return render_template('item.html', item=item)

    # expose helpers for tests
    app.get_db = lambda: get_db()
    app.init_db = lambda: (init_db())

    return app


if __name__ == '__main__':
    app = create_app()
    # initialize DB on first run
    app.init_db()
    app.run(debug=True)
