from werkzeug.serving import run_simple
from app import app as application

import sys

reload(sys)
sys.setdefaultencoding('utf-8')


if __name__ == "__main__":
	run_simple('0.0.0.0', 8000, application, use_reloader=True, use_debugger=True, threaded=True)
