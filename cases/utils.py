from social_django.models import UserSocialAuth

GROUP_TO_IDX = {
    1: 'patient',
    2: 'hospital',
    3: 'pharmacy',
    4: 'diagnosis_center',
}


def get_group(user):
    for idx, group in GROUP_TO_IDX.items():
        if user.groups.filter(name=group).exists():
            return idx
    return None


def get_token():
    """
    Social Auth module is configured to store our access tokens. This dark magic will fetch it for us if we've
    already signed in.
    """
    oauth_provider = UserSocialAuth.objects.get(provider='drchrono')
    access_token = oauth_provider.extra_data['access_token']
    return access_token
