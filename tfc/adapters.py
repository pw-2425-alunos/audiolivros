from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.exceptions import ImmediateHttpResponse
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth import get_user_model

User = get_user_model()

class NoNewSocialAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        # Se já está autenticado, nada a fazer
        if request.user.is_authenticated:
            return

        # Se o email não existe, bloqueia
        email = sociallogin.user.email
        if not email:
            return

        try:
            existing_user = User.objects.get(email=email)
            sociallogin.connect(request, existing_user)  # associa a conta Google
        except User.DoesNotExist:
            messages.error(
                request,
                "Este email não está registado. Por favor crie uma conta primeiro."
            )
            raise ImmediateHttpResponse(redirect("account_login"))
