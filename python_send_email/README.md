# A Python script to send email message

My scientific calculation may take hours on cluster, and I want it to send me an email when it finished.

To avoid saving the password in plain text inside script, we need to create an encrypted file.

## [GnuPG setup](https://wiki.archlinux.org/title/GnuPG#Usage)
- If you do not have gpg key for your user, generate a key pair 
  ```
  gpg --gen-key
  ```
  following [this](https://wiki.archlinux.org/title/GnuPG#Create_a_key_pair) guidance.

  - To check whether you have set up secret key before, use 
    ```
    gpg --list-secret-keys
    ```
    this command.


## [Encrypt e-mail password](https://wiki.archlinux.org/title/Msmtp#GnuPG)
- Create a directory with `700` permission on [tmpfs](https://wiki.archlinux.org/title/Tmpfs) to avoid writing the unencrypted password to the disk.
  On the linux distrobution using `systemd`, `/tmp` is a `tmpfs` directory.
  ```
  mkdir /tmp/my_dir
  chmod -R 700 /tmp/my_dir
  ```
- Then put your password in a plain text file `/tmp/my_dir/my_password` 
  - For personal Gmail account, create an [app password].
- Encrypt it with
  ```
  gpg --default-recipient-self -e /tmp/my_dir/my_password
  ```
- Remove the plain text file and move the encrypted file to `~/.smtp-password.gpg`.
  ```
  mv /tmp/my_dir/my_passwd.gpg ~/.smtp-password.gpg
  rm -r /tmp/my_dir
  ```

## Send e-mail using python script
  Install system package for Arch Linux
  ```
  pacman -S python-gnupg
  ```
  For `anaconda`/`miniconda` environment,
  ```
  conda install -c conda-forge python-gnupg 
  ```
  ```python
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
  ```
