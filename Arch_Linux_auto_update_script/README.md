# Arch Linux auto-update script

Auto update system when remote machine is offline.
For example, a NAS runs Arch Linux and it share file through NFS to a workstation.
Therefore if the NAS finds out the workstation is online, then it postpone updates, untill the workstation is powered off.
After the update, the NAS will send the update result (all termial outputs) to my email, so that I could check whether the update succeeded.

Arch Linux does not recommend unattend upgrade, see [this](https://wiki.archlinux.org/title/System_maintenance#Act_on_alerts_during_an_upgrade).

USE AT YOUR OWN RISK.
And make sure you have a roll back solution (like [snap-pac](https://github.com/wesbarnett/snap-pac)), or backup.


___

## E-mail set up
- Set up e-mail for root user
  ```
  sudo -i
  ```
  Then following [this](https://github.com/Bai-Chiang/Linux_tinkering_notes/tree/main/python_send_email) guide.

## Script and scheduling
- Download/Copy [`auto-update.py`](https://github.com/Bai-Chiang/Linux_tinkering_notes/blob/main/Arch_Linux_auto_update_script/auto-update.py) to `/usr/local/bin/`.
  Then make it executable 
  ```
  chmod 755 /usr/local/bin/auto-update.py
  ```.
  Read and change email address and some other variables in the script. 

- Create a systemd unit `/etc/systemd/system/auto-update.service`.
  The following unit file restart service every 15 minutes if it fails, maximum 5 retries.
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
