import unicodedata
from uuid import uuid4

from django.contrib.auth.models import update_last_login
from mozilla_django_oidc.auth import OIDCAuthenticationBackend

from portal.apps.profiles.models import AerpawUserProfile


def generate_username(email):
    # Using Python 3 and Django 1.11+, usernames can contain alphanumeric
    # (ascii and unicode), _, @, +, . and - characters. So we normalize
    # it and slice at 150 characters.
    return unicodedata.normalize('NFKC', email)[:150]


class MyOIDCAB(OIDCAuthenticationBackend):
    def create_user(self, claims):
        user = super(MyOIDCAB, self).create_user(claims)
        user.created_by = claims.get('email', '')
        user.display_name = claims.get('given_name', '') + ' ' + claims.get('family_name', '')
        user.first_name = claims.get('given_name', '')
        user.last_name = claims.get('family_name', '')
        user.modified_by = claims.get('email', '')
        user.openid_sub = claims.get('sub', '')
        user.profile = AerpawUserProfile.objects.create(
            created_by=claims.get('email', ''),
            modified_by=claims.get('email', ''),
            uuid=str(uuid4())
        )
        user.uuid = str(uuid4())
        user.save()

        return user

    def update_user(self, user, claims):
        user.first_name = claims.get('given_name', '')
        user.last_name = claims.get('family_name', '')
        update_last_login(None, user)
        user.save()

        return user
