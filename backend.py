import os
from bottle import Bottle

app = Bottle()


APP_NAME = os.environ.get("APP","Default")

@app.route('/')
def index():
    return f'This is the {APP_NAME} application.'

app.run(host='0.0.0.0', port=5001)