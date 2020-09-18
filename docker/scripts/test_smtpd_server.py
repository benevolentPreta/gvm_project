#!/usr/bin/env python3

# the first step is always the same: import all necessary components:
import smtplib
import os
from socket import gaierror


# now you can play with your code. Let’s define the SMTP server separately here:
port = 2525 
smtp_server = os.environ['SMTP_DOMAIN'] # set in .env file
login = os.environ['SMTP_USER'] # set in .env file
password = os.environ['SMTP_PASS'] # set in .env file

# specify the sender’s and receiver’s email addresses
sender = "from@example.com"
receiver = "mailtrap@example.com"

# type your message: use two newlines (\n) to separate the subject from the message body, and use 'f' to  automatically insert variables in the text
message = f"""\
Subject: Hi Mailtrap
To: {receiver}
From: {sender}

Testing smtp mail server."""

try:
    #send your message with credentials specified above
    with smtplib.SMTP(smtp_server, port) as server:
        server.login(login, password)
        server.sendmail(sender, receiver, message)

    # tell the script to report if your message was sent or which errors need to be fixed 
    print('Sent')
except (gaierror, ConnectionRefusedError):
    print('Failed to connect to the server. Bad connection settings?')
except smtplib.SMTPServerDisconnected:
    print('Failed to connect to the server. Wrong user/password?')
except smtplib.SMTPException as e:
    print('SMTP error occurred: ' + str(e))