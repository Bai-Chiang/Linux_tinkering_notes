# Install headless libvirt VM

command:
```
virt-install \
    --name vm_name \
    --memory 1024 \
    --memorybacking allocation.mode=ondemand \
    --cpu host-passthrough,cache.mode=passthrough,topology.sockets=1,topology.cores=1,topology.threads=1 \
    --os-variant name=archlinux \
    --cdrom /path/to/archlinux.iso \
    --disk path=/var/lib/libvirt/images/vm_name.qcow2,size=16,bus=virtio \
    --network bridge=br0,model.type=virtio \
    --graphics none \
    --autoconsole text \
    --serial pty \
    --boot firmware=efi \
    --autostart
```

At the systemd-boot boot loader selection screen press `e` enter edit mode.
Add `console=ttyS0` to the end of kernel parameters.
Then press `Enter` to continue boot.
