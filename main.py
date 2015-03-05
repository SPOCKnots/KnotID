from __future__ import print_function
from flask import (Flask, url_for, render_template, request, redirect,
                   flash, Blueprint)
from analysis import text_to_json, torus_knot_to_json
from fractions import gcd

class ReverseProxied(object):
    '''Wrap the application in this middleware and configure the 
    front-end server to add these headers, to let you quietly bind 
    this to a URL other than / and to an HTTP scheme that is 
    different than what is used locally.

    In nginx:
    location /myprefix {
        proxy_pass http://192.168.0.1:5001;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Scheme $scheme;
        proxy_set_header X-Script-Name /myprefix;
        }

    :param app: the WSGI application
    '''
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        script_name = environ.get('HTTP_X_SCRIPT_NAME', '')
        if script_name:
            environ['SCRIPT_NAME'] = script_name
            path_info = environ['PATH_INFO']
            if path_info.startswith(script_name):
                environ['PATH_INFO'] = path_info[len(script_name):]

        scheme = environ.get('HTTP_X_SCHEME', '')
        if scheme:
            environ['wsgi.url_scheme'] = scheme
        return self.app(environ, start_response)

app = Flask(__name__)
app.wsgi_app = ReverseProxied(app.wsgi_app)

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
