from flask import Flask, Response

app = Flask(__name__)

@app.route('/', methods=['GET'])
def index():
    print("Hello wor;lds")

    return Response("Test", status=200, mimetype='text/html')

app.run(port=5000)

index()

