#!/usr/bin/env python3

import os
import sys
import subprocess
import smtplib
from email.message import EmailMessage
import gnupg

# try to check if remote machine is online
remote_ip = 192.168.1.2
ping_failed = os.system('ping -c 1 ' + remote_ip)

if ping_failed:

    # update system if remote machine powered off
    try:
        output = subprocess.check_output('pacman -Syu --noconfirm', shell=True, text=True, stderr=subprocess.STDOUT)
        update_succeed = True
    except subprocess.CalledProcessError as err:
        output = err.output
        update_succeed = False


    # read password from encrypted file
    home_dir = '/root'  # root user home directory without ending slash
    gpg = gnupg.GPG(gnupghome=home_dir+'/.gnupg')
    with open(home_dir+'/.smtp-password.gpg', 'rb') as _file:
        decrypted_data = gpg.decrypt_file(_file)
        password = str(decrypted_data)

    # send e-mail, using Gmail for example
    sender = account = 'username@gmail.com' # your Gmail account
    receiver = 'receiver@domain.com' # you can use the same address to send to yourself
    subject = 'Arch Linux update'
    content = output
    with smtplib.SMTP('smtp.gmail.com', port=587) as server:
        server.starttls()
        server.login(account, password)
        msg = EmailMessage()
        msg.set_content(content)
        msg['Subject'] = subject
        msg['From'] = sender
        msg['To'] = receiver
        server.send_message(msg)

    # reboot after successful update
    if update_succeed:
        os.system('reboot')
        sys.exit(0)
    else:
        sys.exit(0)

else:
    sys.exit(1)

