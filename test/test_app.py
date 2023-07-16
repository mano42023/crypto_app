from app.app import app 
import json
headers = {'Authorization': ''}
market = '1PECO-BTC'

def test_auth():
    response = app.test_client().post('/api/get_token', json={'username':'user1',  'password':'user1'})
    res = json.loads(response.text)
    headers['Authorization'] = res['token']
    assert response.status_code == 200

def test_all_summmaries():
    response = app.test_client().get('/api/get_all_summaries', headers=headers)
    assert response.status_code == 200

def test_summary():
    response = app.test_client().get('/api/get_summary?market=', headers=headers)
    assert response.status_code == 200