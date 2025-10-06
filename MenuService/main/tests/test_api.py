from datetime import date
import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from main.models import Employee

@pytest.fixture
def client():
    return APIClient()

@pytest.fixture
def staff_user(db):
    u = User.objects.create_user(username='admin', password='adminpass', is_staff=True)
    Employee.objects.create(user=u)
    return u

@pytest.fixture
def user(db):
    u = User.objects.create_user(username='alice', password='password123')
    Employee.objects.create(user=u)
    return u

def auth(client, username, password, build=210):
    r = client.post('/api/auth/token/', {'username': username, 'password': password}, format='json')
    token = r.data['access']
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}', HTTP_X_APP_BUILD=str(build))
    return client

def test_menu_flow(db, client, staff_user, user):
    staff = auth(client, 'admin', 'adminpass')
    r = staff.post('/restaurants/', {'name': 'Cafe Roma'}, format='json')
    rid = r.data['id']
    m = staff.post('/menu/', {'restaurant_id': rid, 'date': str(date.today()), 'items': [{'name':'Soup'}]}, format='json')
    mid = m.data['id']

    alice = APIClient()
    auth(alice, 'alice', 'password123')
    t = alice.get('/menu/today/')
    assert t.status_code == 200 and len(t.data) >= 1

    v = alice.post(f'/menu/{mid}/vote/', {}, format='json')
    assert v.status_code == 201

    v2 = alice.post(f'/menu/{mid}/vote/', {}, format='json')
    assert v2.status_code == 400