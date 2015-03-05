from __future__ import print_function
from flask import (Flask, url_for, render_template, request, redirect,
                   flash, Blueprint)
from analysis import text_to_json, torus_knot_to_json
from fractions import gcd

app = Flask(__name__)

with open('secret_key.bin', 'rb') as fileh:
    app.secret_key = fileh.read()

@app.route('/')
def main():
    print('yay')
    return render_template('index.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload():

    if request.method == 'POST':
        return upload_post()

    elif request.method == 'GET':
        return upload_get()

    flash('invalid upload request')
    return upload_fail()

def upload_get():
    args = request.args

    if 'mode' not in args:
        flash('No knot construction mode set (perhaps you entered the wrong URL)')
        return upload_fail()

    if args['mode'] == 'torus':
        if 'p' not in args or 'q' not in args:
            flash('p and/or q parameters were not provided')
            return upload_fail()

        try:
            p = int(args['p'])
            q = int(args['q'])
        except ValueError:
            flash('Could not convert p and q to integers')
            return upload_fail()

        if gcd(p, q) != 1:
            flash('Chosen p and q are not coprime')
            return upload_fail()

        array_json, camera_extent, extra_stuff = torus_knot_to_json(p, q)
    else:
        flash('invalid mode (should be \'torus\')')
        return upload_fail()
    tube_points = 600

    return render_template('upload.html', 
                           parse_success=True,
                           line_points=array_json,
                           camera_extent=camera_extent,
                           tube_points=tube_points,
                           **extra_stuff)


def upload_fail():
    return redirect(url_for('main'))

def upload_post():
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
        array_json, camera_extent, extra_stuff = text_to_json(text)
        parse_success = True
    except ValueError:
        flash('Could not parse uploaded knot points')
        return upload_fail()


    tube_points = 10*num_lines

    return render_template('upload.html', num_lines=num_lines,
                           parse_success=parse_success,
                           line_points=array_json,
                           camera_extent=camera_extent,
                           tube_points=tube_points,
                           **extra_stuff)


@app.route('/about')
def about():
    return render_template('about.html')

if __name__ == "__main__":
    #app.run()
    app.run(debug=True)
