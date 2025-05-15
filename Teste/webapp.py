import os
from flask import Flask, request, render_template, send_file, redirect, url_for
from werkzeug.utils import secure_filename
import tempfile
import shutil
import subprocess

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'035'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            return render_template('index.html', error='Nenhum arquivo enviado.')
        file = request.files['file']
        if file.filename == '':
            return render_template('index.html', error='Nenhum arquivo selecionado.')
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            temp_dir = tempfile.mkdtemp()
            file_path = os.path.join(temp_dir, filename)
            file.save(file_path)
            output_base = os.path.splitext(filename)[0] + '_atualizado'
            output_json = os.path.join(temp_dir, output_base + '.json')
            output_txt = os.path.join(temp_dir, output_base + '.txt')
            # Chama o script principal para processar
            subprocess.run([
                'python', 'main.py',
                '--input', file_path,
                '--from', 'txt',
                '--to', 'txt',
                '--output', os.path.join(temp_dir, output_base),
                '--processar_035'
            ], check=True)
            # Disponibiliza para download
            return render_template('result.html',
                json_url=url_for('download_file', path=output_json),
                txt_url=url_for('download_file', path=output_txt),
                json_name=output_base + '.json',
                txt_name=output_base + '.txt')
        else:
            return render_template('index.html', error='Tipo de arquivo não suportado. Envie um arquivo .035.')
    return render_template('index.html')

@app.route('/download')
def download_file():
    path = request.args.get('path')
    if not path or not os.path.isfile(path):
        return 'Arquivo não encontrado.', 404
    return send_file(path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
