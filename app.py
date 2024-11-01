from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
from pathlib import Path
from tempfile import mkdtemp, mkstemp
from subprocess import run
from base64 import b64encode


ALLOWED = {'png', 'jpg', 'jpeg'}

app = Flask(__name__)
app.config['SECRET_KEY'] = 'whatever'


def allowed_file(name):
    return '.' in name and Path(name).suffix[1:].lower() in ALLOWED


@app.route('/', methods=['POST'])
def transform():
    if 'file' not in request.files:
        return jsonify(error='No file in request'), 400
    upload = request.files['file']
    if upload.filename == '':
        return jsonify(error='No file selected'), 400
    if not allowed_file(upload.filename):
        return jsonify(error='Bad file type'), 400

    input_path = Path(mkdtemp()) / secure_filename(upload.filename)
    upload.save(input_path)

    _, output_path = mkstemp(suffix='.jpg')

    # number of primitives
    try:
        n = int(request.form.get('n', '128'))
    except ValueError:
        return jsonify(error='n must be an integer')
    if n < 1:
        return jsonify(error='n must be positive')

    # shape: 0=combo 1=triangle 2=rect 3=ellipse 4=circle 5=rotatedrect
    # 6=beziers 7=rotatedellipse 8=polygon
    try:
        m = int(request.form.get('m', '1'))
    except ValueError:
        return jsonify(error='m must be an integer')
    if not m in range(9):
        return jsonify(error='Shape (m) must be between 0 and 8')

    cmd = f'primitive -i {input_path} -o {output_path} -n {n} -m {m}'
    run(cmd.split(' '))

    with open(output_path, 'rb') as f:
        data = b64encode(f.read()).decode()

    return jsonify(img=f"<img src='data:image/jpeg;base64,{data}'>", m=m, n=n)


app.run(host='0.0.0.0', port=8000)
