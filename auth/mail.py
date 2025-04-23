import smtplib
from email.message import EmailMessage

HOST = "smtp.gmail.com"
PORT = 465

username = 'gauravsh839@gmail.com'
sender = username

def signup_mail():
    reciever_mail = input('enter you gmail account : ')

    To = [reciever_mail]
    CC = [reciever_mail]
    subject = "thefarmguy login"
    body = "\n you have successfully signed up \n Now you can change you password or you can logout . \n Thanks"

    reciever = To + CC

    message = EmailMessage()
    message["from"] = sender
    message["to"] = ''.join(To)
    message["CC"] = ''.join(CC)
    message["subject"] = subject
    message.set_content(body)

    with (smtplib.SMTP_SSL(HOST, PORT)) as server:
        server.login(username, 'zgxgzjvysnpuqzlg')
        server.send_message(message, sender, reciever)
        print('message sent')
    
def reset_mail():
    reciever_mail = input('enter you gmail account : ')

    To = [reciever_mail]
    CC = [reciever_mail]
    subject = "thefarmguy login"
    body = "\n password changed. \n Thanks"

    reciever = To + CC

    message = EmailMessage()
    message["from"] = sender
    message["to"] = ''.join(To)
    message["CC"] = ''.join(CC)
    message["subject"] = subject
    message.set_content(body)

    with (smtplib.SMTP_SSL(HOST, PORT)) as server:
        server.login(username, 'zgxgzjvysnpuqzlg')
        server.send_message(message, sender, reciever)
        print('message sent')    