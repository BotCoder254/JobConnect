from flask_mail import Message
from flask import url_for
from app import mail

def send_email(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    mail.send(msg)

def send_password_reset_email(user):
    token = user.get_reset_password_token()
    send_email('[Job Board] Reset Your Password',
               sender='noreply@jobboard.com',
               recipients=[user.email],
               text_body=f'''To reset your password, visit the following link:
{url_for('auth.reset_password', token=token, _external=True)}
If you did not request a password reset, simply ignore this message.
''',
               html_body=f'''
<p>To reset your password, visit the following link:</p>
<p><a href="{url_for('auth.reset_password', token=token, _external=True)}">Click here to reset your password</a></p>
<p>If you did not request a password reset, simply ignore this message.</p>
''')
