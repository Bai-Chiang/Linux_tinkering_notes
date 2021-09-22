#!/usr/bin/env python

import os
import sys
import subprocess
import smtplib
from email.message import EmailMessage
import gnupg

# try to check if remote machine is online
ping_failed = os.system('ping -c 1 192.168.1.2')

if ping_failed:

    # update system if remote machine powered off
    try:
        output = subprocess.check_output('pacman -Syu --noconfirm', shell=True, text=True)
        update_succeed = True
    except subprocess.CalledProcessError as err:
        output =  err
        update_succeed = False


    # send an e-mail of update result
    account = 'send@domain.com'
    # read password from encrypted file
    gpg = gnupg.GPG(gnupghome='/path/to/gnupghome')
    with open('/path/to/.msmtp-password.gpg', 'rb') as _file:
        decrypted_data = gpg.decrypt_file(_file)
        password = str(decrypted_data)
    # send e-mail
    with smtplib.SMTP('smtp.domain.com', port=587) as server:
        server.starttls()
        server.login(account, password)
        msg = EmailMessage()
        msg.set_content(output)
        msg['Subject'] = 'Arch Linux update'
        msg['From'] = account
        msg['To'] = 'receive@domain.com'
        server.send_message(msg)

    # reboot after successful update
    if update_succeed:
        os.system('reboot')
        sys.exit(0)
    else:
        sys.exit(0)

else:
    sys.exit(1)

