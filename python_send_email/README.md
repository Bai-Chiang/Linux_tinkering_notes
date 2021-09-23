# A Python script to send email message

## [GnuPG setup](https://wiki.archlinux.org/title/GnuPG#Usage)
To avoid saving the password in plain text inside the python script, we need to create an encrypted file.

- If you do not have gpg key for your user, generate a key pair using this command
  ```
  gpg --gen-key
  ```
  then following [this](https://wiki.archlinux.org/title/GnuPG#Create_a_key_pair) guidance.

  - To check whether you have already set up secret key before, use this command.
    ```
    gpg --list-secret-keys
    ```


## [Encrypt e-mail password](https://wiki.archlinux.org/title/Msmtp#GnuPG)
- Create a directory with `700` permission on [tmpfs](https://wiki.archlinux.org/title/Tmpfs) to avoid writing the unencrypted password to the disk.
  On the linux distrobution using `systemd`, `/tmp` is a `tmpfs` directory.
  ```
  mkdir /tmp/my_dir
  chmod -R 700 /tmp/my_dir
  ```
- Then put your password in a plain text file `/tmp/my_dir/my_password` 
  - For personal Gmail account with two factor authentication enabled,
    create an [app password](https://myaccount.google.com/apppasswords).
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
- Copy/Download [`send_email.py`](https://github.com/Bai-Chiang/Linux_tinkering_notes/blob/9c4b855abfdb8334fe2512330309affcfa375b5e/python_send_email/send_email.py)
  Change `home_dir` `sender` `receiver` `subject` `content` variable,
  and its permission if you don't want other user find out your email address
  ```
  chmod 700 send_email.py
  ```
- Install necessary python packages
  - Install system package, if you have root access. For example on Arch Linux, install `python-gnupg`.
    ```
    pacman -S python-gnupg
    ```
  - If using `anaconda`/`miniconda` environment,
    install [`python-gnupg`](https://anaconda.org/conda-forge/python-gnupg) from [conda-forge](https://conda-forge.org/).
    ```
    conda install -c conda-forge python-gnupg 
    ```

## Use cases
- Scientific calculations may take hours on cluster, and I want it to send me an email when it finished.
  For example, `node0` is connect to internet,
  but the code is running on `node1` which is connected with `node0` but no internet access.
  The folllowing command will run  `run_calculation` on `node1`,
  after finishing the calculation it will send an email notification from `node0`.
  ```
  nohup bash -c "run_calculation; ssh username@node0 'python ~/send_email.py'" > ~/stdout 2>&1 &
  ```
  (need set up `ssh` [key authentication](https://wiki.archlinux.org/title/SSH_keys) so no password is needed when using `ssh`)
