from flask import Flask, send_from_directory, jsonify, request
from datetime import datetime
import sqlite3
import os

from openai import OpenAI

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 25 * 1024 * 1024  # 25 MB límite de Groq
DB_PATH = 'notas.db'

# Carga .env si existe
_env_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(_env_path):
    with open(_env_path) as _f:
        for _line in _f:
            _line = _line.strip()
            if _line and not _line.startswith('#') and '=' in _line:
                _k, _v = _line.split('=', 1)
                os.environ.setdefault(_k.strip(), _v.strip())

GROQ_KEY = os.environ.get('GROQ_API_KEY')
client = OpenAI(api_key=GROQ_KEY, base_url='https://api.groq.com/openai/v1') if GROQ_KEY else None


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_db() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS carpetas (
                id     INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT    UNIQUE NOT NULL,
                fecha  TEXT    NOT NULL
            )
        ''')
        conn.execute('''
            CREATE TABLE IF NOT EXISTS notas (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                titulo     TEXT    UNIQUE NOT NULL,
                contenido  TEXT    NOT NULL,
                fecha      TEXT    NOT NULL,
                palabras   INTEGER NOT NULL,
                carpeta_id INTEGER
            )
        ''')
        cols = [r[1] for r in conn.execute('PRAGMA table_info(notas)').fetchall()]
        if 'carpeta_id' not in cols:
            conn.execute('ALTER TABLE notas ADD COLUMN carpeta_id INTEGER')


@app.route('/')
def index():
    return send_from_directory('static', 'index.html')


@app.route('/api/notas', methods=['GET'])
def get_notas():
    carpeta_id = request.args.get('carpeta_id')
    with get_db() as conn:
        if carpeta_id is not None:
            rows = conn.execute(
                'SELECT id, titulo, fecha, palabras, carpeta_id FROM notas WHERE carpeta_id = ? ORDER BY id DESC',
                (carpeta_id,)
            ).fetchall()
        else:
            rows = conn.execute(
                'SELECT id, titulo, fecha, palabras, carpeta_id FROM notas WHERE carpeta_id IS NULL ORDER BY id DESC'
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


@app.route('/api/notas/<int:nota_id>', methods=['PATCH'])
def renombrar_nota(nota_id):
    data = request.get_json()
    titulo = (data.get('titulo') or '').strip()
    if not titulo:
        return jsonify({'error': 'El título no puede estar vacío'}), 400
    try:
        with get_db() as conn:
            conn.execute('UPDATE notas SET titulo = ? WHERE id = ?', (titulo, nota_id))
    except sqlite3.IntegrityError:
        return jsonify({'error': 'Ya existe una nota con ese título'}), 409
    return jsonify({'titulo': titulo})


@app.route('/api/notas/<int:nota_id>/contenido', methods=['PATCH'])
def editar_contenido(nota_id):
    data = request.get_json()
    contenido = (data.get('contenido') or '').strip()
    if not contenido:
        return jsonify({'error': 'El contenido no puede estar vacío'}), 400
    palabras = len(contenido.split())
    with get_db() as conn:
        conn.execute(
            'UPDATE notas SET contenido = ?, palabras = ? WHERE id = ?',
            (contenido, palabras, nota_id)
        )
    return jsonify({'palabras': palabras})


@app.route('/api/notas/<int:nota_id>', methods=['DELETE'])
def borrar_nota(nota_id):
    with get_db() as conn:
        conn.execute('DELETE FROM notas WHERE id = ?', (nota_id,))
    return '', 204


@app.route('/api/notas/<int:nota_id>/carpeta', methods=['PATCH'])
def mover_nota_carpeta(nota_id):
    data = request.get_json()
    carpeta_id = data.get('carpeta_id')
    with get_db() as conn:
        conn.execute('UPDATE notas SET carpeta_id = ? WHERE id = ?', (carpeta_id, nota_id))
    return jsonify({'carpeta_id': carpeta_id})


@app.route('/api/carpetas', methods=['GET'])
def get_carpetas():
    with get_db() as conn:
        rows = conn.execute('''
            SELECT c.id, c.nombre, c.fecha, COUNT(n.id) as total
            FROM carpetas c
            LEFT JOIN notas n ON n.carpeta_id = c.id
            GROUP BY c.id
            ORDER BY c.nombre
        ''').fetchall()
    return jsonify([dict(r) for r in rows])


@app.route('/api/carpetas', methods=['POST'])
def crear_carpeta():
    data = request.get_json()
    nombre = (data.get('nombre') or '').strip()
    if not nombre:
        return jsonify({'error': 'El nombre no puede estar vacío'}), 400
    fecha = datetime.now().strftime('%d/%m/%Y %H:%M')
    try:
        with get_db() as conn:
            cur = conn.execute('INSERT INTO carpetas (nombre, fecha) VALUES (?, ?)', (nombre, fecha))
            carpeta_id = cur.lastrowid
    except sqlite3.IntegrityError:
        return jsonify({'error': 'Ya existe una carpeta con ese nombre'}), 409
    return jsonify({'id': carpeta_id, 'nombre': nombre, 'fecha': fecha, 'total': 0}), 201


@app.route('/api/carpetas/<int:carpeta_id>', methods=['PATCH'])
def renombrar_carpeta(carpeta_id):
    data = request.get_json()
    nombre = (data.get('nombre') or '').strip()
    if not nombre:
        return jsonify({'error': 'El nombre no puede estar vacío'}), 400
    try:
        with get_db() as conn:
            conn.execute('UPDATE carpetas SET nombre = ? WHERE id = ?', (nombre, carpeta_id))
    except sqlite3.IntegrityError:
        return jsonify({'error': 'Ya existe una carpeta con ese nombre'}), 409
    return jsonify({'nombre': nombre})


@app.route('/api/carpetas/<int:carpeta_id>', methods=['DELETE'])
def borrar_carpeta(carpeta_id):
    with get_db() as conn:
        conn.execute('UPDATE notas SET carpeta_id = NULL WHERE carpeta_id = ?', (carpeta_id,))
        conn.execute('DELETE FROM carpetas WHERE id = ?', (carpeta_id,))
    return '', 204


@app.route('/api/transcribir', methods=['POST'])
def transcribir_audio():
    if not client:
        return jsonify({'error': 'Falta configurar GROQ_API_KEY en el archivo .env'}), 500
    if 'archivo' not in request.files:
        return jsonify({'error': 'No se recibió ningún archivo'}), 400
    archivo = request.files['archivo']
    if not archivo.filename:
        return jsonify({'error': 'Archivo inválido'}), 400
    try:
        response = client.audio.transcriptions.create(
            model='whisper-large-v3',
            file=(archivo.filename, archivo.stream, archivo.content_type),
        )
        return jsonify({'texto': response.text})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/corregir', methods=['POST'])
def corregir_texto():
    if not client:
        return jsonify({'error': 'Falta configurar GROQ_API_KEY en el archivo .env'}), 500
    data = request.get_json()
    texto = (data.get('texto') or '').strip()
    if not texto:
        return jsonify({'error': 'Texto vacío'}), 400
    try:
        response = client.chat.completions.create(
            model='llama-3.3-70b-versatile',
            max_tokens=2048,
            messages=[
                {
                    'role': 'system',
                    'content': (
                        'Sos un corrector de texto. Tu única tarea es corregir puntuación, '
                        'mayúsculas y eliminar muletillas (como "eh", "mmm", "este", "o sea", "digamos") '
                        'del texto que te manden. '
                        'Devolvé únicamente el texto corregido, sin comentarios ni explicaciones.'
                    )
                },
                {'role': 'user', 'content': texto}
            ]
        )
        return jsonify({'texto': response.choices[0].message.content})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/chat', methods=['POST'])
def chat():
    if not client:
        return jsonify({'error': 'Falta configurar GROQ_API_KEY en el archivo .env'}), 500

    data = request.get_json()
    nota_id = data.get('nota_id')
    mensaje = (data.get('mensaje') or '').strip()
    historial = data.get('historial', [])

    if not mensaje:
        return jsonify({'error': 'Mensaje vacío'}), 400

    with get_db() as conn:
        row = conn.execute('SELECT * FROM notas WHERE id = ?', (nota_id,)).fetchone()
    if not row:
        return jsonify({'error': 'Nota no encontrada'}), 404

    nota = dict(row)

    system_prompt = (
        f'Sos un asistente que ayuda a analizar transcripciones de audio. '
        f'La nota se llama "{nota["titulo"]}" y su contenido es:\n\n{nota["contenido"]}\n\n'
        f'Respondé siempre en el mismo idioma que el usuario.'
    )

    messages = [{'role': 'system', 'content': system_prompt}]
    role_map = {'model': 'assistant', 'ai': 'assistant'}
    messages += [{'role': role_map.get(m['role'], m['role']), 'content': m['content']} for m in historial]
    messages.append({'role': 'user', 'content': mensaje})

    try:
        response = client.chat.completions.create(
            model='llama-3.3-70b-versatile',
            max_tokens=1024,
            messages=messages
        )
        text = response.choices[0].message.content
        return jsonify({'respuesta': text})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5000)
