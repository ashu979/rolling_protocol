from waitress import serve
from myproject.wsgi import application

serve(application, host='0.0.0.0', port=8000)
