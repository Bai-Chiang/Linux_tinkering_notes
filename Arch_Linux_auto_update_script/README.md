# Arch Linux auto-update script

Auto update system when remote machine is offline.
For example, my NAS running Arch Linux, and I want updates only when my destop is offline.
It will then send the update result to my email.

Make sure you have a roll back solution (like [snap-pac](https://github.com/wesbarnett/snap-pac)). 

USE AT YOUR OWN RISK.


## [E-mail password setup](https://wiki.archlinux.org/title/Msmtp#GnuPG)
- To avoid saving the password in plain text, first create a directory with `700` permission on [tmpfs](https://wiki.archlinux.org/title/Tmpfs).
  On the linux distrobution using `systemd`, `/tmp` is a `tmpfs` directory.
  ```
  mkdir /tmp/my_dir
  chmod 700 /tmp/my_dir
  ```
- Then create a plain text file `/tmp/my_dir/my_password` conatins your password.
- Encrypt it with
  ```
  gpg --default-recipient-self -e /tmp/my_dir/my_password
  ```
- Remove the plain text file and move the encrypted file to `/path/to/.msmtp-password.gpg`.
  ```
  mv /tmp/my_dir/my_passwd.gpg /root/.msmtp-password.gpg
  rm -r /tmp/my_dir
  ```

## Script and scheduling
1. Download `auto-update.py` to `/usr/local/bin/`. Then make it executable `chmod 755 /usr/local/bin/auto-update.py`. Change email address and some other variables in the script. If using Gmail setup [App Password](https://myaccount.google.com/apppasswords).

2. Create a systemd unit `/etc/systemd/system/auto-update.service`. The following unit file restart service every 5 minutes if it fails, maximum 5 retries.
```
[Unit]
Description=Auto-update
StartLimitIntervalSec=30min
StartLimitBurst=5

[Service]
Type=oneshot
ExecStart=/usr/bin/python3 /usr/local/bin/auto-update.py
Restart=on-failure
RestartSec=15min

[Install]
WantedBy=multi-user.target
```
3. Create a timer unit `/etc/systemd/system/auto-update.timer`
```
[Unit]
Description=Schedule auto-update

[Timer]
OnCalendar=*-*-* 00:00:00

[Install]
WantedBy=timers.target
```
4. enabling timer
```
systemctl enable auto-update.timer
```
