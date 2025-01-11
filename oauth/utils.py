from django.db import transaction
from user.models import User

@transaction.atomic
def social_user_create(github_id, github_username, email,access_token, profile_image=None ):
    """
    GitHub OAuth를 통해 받은 정보를 바탕으로 User를 생성
    """
    user = User(
        github_id=github_id,
        github_username=github_username,
        email=email,
        profile_image=profile_image,
        access_token=access_token
    )

    user.full_clean()
    user.save()
    return user


@transaction.atomic
def social_user_get_or_create(github_id, github_username, email, access_token, profile_image=None):
    """
    GitHub ID를 기준으로 User를 가져오거나 새로 생성합니다.
    """
    user = User.objects.filter(github_id=github_id).first()

    if user:
        return user, False

    return social_user_create(
        github_id=github_id,
        github_username=github_username,
        email=email,
        profile_image=profile_image,
        access_token=access_token
    ), True
