from django.contrib.auth.tokens import PasswordResetTokenGenerator
import six
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.contrib.auth.tokens import default_token_generator

class EmailVerificationTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, member, timestamp):
        return f"{member.pk}{timestamp}{member.is_verified}"

email_verification_token = EmailVerificationTokenGenerator()

def send_verification_email(request, user):
    mail_subject = 'Activate your TBIDO account'
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    domain = get_current_site(request).domain
    link = f"http://{domain}/verify-email/{uid}/{token}/"

    message = render_to_string('verify_email.html', {
        'user': user,
        'domain': domain,
        'uid': uid,
        'token': token,
        'link': link,
    })

    email = EmailMessage(mail_subject, message, to=[user.email])
    email.send()