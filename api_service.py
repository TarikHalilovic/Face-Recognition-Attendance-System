import requests
from requests.auth import HTTPBasicAuth
from Model.ActionResponse import ActionResponse


def post_action(userId, buttonId, serverUrl, token):
    ar = ActionResponse(True, False, 0, None, None, None)
    try:
        response = requests.post(
            url=f'{serverUrl}/api/attendance/insert',
            json={'personnelId': userId, 'buttonId': buttonId},
            headers={
                'Content-Type': 'application/json',
                'Authorization': token
            },
            timeout=8
        )
        # serverError, isSuccessful, statusCode, message, fullName, errorCode
        # ar = ActionResponse(True, False, response.status_code, None, None, None)
        ar.statusCode = response.status_code
        if response.status_code != 200:
            print(f'[ERROR] Server error. Status code -> {response.status_code}')
        else:
            data = response.json()
            ar.serverError = False
            ar.isSuccessful = data["isSuccessful"]
            ar.message = data["message"]
            ar.fullName = data["fullName"]
            ar.messageCode = data["messageCode"]
    except:
        print('[ERROR] Api request timed out.')
    finally:
        return ar


def add_person_to_external_system(firstName, lastName, serverUrl, token):
    try:
        response = requests.post(url=f'{serverUrl}/api/personnel',
                                 json={'firstName': firstName, 'lastName': lastName},
                                 headers={
                                    'Content-Type': 'application/json',
                                    'Authorization': token
                                },
                                 timeout=3.5
                                )
        if response.status_code != 201:
            print(f'[ERROR] Server error. Status code -> {response.status_code}')
            print('[ERROR] Person has not been added to external database.')
            return 0
        else:
            print('[INFO] Person added to external server database.')
            return int(response.json()["id"])
    except:
        print('[ERROR] Api request timed out.')
        raise Exception('Request timed out exception')


def get_token(serverUrl, username, password):
    try:
        response = requests.get(url=f'{serverUrl}/api/account/login',
                                json={'username': username, 'passwordHash': password},
                                timeout=3.5
                                )
        if response.status_code == 200:
            print(f'[INFO] Successfully authenticated with server.')
            return response.text
        elif response.status_code == 403:
            print(f'[ERROR] Wrong username/password, can not connect to server. Status code -> {response.status_code}')
        else:
            print(f'[ERROR] Server error. Not connected to server. Status code -> {response.status_code}')
        return None
    except:
        print('[ERROR] Server error. Not connected to server. API timeout.')
        return None


def server_connection_test(serverUrl, token):
    try:
        response = requests.get(url=f'{serverUrl}/api/account/validate-login',
                                 headers={'Authorization': token},
                                 timeout=3.5
                                 )
        if response.status_code != 200:
            print(f'[ERROR] Server error. Not connected to server. Status code -> {response.status_code}')
        else:
            print('[INFO] Connection with server established successfully.')
    except:
        print('[ERROR] Server error. Not connected to server.')
    
