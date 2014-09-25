__author__ = 'robdefeo'

# Run a test server.
from detect import app
app.run(host='0.0.0.0', port=8999, debug=True)