__author__ = 'robdefeo'
import sys

from flask import Flask

app = Flask(__name__)

from detect.container import Container
container = Container()
from detect.data import Data

data = Data(container=container)
print "loadeding! ****************"
data.generate()
data.load()

from detect.data import alias_data
from detect.views import mod_detect
mod_detect.test  = "lkjhgfhj"
app.register_blueprint(mod_detect)
