# Single GPU PCI Passthrough/VFIO for headless host
This notes uses `virt-install` command line install virtual machine instead of GUI application `virt-manager`.
This setup is for headless host that does not have `X`/`wayland` installed.

## [GPU Passthough setup](https://wiki.archlinux.org/title/PCI_passthrough_via_OVMF)
- Follow the Arch Wiki make sure the system meets the [requirements](https://wiki.archlinux.org/title/PCI_passthrough_via_OVMF#Prerequisites)
- [Set up IOMMU Group](https://wiki.archlinux.org/title/PCI_passthrough_via_OVMF#Setting_up_IOMMU)
- [GPU Isolation](https://wiki.archlinux.org/title/PCI_passthrough_via_OVMF#Isolating_the_GPU)

## [Virtual Machine setup](https://wiki.archlinux.org/title/Libvirt)
- Install `qemu` `libvirt` `iptables-nft` `dnsmasq` `bridge-utils` `edk2-ovmf` `dmidecode`(for exposing the host's SMBIOS info to the VM) `swtpm`(for TPM 2.0 emulator)
  ```
  pacman -S qemu libvirt iptables-nft dnsmasq bridge-utils edk2-ovmf dmidecode swtpm
  ```
  and reboot.

- Add yourself to `libvirt`group (see [this](https://wiki.archlinux.org/title/Libvirt#Using_libvirt_group))
  ```
  usermod -aG libvirt my_username
  ```

- Start `libvirtd.service` `virtlogd.service` and enable `libvirtd.service` (see [this](https://wiki.archlinux.org/title/Libvirt#Daemon))
  ```
  systemctl start libvirtd.service
  systemctl start virtlogd.service
  systemctl enable libvirtd.service
  ```

- You may also need to activate the default libvirt network
  ```
  virsh net-autostart default
  virsh net-start default
  ```

- For btrfs create a subvolume for VM images, so that it's not backuped in snapshots.
  ```
  btrfs subvolume create /home/username/VM_images
  ```
  and disable Copy-on-Write (CoW) for this directory
  ```
  chattr +C /home/username/VM_images
  ```

- For linux guest, download the ISO for your favourate distrobution.
  - Create VM usinng command
    ```
    virt-install \
        --name new_vm \
        --memory 8192 \
        --sysinfo host \
        --cpu host-passthrough,cache.mode=passthrough,topology.sockets=1,topology.cores=4,topology.threads=1 \
        --os-variant detect=on,require=on,name=archlinux \
        --cdrom /path/to/linux.iso \
        --network network=default,model.type=virtio \
        --graphics none \
        --noautoconsole \
        --boot uefi \
        --disk path=/home/username/VM_images/new_vm.qcow2,size=64,bus=virtio \
        --disk path=/path/to/storage/disk.qcow2,size=100,bus=virtio \
        --hostdev 01:00.0,type=pci \
        --hostdev 01:00.1,type=pci \
        --hostdev 0x046d:0xc52b,type=usb
    ```
    - `--cpu topology.cores` specify how many CPU core this guest machine could use.
    - `--os-variant` use `osinfo-query os` command list all os variants name
    - If disk already exist, remove `size=` under `--disk`.
    - `hostdev` pass host device to VM. Use `lspci` get all PCI devices and `lsusb` get all usb vendor:product ids.
      Note that when using vender:product id for use device need add `0x` before the vender:product id output from `lsubs`.
    See `man virt-install` for more option details.

- For windows guest, download Windows ISO and virtio driver from https://github.com/virtio-win/virtio-win-pkg-scripts/blob/master/README.md if using virtio disk or virtio network.
  - Create VM usinng command
    ```
    virt-install \
        --name your_windows_vm_name \
        --memory 8192 \
        --sysinfo host \
        --cpu host-passthrough,cache.mode=passthrough,topology.sockets=1,topology.cores=6,topology.threads=1 \
        --os-variant name=win10 \
        --cdrom /path/to/windows.iso \
        --disk path=/path/to/virtio-win-0.1.xxx.iso,device=cdrom,bus=sata \
        --network network=default,model.type=virtio \
        --graphics none \
        --noautoconsole \
        --boot uefi,loader=/usr/share/edk2-ovmf/x64/OVMF_CODE.secboot.fd,loader.readonly=yes,loader.secure=yes,loader.type=pflash,nvram.template=/usr/share/edk2-ovmf/x64/OVMF_VARS.fd \
        --features smm.state=on \
        --tpm model=tpm-crb,backend.type=emulator,backend.version=2.0 \
        --disk path=/path/to/OS/disk.qcow2,size=65,bus=virtio \
        --disk path=/path/to/storage/disk.qcow2,size=100,bus=virtio \
        --hostdev 01:00.0,type=pci \
        --hostdev 01:00.1,type=pci \
        --hostdev 0x0f39:0x0611,type=usb \
        --hostdev 0x1532:0x0071,type=usb
    ```
    Change the last four line changes to your GPU pcie address and usb keyboard and mouse device id.

- If your computer comes with windows OEM activation, use this command to get your OEM key, and use it during installation process.
  ```
  sudo strings /sys/firmware/acpi/tables/MSDM | tail -1
  ```

- Nvidia laptop driver error code 43, see https://wiki.archlinux.org/title/PCI_passthrough_via_OVMF#%22Error_43:_Driver_failed_to_load%22_with_mobile_(Optimus/max-q)_nvidia_GPUs

