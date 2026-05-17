from flask import Flask, send_from_directory, jsonify, request
from datetime import datetime
import sqlite3

app = Flask(__name__)
DB_PATH = 'notas.db'


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_db() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS notas (
                id       INTEGER PRIMARY KEY AUTOINCREMENT,
                titulo   TEXT    UNIQUE NOT NULL,
                contenido TEXT   NOT NULL,
                fecha    TEXT    NOT NULL,
                palabras INTEGER NOT NULL
            )
        ''')


@app.route('/')
def index():
    return send_from_directory('static', 'index.html')


@app.route('/api/notas', methods=['GET'])
def get_notas():
    with get_db() as conn:
        rows = conn.execute(
            'SELECT id, titulo, fecha, palabras FROM notas ORDER BY id DESC'
        ).fetchall()
    return jsonify([dict(r) for r in rows])


@app.route('/api/notas', methods=['POST'])
def crear_nota():
    data = request.get_json()
    titulo = (data.get('titulo') or '').strip()
    contenido = (data.get('contenido') or '').strip()

    if not titulo:
        return jsonify({'error': 'El título no puede estar vacío'}), 400
    if not contenido:
        return jsonify({'error': 'El contenido no puede estar vacío'}), 400

    palabras = len(contenido.split())
    fecha = datetime.now().strftime('%d/%m/%Y %H:%M')

    try:
        with get_db() as conn:
            cur = conn.execute(
                'INSERT INTO notas (titulo, contenido, fecha, palabras) VALUES (?, ?, ?, ?)',
                (titulo, contenido, fecha, palabras)
            )
            nota_id = cur.lastrowid
    except sqlite3.IntegrityError:
        return jsonify({'error': 'Ya existe una nota con ese título'}), 409

    return jsonify({'id': nota_id, 'titulo': titulo, 'fecha': fecha, 'palabras': palabras}), 201


@app.route('/api/notas/<int:nota_id>', methods=['GET'])
def get_nota(nota_id):
    with get_db() as conn:
        row = conn.execute('SELECT * FROM notas WHERE id = ?', (nota_id,)).fetchone()
    if not row:
        return jsonify({'error': 'Nota no encontrada'}), 404
    return jsonify(dict(row))


@app.route('/api/notas/<int:nota_id>', methods=['DELETE'])
def borrar_nota(nota_id):
    with get_db() as conn:
        conn.execute('DELETE FROM notas WHERE id = ?', (nota_id,))
    return '', 204


if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5000)
