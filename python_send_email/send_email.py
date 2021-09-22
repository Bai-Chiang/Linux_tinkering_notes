#!/usr/bin/env python3

import os
import sys
import subprocess
import smtplib
from email.message import EmailMessage
import gnupg

# read password from encrypted file
home_dir = '/home/username'  # your home directory without ending slash
gpg = gnupg.GPG(gnupghome=home_dir+'/.gnupg')
with open(home_dir+'/.smtp-password.gpg', 'rb') as _file:
    decrypted_data = gpg.decrypt_file(_file)
    password = str(decrypted_data)

# send e-mail, using Gmail for example
sender = account = 'username@gmail.com' # your Gmail account
receiver = 'receiver@domain.com' # you can use the same address to send to yourself
subject = 'Test message'
content = 'Hello world!'
with smtplib.SMTP('smtp.gmail.com', port=587) as server:
    server.starttls()
    server.login(account, password)
    msg = EmailMessage()
    msg.set_content(content)
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = receiver
    server.send_message(msg)

