from django import template
# from ..models import User, ChatMessage
from django.db.models import Q
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
# from civil_dashboard.models import Civil_ChatMessage, Civil_CallRecording
# from account.models import Custom_User 

register = template.Library()

@register.simple_tag()
def otp_mail(user, otp, subject, status):
        message = render_to_string('otp_email.txt', {
            'user': user,
            'otp': otp,
            'status': status,
        })
        subject = subject
        from_email = settings.EMAIL_HOST_USER
        recipient_list = [user.email]
        send_mail(subject, message, from_email, recipient_list)


def admin_login_url_mail(user, url, subject, status):
        message = render_to_string('admin_login_url_mail.txt', {
            'user': user,
            'url': url,
            'status': status,
        })
        subject = subject
        from_email = settings.EMAIL_HOST_USER
        recipient_list = [user.email]
        send_mail(subject, message, from_email, recipient_list)
         
        

# @register.simple_tag()
# def chat_is_read_status(username, model):
#     user = Custom_User.objects.get(username=username)
#     result = model.objects.filter(receiver=user, is_read=False).count()
#     return result 
  

# @register.simple_tag()
# def chat_is_read_status2(receiver_username, sender_username):
#     receiver = Custom_User.objects.get(username=receiver_username)
#     sender = Custom_User.objects.get(username=sender_username)
#     result = Civil_ChatMessage.objects.filter(receiver=receiver, sender=sender, is_read=False).count()
#     return result         