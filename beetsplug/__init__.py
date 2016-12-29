from pkgutil import extend_path
from beets import config
__path__ = extend_path(__path__, __name__)

try:
    PORT = config['web_tagger']['port'].as_number()
except:
    PORT = 8000
