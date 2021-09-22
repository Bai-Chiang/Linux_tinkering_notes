# A Python script to send email message

My scientific calculation may take hours on cluster, and I want it to send me an email when it finished.
For example:
```
nohup bash -c "run_calculation_command; python ~/send_email.py" > ~/stdout 2>&1 &
```
After ending `run_calculation_command` it will send me an email notification.

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
  Copy/Download [`send_email.py`](https://github.com/Bai-Qiang/Linux_tinkering_notes/blob/9c4b855abfdb8334fe2512330309affcfa375b5e/python_send_email/send_email.py)
  Change `home_dir` `sender` `receiver` `subject` `content` variable,
  and its permission if you don't want other user find your email address
  ```
  chmod 700 send_email.py
  ```
