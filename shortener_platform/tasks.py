from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from shortener_platform.models import Link
from urlshortener.celery import app

@app.task
def check_expired_urls():
    current_time = timezone.now()

    links = Link.objects.all()
    for link in links:
        if link.expires_at > current_time:
            send_link_expiry_email_to_user.delay(link.owner.email, link.owner.get_full_name(), link.url, link.alt_url, link.expired_at)
        else:
            pass


@app.task
def send_link_expiry_email_to_user(email, owner_name, url, short_url, expired_at):
    try:
        message = f"""
        Hello {owner_name},
        The link {url} => {short_url} has expired at {expired_at}
        
        Regards
        URL Shortener Platform
        """
        try:
            send_mail('Link Expiry Notification', message=message, from_email='sexwitmeigot@gmail.com', recipient_list=[email], fail_silently=False)
        except Exception as e:
            print("Exception", e)
            pass
    except ObjectDoesNotExist as e:
        print("Exception", e)


@app.task
def send_password_reset_email(user_id):
    try:
        user_model = get_user_model()
        user = user_model.objects.get(pk=user_id)
        verification_identifier = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        user.token = token
        user.identifier = verification_identifier
        user.save()

        c = dict(
            uid=verification_identifier,
            token=token,
            domain='http://127.0.0.1:8000',
            site_name='URL Shortener Platform',
            user=user,
            protocol='http'
        )

        email_template_name = 'emails/email_verification.html'
        email = render_to_string(email_template_name, c)
        try:
            send_mail('Email Verification', message='message', from_email='joseph@speki.co.tz', recipient_list=[user.email], fail_silently=False, html_message=email,)
        except Exception as e:
            print("Exception", e)
            pass
    except ObjectDoesNotExist as e:
        print("Exception", e)
