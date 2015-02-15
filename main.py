from flask import Flask, url_for, render_template, request
from analysis import text_to_json

app = Flask(__name__)


@app.route('/')
def main():
    return render_template('index.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        if 'pointstext' in request.form:
            pointstext = request.form['pointstext']
            text = pointstext
            lines = pointstext.split('\n')

        if 'pointsfile' in request.files:
            pointsfile = request.files['pointsfile']
            text = pointsfile.read().decode('utf8')
            lines = text.split('\n')

        num_lines = len(lines)

        parse_success = False

        try:
            array_json, camera_extent = text_to_json(text)
            parse_success = True
        except ValueError:
            print('Caught ValueError')
            array_json = []
            camera_extent = 5

        print('num_lines is', num_lines)
        print('lines is', lines)

        tube_points = 10*num_lines

        return render_template('upload.html', num_lines=num_lines,
                               parse_success=parse_success,
                               line_points=array_json,
                               camera_extent=camera_extent,
                               tube_points=tube_points)

    else:
        return render_template('upload_fail.html')

if __name__ == "__main__":
    app.run(debug=True)
