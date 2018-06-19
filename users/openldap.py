from openldap.api import user_api
from users.models import Profile


def reset_scw_password(request):
    """
    Reset a user's SCW account password.

    Args:
        request (django.http.request.HttpRequest): Django HTTP request - required
    """
    try:
        # Ensure password fields match.
        password = request.POST.get("password")
        password_confirm = request.POST.get("password_confirm")
        if password != password_confirm:
            raise ValidationError()

        # Ensure password complies with OpenLDAP password policy.
        pattern = re.compile("^(?=.*\d)(?=.*[a-z])(?=.*[A-Z]).{8,}")
        if not pattern.match(password):
            raise ValidationError()

        # Submit an OpenLDAP password reset request.
        user_api.reset_user_password.delay(user=request.user, password=password)

        message = _('Successfully submitted a password reset request. You should receive a '
                    'confirmation email once the request has been processed.')
        return JsonResponse(
            status=200,
            data={'data': message},
        )
    except Exception as e:
        return JsonResponse(status=400)


def update_user_openldap_account(profile):
    """
    Ensure account status updates are propogated to the user's Open LDAP account.
    """
    if profile.account_status == Profile.APPROVED:
        if profile.scw_username:
            user_api.activate_user_account.delay(user=profile.user)
        else:
            user_api.create_user.delay(user=profile.user)
    else:
        user_api.deactivate_user_account.delay(user=profile.user)
