__author__ = 'robdefeo'
from detect.settings import PORT
# Run a test server.
from detect import app
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=PORT, debug=True)