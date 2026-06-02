import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_cors import CORS # Nueva importación

app = Flask(__name__)
app.secret_key = 'clave_secreta_super_segura'
DB_NAME = 'database.db'

CORS(app, supports_credentials=True)

def init_db():
    if not os.path.exists(DB_NAME):
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE usuarios (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, password TEXT, nombre TEXT)''')
        cursor.execute('''CREATE TABLE productos (id INTEGER PRIMARY KEY AUTOINCREMENT, codigo TEXT UNIQUE, nombre TEXT, descripcion TEXT, precio REAL, stock INTEGER, categoria TEXT)''')
        cursor.execute("INSERT INTO usuarios (username, password, nombre) VALUES ('admin', '12345', 'Carlos Roque Silva Valera')")
        productos = [
            ('P001', 'Procesador Ryzen 5 8600G', 'Procesador AMD AM5 con gráficos integrados', 850.00, 12, 'Componentes PC'),
            ('P002', 'Placa Madre B650', 'Placa base socket AM5', 620.00, 5, 'Componentes PC'),
            ('P003', 'Smartphone Redmi Note 14 5G', 'Teléfono 5G', 1100.00, 20, 'Celulares')
        ]
        cursor.executemany("INSERT INTO productos (codigo, nombre, descripcion, precio, stock, categoria) VALUES (?, ?, ?, ?, ?, ?)", productos)
        conn.commit()
        conn.close()

init_db()

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn



@app.route('/', methods=['GET'])
def index():

    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'logged_in' in session:
        return redirect(url_for('principal'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM usuarios WHERE username = ? AND password = ?', (username, password)).fetchone()
        conn.close()
        
        if user:
            session['logged_in'] = True
            session['username'] = user['username']
            session['nombre'] = user['nombre']
            return redirect(url_for('principal'))
        else:
            flash('Credenciales incorrectas. Inténtalo de nuevo.')
            
    return render_template('login.html')

@app.route('/principal', methods=['GET'])
def principal():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template('principal.html')

@app.route('/buscador', methods=['GET'])
def buscador():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    return render_template('buscador.html')

@app.route('/api/buscar_producto', methods=['POST'])
def buscar_producto():

    data = request.get_json()
    code = data.get('codigo')
    
    conn = get_db_connection()
    producto = conn.execute('SELECT * FROM productos WHERE codigo = ?', (code,)).fetchone()
    conn.close()
    
    if producto:

        return jsonify({
            'success': True,
            'data': dict(producto)
        })
    else:
        return jsonify({
            'success': False,
            'message': 'Producto no encontrado'
        }), 404

@app.route('/logout', methods=['GET'])
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)