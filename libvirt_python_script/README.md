# A python script to start/stop libvirt VMs

## start/stop VMs using `start_vm.py` script
- Start a VM

```
python3 start_vm.py your_vm_name
```
or
```
python3 start_vm.py your_vm_name start
```

- stop a VM
```
python3 start_vm.py your_vm_name stop
```

## Start/Stop VMs in order with systemd

### Two VMs example

For example you have two VMs, `vm1` and `vm2`. `vm1` runs pfsense (a firewall/router). `vm2` runs some other services but it needs to mount NFS (Network File System).
Both host and `vm2` network are managed by `vm1`, so we want to start `vm2` after there is network connection, such that it could mount NFS. The boot order is
> host poweron -> start `vm1` -> waiting pfsense config network -> host has network connection -> start `vm2`

1. copy `start_vm.py` to `/opt/bin/`

2. create a systemd service file `/etc/systmed/system/start_vm1.service`
```
[Unit]
Description=Start vm1
Requires=libvirtd.service
After=libvirtd.service

[Service]
Type=oneshot
RemainAfterExit=yes
ExecStart=/usr/bin/python3 /opt/bin/start_vm.py vm1 start
ExecStop=/usr/bin/python3 /opt/bin/start_vm.py vm1 stop

[Install]
WantedBy=multi-user.target
```

and another file for `vm2` `/etc/systemd/system/start_vm2.service`
```
[Unit]
Description=Start vm2
Requires=network-online.target libvirtd.service
After=network-online.target libvirtd.service

[Service]
Type=oneshot
RemainAfterExit=yes
ExecStart=/usr/bin/python3 /opt/bin/start_vm.py vm2 start
ExecStop=/usr/bin/python3 /opt/bin/start_vm.py vm2 stop

[Install]
WantedBy=multi-user.target
```

3. Run 
```
systemctl daemon-reload
systemctl start start_vm1.service
systemctl start start_vm2.service
```
and stop them
```
systemctl stop start_vm1.service
systemctl stop start_vm2.service
```
if everything works enable these two services
```
systemctl enable start_vm1.service
systemctl enable start_vm2.service
```

### Multiple VMs
If you have several VMs (`vm1`, `vm2`, `vm3`, ...), some could start without network connection (`vm1`,...), the others need to wait online (`vm2`, `vm3`, ...).
Then we could create two systemd files using instance names to start different VMs

1. copy `start_vm.py` to `/opt/bin/`

2. create a systemd service file for those don't need network connection `/etc/systmed/system/start_vm@.service`
```
[Unit]
Description=Start VM %I
Requires=libvirtd.service
After=libvirtd.service

[Service]
Type=oneshot
RemainAfterExit=yes
ExecStart=/usr/bin/python3 /opt/bin/start_vm.py %i start
ExecStop=/usr/bin/python3 /opt/bin/start_vm.py %i stop

[Install]
WantedBy=multi-user.target
```

and another file for those need to wait online `/etc/systemd/system/start_vm_online@.service`
```
[Unit]
Description=Start VM %I
Requires=network-online.target libvirtd.service
After=network-online.target libvirtd.service

[Service]
Type=oneshot
RemainAfterExit=yes
ExecStart=/usr/bin/python3 /opt/bin/start_vm.py %i start
ExecStop=/usr/bin/python3 /opt/bin/start_vm.py %i stop

[Install]
WantedBy=multi-user.target
```

3. Run 
```
systemctl daemon-reload
# VMs don't need to wait network connection
systemctl start start_vm@vm1.service
...
# VMs need to wait network connection
systemctl start start_vm_online@vm2.service
systemctl start start_vm_online@vm3.service
...
```
and stop them
```
# VMs don't need to wait network connection
systemctl stop start_vm@vm1.service
...
# VMs need to wait network connection
systemctl stop start_vm_online@vm2.service
systemctl stop start_vm_online@vm3.service
...
```
if everything works enable these services
```
# VMs don't need to wait network connection
systemctl enable start_vm@vm1.service
...
# VMs need to wait network connection
systemctl enable start_vm_online@vm2.service
systemctl enable start_vm_online@vm3.service
...
```




