# http://blog.luisrei.com/articles/flaskrest.html
from flask import Flask, url_for
app = Flask(__name__)

@app.route('/' methods = ['GET'])
def api_root():
    return 'Welcome'

if __name__ == '__main__':
    app.run()
    # print "app=detection,port=%d,mode=%s,action=started", port, app.settings.env)
