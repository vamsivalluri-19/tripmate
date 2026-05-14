import os
import sys
from django.contrib.auth import get_user_model

repo_root = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.join(repo_root, 'TripMate-main', 'backend')
sys.path.insert(0, backend_dir)
os.environ.setdefault('DJANGO_SETTINGS_MODULE','tourAndTravel.settings')
import django
django.setup()
from django.test import Client

User = get_user_model()
user, _ = User.objects.get_or_create(username='smoke_test_package')

c = Client()
if user.password != '':
    user.set_unusable_password()
    user.save(update_fields=['password'])
c.force_login(user)
resp = c.post('/package/', {'source':'guntur','destination':'Vadodara','date':'2026-05-09'}, HTTP_HOST='127.0.0.1')
print('STATUS', resp.status_code)
print('URL', resp.request.get('PATH_INFO'))
content = resp.content.decode('utf-8')
if 'list index out of range' in content or 'IndexError' in content:
    print('SERVER ERROR: IndexError in response')
else:
    print('RESPONSE LENGTH', len(content))
    if 'FLIGHTS' in content.upper():
        print('FLIGHTS section present')
    if 'HOTELS' in content.upper():
        print('HOTELS section present')
    if 'NO RESULTS' in content.upper():
        print('NO RESULTS')
