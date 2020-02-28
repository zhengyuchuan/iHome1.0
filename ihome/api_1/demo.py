from . import api
from ihome import models

@api.route('/')
def hello_world():
    return 'Hello World!'