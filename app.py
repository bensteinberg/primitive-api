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


def clamp(n, minimum, maximum):
    return max(min(maximum, int(n)), minimum)


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

    # number of primitives: max of 2048 is arbitrary
    n = clamp(request.form['n'], 2048, 1) if 'n' in request.form else 128

    # shape: 0=combo 1=triangle 2=rect 3=ellipse 4=circle 5=rotatedrect
    # 6=beziers 7=rotatedellipse 8=polygon
    m = clamp(request.form['m'], 8, 0) if 'm' in request.form else 1

    cmd = f'primitive -i {input_path} -o {output_path} -n {n} -m {m}'
    run(cmd.split(' '))

    with open(output_path, 'rb') as f:
        data = b64encode(f.read()).decode()

    return jsonify(img=f"<img src='data:image/jpeg;base64,{data}'>", m=m, n=n)


app.run(host='0.0.0.0', port=8000)
