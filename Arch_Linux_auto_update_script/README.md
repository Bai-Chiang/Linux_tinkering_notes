# Arch Linux auto-update script

Auto update system when remote machine is offline.
For example, my NAS running Arch Linux, and I want updates only when my destop is offline.
It will then send the update result to my email.

Make sure you have a roll back solution (like [snap-pac](https://github.com/wesbarnett/snap-pac)). 

USE AT YOUR OWN RISK.

___

## E-mail set up
- Set up e-mail following [this](https://github.com/Bai-Chiang/Linux_tinkering_notes/tree/main/python_send_email) guide.

## Script and scheduling
- Download/Copy [`auto-update.py`](https://github.com/Bai-Chiang/Linux_tinkering_notes/blob/main/Arch_Linux_auto_update_script/auto-update.py) to `/usr/local/bin/`.
  Then make it executable 
  ```
  chmod 755 /usr/local/bin/auto-update.py
  ```.
  Change email address and some other variables in the script. 

- Create a systemd unit `/etc/systemd/system/auto-update.service`.
  The following unit file restart service every 5 minutes if it fails, maximum 5 retries.
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
- Create a timer unit `/etc/systemd/system/auto-update.timer`
  ```
  [Unit]
  Description=Schedule auto-update
  
  [Timer]
  OnCalendar=*-*-* 00:00:00
  
  [Install]
  WantedBy=timers.target
  ```
- enabling timer
  ```
  systemctl enable auto-update.timer
  ```
