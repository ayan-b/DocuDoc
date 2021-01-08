def login_drchrono(request):
    CLIENT_ID = 'HgEutH1AWHjLw1RaXz8hTZRhBq1bFkjGLF5tJ37s'
    CLIENT_SECRET = '036DIWSCaoWCNoRmRosWgIDKmczjKjoDRY5KTOtqPSsYaqNfz9fxGKkjPnR1c3d91F5GbomMFLFCe6zDdH9s9oGlK3p0tjsYqqHTqcFljiX1o9lG50w55aVpPKH9OM1A'
    REDIRECT_URI_ENCODED = 'http://localhost:3001/drchrono-redir'
    SCOPES_ENCODED = ' '.join([
        'user:read',
        'user:write',
        'patients:summary:read',
        'patients:summary:write',
        'calendar:read',
        'calendar:write',
        'clinical:read',
        'clinical:write',
    ])
    dr_chrono_url = f"https://drchrono.com/o/authorize/?redirect_uri={REDIRECT_URI_ENCODED}&response_type=code&client_id={CLIENT_ID}&scope={SCOPES_ENCODED}"
    return redirect(dr_chrono_url)


def handle_drchrono(request):
    CLIENT_ID = 'HgEutH1AWHjLw1RaXz8hTZRhBq1bFkjGLF5tJ37s'
    CLIENT_SECRET = '036DIWSCaoWCNoRmRosWgIDKmczjKjoDRY5KTOtqPSsYaqNfz9fxGKkjPnR1c3d91F5GbomMFLFCe6zDdH9s9oGlK3p0tjsYqqHTqcFljiX1o9lG50w55aVpPKH9OM1A'

    if 'error' in request.GET:
        raise ValueError('Error authorizing application: %s' % request.GET['error'])

    response = requests.post('https://drchrono.com/o/token/', data={
        'code': request.GET['code'],
        'grant_type': 'authorization_code',
        'redirect_uri': 'http://localhost:3001/drchrono-redir',
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
    })
    # response.raise_for_status()
    data = response.json()

    # Save these in your database associated with the user
    access_token = data['access_token']
    refresh_token = data['refresh_token']
    expires_timestamp = datetime.datetime.now(pytz.utc) + datetime.timedelta(seconds=data['expires_in'])

    response = requests.get('https://app.drchrono.com/api/users/current', headers={
        'Authorization': 'Bearer %s' % access_token,
    })
    current_user = response.json()
    response = requests.get('https://app.drchrono.com/api/doctors', headers={
        'Authorization': 'Bearer %s' % access_token,
    })
    first_user = (response.json())['results'][0]
    # create user
    new_user = User(
        username=current_user['username'],
        email=first_user['email'],
        first_name=first_user['first_name'],
        last_name=first_user['last_name'],
        mobile_no=first_user['office_phone'],
        emergency_mobile=first_user['cell_phone'],
        address=first_user['country'],
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=expires_timestamp,
    )
    new_user.save()
    return index_view(request)

