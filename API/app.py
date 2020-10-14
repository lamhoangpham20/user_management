from flask import Flask
import os

#Initialize app
app = Flask(__name__)

#Run server
if __name__ == '__main__':
    app.run(debug=True)