from flask import Flask, request, render_template, send_from_directory, redirect, url_for, flash
import os

app = Flask(__name__)
app.secret_key = '5f7caa2d6f1b47e2b87e29d59f94bc87'
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        flash('Dosya seçilmedi!')
        return redirect(url_for('index'))
    
    file = request.files['file']
    
    if file.filename == '':
        flash('Dosya adı boş!')
        return redirect(url_for('index'))

    file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))
    flash(f"Yükleme Başarılı! 🔗 <a href='/uploads/{file.filename}' target='_blank'>{file.filename}</a>")
    return redirect(url_for('index'))

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True)
