from flask import Flask, render_template, request, redirect, url_for, session, flash, send_from_directory
import sqlite3
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = '5f7caa2d6f1b47e2b87e29d59f94bc87'

DATABASE = 'valexdp.db'
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def home():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        try:
            conn.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            conn.commit()
            flash('Kayıt başarılı! Şimdi giriş yap.', 'success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('⚠️ Bu kullanıcı adı zaten alınmış!', 'error')
        finally:
            conn.close()
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        user = conn.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password)).fetchone()
        conn.close()

        if user:
            session['user_id'] = user['id']
            session['username'] = user['username']
            return redirect(url_for('dashboard'))
        else:
            flash('❌ Hatalı kullanıcı adı veya şifre!', 'error')
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    files = conn.execute("SELECT * FROM files WHERE user_id = ?", (session['user_id'],)).fetchall()
    conn.close()

    return render_template('dashboard.html', username=session['username'], files=files)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if 'file' not in request.files:
        flash("⚠️ Dosya seçilmedi!")
        return redirect(url_for('dashboard'))

    file = request.files['file']
    if file.filename == '':
        flash("⚠️ Dosya seçilmedi!")
        return redirect(url_for('dashboard'))

    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)

    # Aynı isimli dosya varsa sonuna (1), (2) gibi ek yap
    counter = 1
    base, ext = os.path.splitext(filename)
    while os.path.exists(filepath):
        filename = f"{base}({counter}){ext}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        counter += 1

    file.save(filepath)

    conn = get_db_connection()
    conn.execute("INSERT INTO files (filename, user_id) VALUES (?, ?)", (filename, session['user_id']))
    conn.commit()
    conn.close()

    flash(f'Dosya yüklendi: <a href="{url_for("uploaded_file", filename=filename)}" target="_blank">{filename}</a>')
    return redirect(url_for('dashboard'))

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    # Dosyaları doğrudan uploads klasöründen servis et
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/logout')
def logout():
    session.clear()
    flash('Başarıyla çıkış yapıldı.')
    return redirect(url_for('login'))

if __name__ == '__main__':
    from waitress import serve
    serve(app, host='0.0.0.0', port=8080)
