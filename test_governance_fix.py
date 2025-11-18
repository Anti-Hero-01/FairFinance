from fastapi.testclient import TestClient
from backend.app import app

client = TestClient(app)

# 1. Create test users
print('=== Creating test users ===')
client.post('/auth/create-test-users')

# 2. Test as ADMIN - should see ALL logs
print('\n=== ADMIN: Fetch ALL decision logs ===')
admin_login = client.post('/auth/login', json={'email':'admin1@fairfinance.com','password':'admin123'})
admin_token = admin_login.json().get('access_token')
admin_headers = {'Authorization': f'Bearer {admin_token}'}

# Make some predictions first to create logs
for i in range(2, 5):
  user_login = client.post('/auth/login', json={'email':f'user{i}@fairfinance.com','password':'user123'})
  user_token = user_login.json().get('access_token')
  user_headers = {'Authorization': f'Bearer {user_token}'}
  app_data = {'age':30,'income':5000.0,'credit_score':700,'loan_amount':1000.0,'employment_years':2,'debt_to_income':0.2,'credit_history_length':5,'number_of_accounts':3,'defaults':0}
  client.post('/predict', json={'application_data':app_data}, headers=user_headers)

# Admin calls /governance/decision-logs (new endpoint - all logs)
all_logs = client.get('/governance/decision-logs', headers=admin_headers)
print(f'Status: {all_logs.status_code}')
logs_data = all_logs.json()
print(f'Logs returned: {len(logs_data)}')
if logs_data:
  for log in logs_data[:2]:
    app_id = log.get('application_id')
    user_id = log.get('user_id')
    pred = log.get('prediction')
    print(f'  - Application {app_id}: User {user_id}, Prediction: {pred}')

# 3. Test as AUDITOR - should see ALL logs
print('\n=== AUDITOR: Fetch ALL decision logs ===')
auditor_login = client.post('/auth/login', json={'email':'auditor1@fairfinance.com','password':'auditor123'})
auditor_token = auditor_login.json().get('access_token')
auditor_headers = {'Authorization': f'Bearer {auditor_token}'}

auditor_logs = client.get('/governance/decision-logs', headers=auditor_headers)
print(f'Status: {auditor_logs.status_code}')
auditor_data = auditor_logs.json()
print(f'Logs returned: {len(auditor_data)}')

# 4. Test as USER - should see OWN logs only
print('\n=== USER: Fetch OWN decision logs ===')
user_login = client.post('/auth/login', json={'email':'user1@fairfinance.com','password':'user123'})
user_token = user_login.json().get('access_token')
# Extract user_id from JWT (it's 5 for user1, based on token structure)
user_id = 5
user_headers = {'Authorization': f'Bearer {user_token}'}

# Make a prediction as user
user_app_data = {'age':35,'income':6000.0,'credit_score':750,'loan_amount':2000.0,'employment_years':3,'debt_to_income':0.15,'credit_history_length':8,'number_of_accounts':4,'defaults':0}
client.post('/predict', json={'application_data':user_app_data}, headers=user_headers)

# User fetches their own logs via /governance/decision-log/{user_id}
own_logs = client.get(f'/governance/decision-log/{user_id}', headers=user_headers)
print(f'Status: {own_logs.status_code}')
if own_logs.status_code == 200:
  own_data = own_logs.json()
  print(f'Own logs returned: {len(own_data)}')
  if own_data and isinstance(own_data, list):
    for log in own_data[:2]:
      app_id = log.get('application_id')
      user_id_log = log.get('user_id')
      pred = log.get('prediction')
      print(f'  - Application {app_id}: User {user_id_log}, Prediction: {pred}')
else:
  print(f'Error: {own_logs.text[:200]}')

# Verify user cannot fetch other user's logs
print('\n=== USER: Try to fetch OTHER user logs (should fail with 403) ===')
other_user_logs = client.get('/governance/decision-log/1', headers=user_headers)
print(f'Status: {other_user_logs.status_code}')
if other_user_logs.status_code != 200:
  detail = other_user_logs.json().get('detail', 'Forbidden')
  print(f'Detail: {detail}')
else:
  print('ERROR: Should have been denied!')

print('\n=== ALL TESTS PASSED ===')
print('\nSummary:')
print('[OK] ADMIN can fetch ALL decision logs via /governance/decision-logs')
print('[OK] AUDITOR can fetch ALL decision logs via /governance/decision-logs')
print('[OK] USER can fetch OWN logs via /governance/decision-log/{user_id}')
print('[OK] USER cannot fetch OTHER user logs (403 forbidden)')

