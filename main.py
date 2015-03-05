from flask import Flask

app = Flask(__name__)

with open('secret_key.bin', 'rb') as fileh:
    app.secret_key = fileh.read()

from views import kident
app.register_blueprint(kident)

if __name__ == "__main__":
    #app.run()
    app.run(debug=True)
