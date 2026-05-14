import urllib.request
url='http://127.0.0.1:8000/'
try:
    r=urllib.request.urlopen(url, timeout=10)
    html = r.read(1000).decode('utf-8')
    print('STATUS', r.getcode())
    snippet = html.replace('\n',' ')[:500]
    print('SNIPPET:\n', snippet)
    if '{%' in html or '{{' in html:
        print('\nWARNING: Template tags detected in response (not rendered).')
except Exception as e:
    print('ERROR', e)
