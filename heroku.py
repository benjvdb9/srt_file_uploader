import os
from bottle import route, static_file, run

@route('/')
def show_def():
    return static_file('SubsMix.srt', root=('.'))

if os.environ.get('APP_LOCATION') == 'heroku':
    run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
    
else:
    run(host='localhost', port=8080)
