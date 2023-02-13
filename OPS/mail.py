import smtplib
import ssl
from email.message import EmailMessage
from flask import Response, request
from flask_restful import Resource
import mongoengine
from OPS.auth import *


def MailToAdmins(group_name, content):
    group = group_db.objects.get(group_name=group_name)
    email_sender = 'nknj.parmar26@gmail.com'
    email_password = 'treyiojpgwjhqesg'
    email_receiver = set(group["admin"] + group["moderator"])
    emails = []
    for name in email_receiver:
        user = user_db.objects.get(user_name=name)
        emails.append(user["email"])
    for receiver in emails:
        subject = 'Hi {}!! Check out the activity of your group' \
                  ' : {}'.format(list(email_receiver)[i], group_name)
        em = EmailMessage()
        em['From'] = email_sender
        em['To'] = receiver
        em['Subject'] = subject
        em.set_content(content)
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
            smtp.login(email_sender, email_password)
            smtp.sendmail(email_sender, receiver, em.as_string())
        i = i+1


def MailToUser(user_name, post_id, content):
    email_sender = 'nknj.parmar26@gmail.com'
    email_password = 'treyiojpgwjhqesg'
    user = user_db.objects.get(user_name=user_name)
    email_receiver = user["email"]
    subject = 'Post Activity : {}'.format(post_id)
    content = "Hi {}!! Check out activity on your recent " \
              "post: {}\n {}".format(user_name, post_id, content)
    em = EmailMessage()
    em['From'] = email_sender
    em['To'] = email_receiver
    em['Subject'] = subject
    em.set_content(content)
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
        smtp.login(email_sender, email_password)
        smtp.sendmail(email_sender, email_receiver, em.as_string())