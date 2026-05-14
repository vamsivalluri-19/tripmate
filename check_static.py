import urllib.request
import sys
url='http://127.0.0.1:8000/static/css/style.css'
try:
    r=urllib.request.urlopen(url, timeout=10)
    code = r.getcode()
    data = r.read(300).decode('utf-8')
    print('STATUS', code)
    print('PREVIEW:')
    print(data)
except Exception as e:
    print('ERROR', e)
    sys.exit(1)
