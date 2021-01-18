import requests
from social.backends.oauth import BaseOAuth2


# Taken from https://github.com/drchrono/api-example-django/
class drchronoOAuth2(BaseOAuth2):
    """
    drchrono OAuth authentication backend
    """

    name = 'drchrono'
    AUTHORIZATION_URL = 'https://drchrono.com/o/authorize/'
    ACCESS_TOKEN_URL = 'https://drchrono.com/o/token/'
    ACCESS_TOKEN_METHOD = 'POST'
    REDIRECT_STATE = False
    USER_DATA_URL = 'https://drchrono.com/api/users/current'
    EXTRA_DATA = [
        ('refresh_token', 'refresh_token'),
        ('expires_in', 'expires_in')
    ]
    # TODO: setup proper token refreshing

    def get_user_details(self, response):
        """
        Return user details from drchrono account
        """
        username = response.get('username')
        access_token = response.get('access_token')
        response = requests.get('https://app.drchrono.com/api/doctors', headers={
            'Authorization': 'Bearer %s' % access_token,
        })
        first_user = (response.json())['results'][0]
        # TODO add to doctors
        return({
            'username': username,
            'email': first_user['email'],
            'first_name': first_user['first_name'],
            'last_name': first_user['last_name'],
            'mobile_no': first_user['office_phone'],
            'emergency_mobile': first_user['cell_phone'],
            'address': first_user['country'],
        })

    def user_data(self, access_token, *args, **kwargs):
        """
        Load user data from the service
        """
        return self.get_json(
            self.USER_DATA_URL,
            headers=self.get_auth_header(access_token)
        )

    def get_auth_header(self, access_token):
        return {'Authorization': 'Bearer {0}'.format(access_token)}


class onpatientOAuth2(BaseOAuth2):
    """
    onpatient OAuth authentication backend
    """

    name = 'onpatient'
    ID_KEY = 'username'
    AUTHORIZATION_URL = 'https://onpatient.com/o/authorize/'
    ACCESS_TOKEN_URL = 'https://onpatient.com/o/token/'
    ACCESS_TOKEN_METHOD = 'POST'
    REDIRECT_STATE = False
    USER_DATA_URL = 'https://drchrono.com/onpatient_api/fhir/Patient'
    EXTRA_DATA = [
        ('refresh_token', 'refresh_token'),
        ('expires_in', 'expires_in')
    ]

    # TODO: setup proper token refreshing

    def get_user_details(self, response):
        """
        Return user details from onpatient account
        """
        username = response.get('username')
        access_token = response.get('access_token')
        response = requests.get('https://app.drchrono.com/api/fhir/Patient', headers={
            'Authorization': 'Bearer %s' % access_token,
        })
        print(response)
        first_user = (response.json())['results']
        # TODO add to doctors
        return ({
            'username': username,
            'gender': first_user['gender'],
            'birthdate': first_user['birthDate'],
            'first_name': first_user['name'],
            # 'email': first_user['email'],
            # 'first_name': first_user['first_name'],
            # 'last_name': first_user['last_name'],
            # 'mobile_no': first_user['office_phone'],
            # 'emergency_mobile': first_user['cell_phone'],
            # 'address': first_user['country'],
        })

    def user_data(self, access_token, *args, **kwargs):
        """
        Load user data from the service
        """
        return self.get_json(
            self.USER_DATA_URL,
            headers=self.get_auth_header(access_token)
        )

    def get_auth_header(self, access_token):
        return {'Authorization': 'Bearer {0}'.format(access_token)}
