from __future__ import print_function
from flask import (Flask, url_for, render_template, request, redirect,
                   flash)
from logging import Formatter, INFO
from logging.handlers import RotatingFileHandler
from analysis import (text_to_json, torus_knot_to_json,
                      gauss_code_to_json, dt_code_to_json)
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

app.config['MAX_CONTENT_LENGTH'] = 300 * 1024

with open('secret_key.bin', 'rb') as fileh:
    app.secret_key = fileh.read()

file_handler = RotatingFileHandler('logs/info.log', maxBytes=1e6,
                                  backupCount=10)
file_handler.setLevel(INFO)
file_handler.setFormatter(Formatter(
    '%(asctime)s %(levelname)s: %(message)s'
))
app.logger.addHandler(file_handler)
app.logger.setLevel(INFO)


@app.route('/')
def main():
    return render_template('index.html')


@app.route('/upload', methods=['GET', 'POST'])
def upload():

    if request.method == 'POST':
        return upload_post()

    elif request.method == 'GET':
        return upload_get()

    flash('invalid upload request')
    return upload_fail()

def get_ip():
    if len(request.access_route) > 1:
        return request.access_route[-1]
    else:
        return request.access_route[0]

def log_analysis(context, analysis):
    num_crossings = str(analysis.get('num_crossings', '?'))
    reduced_num_crossings = analysis.get('reduced_num_crossings', '?')
    num_points = analysis.get('num_points', None)
    roots = analysis.get('alex_roots', None)
    cached = 'new'
    if 'cached' in analysis:
        cached = 'cached' if analysis['cached'] else 'new'
        if 'num_times_accessed' in analysis:
            cached += ' {}'.format(analysis['num_times_accessed'])
    ip = get_ip()
    app.logger.info('Received {}{}, GC length {}->{}, ({}){}, from {}'.format(
        context,
        ', {} points'.format(num_points) if num_points is not None else '',
        num_crossings, reduced_num_crossings,
        cached,
        ', roots {}'.format(tuple(roots)) if roots is not None else '',
        ip))

def log_failure(context, message):
    app.logger.info('Failed {}, from {}'.format(context, message))

def upload_get():
    args = request.args

    if 'mode' not in args:
        flash('No knot construction mode set (perhaps you entered the '
              'wrong URL)')
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

        if p > 20 or q > 20:
            flash('p and q must currently both be less than 20')
            return upload_fail()

        if p < 1 or q < 1:
            flash('p and q must both be greater than 0')
            return upload_fail()

        if gcd(p, q) != 1:
            flash('Chosen p and q are not coprime')
            return upload_fail()

        array_json, camera_extent, extra_stuff = torus_knot_to_json(p, q)
    else:
        flash('invalid mode (should be \'torus\')')
        return upload_fail()
    tube_points = 600

    log_analysis('UPLOAD-GET', extra_stuff)

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
    if num_lines > 3000:
        flash('Too many vertices in uploaded curve. Current maximum is '
              '3000, received {}'.format(num_lines))
        return upload_fail()

    parse_success = False

    try:
        array_json, camera_extent, extra_stuff = text_to_json(text)
        parse_success = True
    except ValueError:
        flash('Could not parse uploaded knot points')
        return upload_fail()

    tube_points = 10*num_lines

    log_analysis('UPLOAD-POST', extra_stuff)

    return render_template('upload.html', num_lines=num_lines,
                           parse_success=parse_success,
                           line_points=array_json,
                           camera_extent=camera_extent,
                           tube_points=tube_points,
                           **extra_stuff)


@app.errorhandler(413)
def request_entity_too_large(error):
    flash('Uploaded file is too large, max size is 200kb')
    return upload_fail()

@app.errorhandler(500)
def error(error):
    flash('test')
    # flash('Error 500 (internal server error): If the problem '
    #       'persists, please contact <a href="mailto:alexander.'
    #       'taylor@bristol.ac.uk">alexander.taylor@bristol.ac.uk'
    #       '</a>.')
    return redirect(url_for('main'))

@app.errorhandler(404)
def notfound(error):
    flash('Error 404 (page not found)')
    return redirect(url_for('main'))

@app.route('/raiseerror')
def raise500():
    raise Exception('test error')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/documentation')
def documentation():
    return render_template('documentation.html')

@app.route('/draw')
def draw():
    return render_template('draw.html')

# @app.route('/secret_dt_upload')
# def secret_dt_upload():
#     return render_template('secret_dt_upload.html')

@app.route('/api/analyse')
def analyse():
    args = request.args
    if 'gausscode' not in args and 'dtcode' not in args:
        return 'FAIL: No DT code or Gauss code received'

    if 'gausscode' in args:
        analysis = gauss_code_to_json(args['gausscode'].replace('b', '+'))
    else:  # 'dtcode' is in args
        analysis = dt_code_to_json(args['dtcode'].replace('b', ' '))

    if analysis[0]:
        return render_template('error.html', error=analysis[1])

    log_analysis('GAUSSCODE', analysis[1])

    return render_template('knot_invariants.html', **analysis[1])


@app.route('/gausscode')
def gausscode():
    return render_template('gausscode.html')

@app.route('/dowker')
def dowker():
    return render_template('dowker.html')

if __name__ == "__main__":
    #app.run()
    app.run(debug=True)
