import os


from flask import Flask, flash, request, redirect, render_template, jsonify
from werkzeug.utils import secure_filename
from tasks import simple_func, celery
from celery.result import AsyncResult
from settings import OPERATOR_FILE_PATH


ALLOWED_EXTENSIONS = {'txt', 'dbf', 'xlsx'}

app = Flask(__name__)
app.config.from_object('settings')
app.secret_key = app.config['SECRET_KEY']


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


operator_codes = {'SE': 'sev_el', 'GAZPROM': 'gaz_prom'}


@app.route('/handler', methods=['GET', 'POST'])
def file_handler():
    if request.method == 'POST':
        operator_code = request.form.get('operator_code')
        if operator_code not in operator_codes:
            flash('Такого оператора нет!')
            return redirect(request.url)
        else:
            dir_name = operator_codes.get(operator_code)
            for file in request.files.getlist('file'):
                if 'file' not in request.files or file.filename == '':
                    flash('Файлы не выбраны!')
                    return redirect(request.url)
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    if os.path.exists(f'{OPERATOR_FILE_PATH}/{dir_name}'):
                        if os.path.isfile(f'{OPERATOR_FILE_PATH}/{filename}'):
                            os.remove(f'{OPERATOR_FILE_PATH}/{dir_name}/{filename}')
                        file.save(os.path.join(f'{OPERATOR_FILE_PATH}/{dir_name}', filename))
                    else:
                        os.mkdir(f'{OPERATOR_FILE_PATH}/{dir_name}')
                        file.save(os.path.join(f'{OPERATOR_FILE_PATH}/{dir_name}', filename))
                else:
                    flash('Тип файла не подходит!')
                    return redirect(request.url)
            task1 = simple_func.delay()
            return jsonify({'task_id': task1.id}), 202
    return render_template('download_file.html')


@app.route('/handler/<task_id>', methods=['GET'])
def get_status(task_id):
    task_result = AsyncResult(task_id, backend=celery.backend)
    result = {
        'task_id': task_id,
        'task_status': task_result.status
    }
    return jsonify(result), 200


if __name__ == "__main__":
    app.run(debug=True)
