# Arch Linux Installation Notes

This arch linux installation notes will guide you set up
- btrfs as root filesystem
- systemd-boot
- encrypted root partition
- systemd-networkd

## Prepare bootable USB drive
- [Download](https://archlinux.org/download/) `archlinux.iso` and [create bootable USB drive](https://wiki.archlinux.org/title/USB_flash_installation_medium#Using_the_ISO_as_is_(BIOS_and_UEFI)) `/dev/sdx` with
  ```
  # dd bs=4M if=path/to/archlinux.iso of=/dev/sdx conv=fsync oflag=direct status=progress
  ```
- Disable secure boot and enable UEFI mode (systemd-boot only support UEFI) in bios
- Boot into USB drive
  
## Pre-installation
- [Verify boot into UEFI mode](https://wiki.archlinux.org/title/Installation_guide#Verify_the_boot_mode)
  ```
  # ls /sys/firmware/efi/efivars
  ```
  this should list files in the directory without errors, otherwise check bios setting.
- [Check network connection](https://wiki.archlinux.org/title/Installation_guide#Connect_to_the_internet) with
  ```
  # ping archlinux.org
  ```
  recommend using ehternet or USB ethernet adapter, for wireless configuration see [this](https://wiki.archlinux.org/title/Iwctl)
- [Update system clock](https://wiki.archlinux.org/title/Installation_guide#Update_the_system_clock)
  ```
  # timedatectl set-ntp true
  ```
- Identify the block device for `boot` and `root` partition with 
  ```
  # lsblk
  ```
  in following tutorial, we install to the nvme ssd `/dev/nvme0n1`.
- [Create GPT partition label](https://wiki.archlinux.org/title/Parted#Create_new_partition_table). 
  ```
  # parted /dev/nvme0n1
  (parted) mklabel gpt
  ```
  The patition scheme follows [this](https://wiki.archlinux.org/title/Parted#UEFI/GPT_examples) example,
  with 512MiB boot partition (also EFI partition), 4GiB swap partition and remaining space as root partition.
  ```
  (parted) mkpart "EFI system partition" fat32 0% 512MiB
  (parted) set 1 esp on
  (parted) mkpart "swap partition" linux-swap 512MiB 4.5GiB
  (parted) mkpart "root partition" btrfs 4.5GiB 100%
  (parted) quit
  ```
- Format the EFI partiton
  ```
  # mkfs.fat -F32 /dev/nvme0n1p1
  ```
- Create swap partition
  ```
  mkswap /dev/nvme0n1p2
  ```
- [Setup encrypted root partition with LUKS mode](https://wiki.archlinux.org/title/Dm-crypt/Device_encryption#Encryption_options_for_LUKS_mode)
  ```
  # cryptsetup --type luks2 --verify-passphrase --sector-size 4096 --verbose luksFormat /dev/nvme0n1p3
  ```
- Optionally, add a keyfile to an USB drive to auto unlock when pluged in.
  - Plug in the USB drive `/dev/sdb`, format and mount it as `/media`
    ```
    # parted /dev/sdb 
    (parted) mklabel gpt
    (parted) mkpart partition1 ext4 0% 100%
    (parted) quit
    # mkfs.ext4 /dev/sdb1
    # mkdir /media
    # mount /dev/sdb1 /media
    ```
  - [Create keyfile](https://wiki.archlinux.org/title/Dm-crypt/Device_encryption#Creating_a_keyfile_with_random_characters)
    ```
    # dd bs=512 count=4 if=/dev/random of=/media/mykeyfile iflag=fullblock
    # chmod 600 /media/mykeyfile
    ```
  - [Add keyfile to LUKS](https://wiki.archlinux.org/title/Dm-crypt/Device_encryption#Configuring_LUKS_to_make_use_of_the_keyfile)
    ```
    # cryptsetup luksAddKey /dev/nvme0n1p3 /media/mykeyfile
    ```
    Or
    ```
    # cryptsetup --type luks2 --verify-passphrase --sector-size 4096 --key-file=/media/mykeyfile --verbose luksFormat /dev/nvme0n1p3
    ```
    create a encrypted partition without passphrase (keyfile only).
- Format root partition as [btrfs](https://btrfs.wiki.kernel.org/index.php/Using_Btrfs_with_Multiple_Devices#Filesystem_creation) 
  ```
  # cryptsetup open /dev/nvme0n1p3 cryptroot
  # mkfs.btrfs /dev/mapper/cryptroot
  # mount /dev/mapper/cryptroot /mnt
  ```
  and create top-level subvolumes `@` `@home` `@snapshots` (following [this](https://wiki.archlinux.org/title/Snapper#Suggested_filesystem_layout) suggested layout)
  ```
  # btrfs subvolume create /mnt/@
  # btrfs subvolume create /mnt/@home
  # btrfs subvolume create /mnt/@snapshots
  # mkdir /mnt/@/{boot,home,.snapshots}
  # umount -R /mnt
  ``` 
- Mount the file system
  ```
  # mount -o ssd,noatime,compress=zstd:1,space_cache=v2,autodefrag,subvol=@ /dev/mapper/cryptroot /mnt
  # mount -o ssd,noatime,compress=zstd:1,space_cache=v2,autodefrag,subvol=@home /dev/mapper/cryptroot /mnt/home
  # mount -o ssd,noatime,compress=zstd:1,space_cache=v2,autodefrag,subvol=@snapshots /dev/mapper/cryptroot /mnt/.snapshots
  # mount /dev/nvme0n1p1 /mnt/boot
  # swapon /dev/nvme0n1p2
  ```
  btrfs mount options:
  - `ssd` for SSD optimizations
  - `noatime` improves performance for read intensive work-loads may break applications that rely on atime uptimes
  - `compress=zstd:1` [transparent compression](https://wiki.archlinux.org/title/btrfs#Compression)
      `zstd:1` for primary SSD and `zstd:3` for storage drive
  - ~~`discard=async` [SSD TRIM](https://wiki.archlinux.org/title/btrfs#SSD_TRIM)~~ (Using `fstrim.timer` systemd unit file for [SSD TRIM](https://wiki.archlinux.org/title/Solid_state_drive#Periodic_TRIM) now). 
    
    > TRIM support for SSD will never be enabled by default on dm-crypt because of the potential security implications.
    
    quote from [here](https://wiki.archlinux.org/title/Dm-crypt/Specialties#Discard/TRIM_support_for_solid_state_drives_(SSD))  
  - `space_cache=v2` improves performance
  - `autodefrag` enable automatic file defragmentation, may increase read latency
  
  see [`btrfs(5)`](https://man.archlinux.org/man/btrfs.5#MOUNT_OPTIONS) for more mount options. 

## Installation
- [Install essential packages](https://wiki.archlinux.org/title/Installation_guide#Install_essential_packages)
  ```
  # pacstrap /mnt base linux linux-firmware btrfs-progs dosfstools e2fsprogs vim man-db man-pages texinfo
  ```
  and other essential packages you may need following [this](https://wiki.archlinux.org/title/Installation_guide#Install_essential_packages) guide.
- Generate `fstab`
  ```
  # genfstab -U /mnt >> /mnt/etc/fstab
  ```
  `genfstab` may generate multiple `subvol` or `subvolid` options in `/mnt/etc/fstab` for btrfs file system.
  Only keep one option like `subvol=/@`. Remove `subvolid` option and other `subvol` option.
- Chroot into new system
  ```
  # arch-chroot /mnt
  # export PS1="(chroot) ${PS1}"
  ```
- [Set time zone](https://wiki.archlinux.org/title/Installation_guide#Time_zone)
  ```
  (chroot) # ln -sf /usr/share/zoneinfo/Region/City /etc/localtime
  (chroot) # hwclock --systohc
  ```
- [Set locale](https://wiki.archlinux.org/title/Installation_guide#Localization)
  
  Uncomment `en_US.UTF-8 UTF-8` in `/etc/locale.gen`, then
  ```
  (chroot) # locale-gen
  ```
  create `/etc/locale.conf`
  ```
  LANG=en_US.UTF-8
  ```
  Set the console keyboard layout in `/etc/vconsole.conf`
  ```
  KEYMAP=us
  ```
- Set root password
  ```
  (chroot) # passwd
  ```
- Network configuration

  Create hostname file `/etc/hostname`
  ```
  myhostname
  ```
  enable `systemd-networkd.service` and `systemd-resolved.service`
  ```
  (chroot) # systemctl enable systemd-networkd.service
  (chroot) # systemctl enable systemd-resolved.service
  ```
  Create simple `systemd-networkd` configuration file fillowing [this example.](https://wiki.archlinux.org/title/Systemd-networkd#Wired_and_wireless_adapters_on_the_same_machine)
  wired connection `/etc/systemd/network/20-wired.network`
  ```
  [Match]
  Name=en*

  [Network]
  DHCP=yes

  [DHCP]
  RouteMetric=10
  ```
  wireless connection `/etc/systemd/network/25-wireless.network`
  ```
  [Match]
  Name=wl*

  [Network]
  DHCP=yes

  [DHCP]
  RouteMetric=20
  ```
- [Configure mkinitcpio hooks](https://wiki.archlinux.org/title/Dm-crypt/System_configuration#mkinitcpio)

  Edit `/etc/mkinitcpio.conf`
  ```
  ...
  HOOKS=(base systemd keyboard autodetect sd-vconsole modconf block sd-encrypt filesystems fsck)
  ...
  ```
  - If created a keyfile on the USB drive, also [add its file system to the kernel module](https://wiki.archlinux.org/title/Dm-crypt/Device_encryption#Configuring_mkinitcpio) in `/etc/mkinitcpio.conf`
    ```
    MODULES=(ext4)
    ```
  then regenerate the initramfs
  ```
  (chroot) # mkinitcpio -P
  ```
- Install [microde](https://wiki.archlinux.org/title/Microcode)
  - for Intel processors
  ```
  (chroot) # pacman -S intel-ucode
  ```
  - for AMD processors
  ```
  (chroot) # pacman -S amd-ucode
  ```
- [Install](https://wiki.archlinux.org/title/Systemd-boot#Installation) `systemd-boot` EFI boot manager.
  ```
  (chroot) # bootctl install
  ```
  Set up [automatic update](https://wiki.archlinux.org/title/Systemd-boot#Automatic_update) the boot manager
  after updating systemd, edit `/etc/pacman.d/hooks/100-systemd-boot.hook`
  ```
  [Trigger]
  Type = Package
  Operation = Upgrade
  Target = systemd

  [Action]
  Description = Updating systemd-boot
  When = PostTransaction
  Exec = /usr/bin/bootctl update
  ```
  Create [loader configuration](https://wiki.archlinux.org/title/Systemd-boot#Loader_configuration) file `/boot/loader/loader.conf`
  ```
  default  arch.conf
  timeout  3
  console-mode max
  editor   no
  ```
  and new [loader](https://wiki.archlinux.org/title/Systemd-boot#Adding_loaders), `/boot/loader/entries/arch.conf`
  ```
  title   Arch Linux
  linux   /vmlinuz-linux
  initrd  /cpu_manufacturer-ucode.img
  initrd  /initramfs-linux.img
  options rd.luks.name=root_partition_UUID=cryptroot rd.luks.options=root_partition_UUID=password-echo=no,x-systemd.device-timeout=0,timeout=0,no-read-workqueue,no-write-workqueue,discard root=/dev/mapper/cryptroot rootflags=subvol=/@ rw
  ```
  replace `cpu_manufacture-ucode.img` with `intel-ucode.img` or `amd-ucode.img` depending on your processor manufacture, and use `lsblk -dno UUID /dev/nvme0n1p3` to get UUID for root partition.
  
  Some explanation to options:
  - `rd.luks.options=password-echo=no` silence the output when typing the password (not showing the asterisks * for each character)
  - `rd.luks.options=x-systemd.device-timeout=0` let systemd wait for the rootfs device to show up indefinitely.
  - `rd.luks.options=timeout=0` disable the timeout for querying for a password.
  - `rd.luks.options=no-read-workqueue,no-write-workqueue` [Disable workqueue for increasing SSD performance](https://wiki.archlinux.org/title/Dm-crypt/Specialties#Disable_workqueue_for_increased_solid_state_drive_(SSD)_performance)
  - `rd.luks.options=discard` enable TRIM support for SSD, it is disabled by default for security, see [this](https://wiki.archlinux.org/title/Dm-crypt/Specialties#Discard/TRIM_support_for_solid_state_drives_(SSD))
  
  See [`cryttab(5)`](https://man.archlinux.org/man/crypttab.5.en) for more options.
  - If created a keyfile on the USB drive, add extra kenel parameter
    ```
    rd.luks.key=root_partition_UUID=/mykeyfile:UUID=USB_drive_partition_UUID
    ```
    and extra LUKS option to fallback to password prompt when the USB drive is not detected
    ```
    rd.luks.options=root_partition_UUID=keyfile-timeout=5s
    ```
    the options line would be
    ```
    options rd.luks.name=root_partition_UUID=cryptroot rd.luks.key=root_partition_UUID=/mykeyfile:UUID=USB_drive_partition_UUID rd.luks.options=root_partition_UUID=password-echo=no,x-systemd.device-timeout=0,keyfile-timeout=5s,timeout=0,no-read-workqueue,no-write-workqueue,discard root=/dev/mapper/cryptroot rootflags=subvol=/@ rw
    ```
  
  Similarly, create fallback loader `/boot/loader/entries/arch-fallback.conf` by copying previous one
  ```
  (chroot) # cp /boot/loader/entries/arch.conf /boot/loader/entries/arch-fallback.conf
  ```
  then change title and initrd entries in `/boot/loader/entries/arch-fallback.conf`
  ```
  title   Arch Linux (fallback initramfs)
  linux   /vmlinuz-linux
  initrd  /cpu_manufacturer-ucode.img
  initrd  /initramfs-linux-fallback.img
  options ...
  ```
- reboot
  ```
  (chroot) # exit
  # umount -R /mnt
  # reboot
  ```
    
## Post-installation
- [Add](https://wiki.archlinux.org/title/Users_and_groups#Example_adding_a_user) new user,
  [add](https://wiki.archlinux.org/title/Users_and_groups#Group_management) it to group `wheel`.
  Install `sudo` package use `visudo` edit `sudoers` file.
  Uncomment `%wheel ALL=(ALL) ALL` allow members in `wheel` group gain `sudo` access,
  or `%wheel ALL=(ALL) NOPASSWD: ALL` execute any command without password (insecure!).
- Login as new user make sure `sudo` is working.
  [Disable root login](https://wiki.archlinux.org/title/Sudo#Disable_root_login) 
  by deleting root password `sudo passwd -d root` and 
  locking root account `sudo passwd -l root`.
- Install [reflector](https://wiki.archlinux.org/title/reflector),
  [edit](https://wiki.archlinux.org/title/reflector#systemd_service) configuration file,
  and enable `reflector.timer` to update mirrorlist weekly.
- Install ` pacman-contrib` package, enable `paccache.timer` to delete unused pacman cache weekly.
- Enable `fstrim.timer` provided by `util-linux` package for [Periodic SSD TRIM](https://wiki.archlinux.org/title/Solid_state_drive#Periodic_TRIM).
- Install `snapper` and `cronie` package. 
  Follow [this](https://wiki.archlinux.org/title/snapper#Suggested_filesystem_layout) guide set up snapper for root subvolume.
  [Create](https://wiki.archlinux.org/title/snapper#Creating_a_new_configuration) new config for home and
  [edit](https://wiki.archlinux.org/title/snapper#Set_snapshot_limits) snapshots limit for both root and home config.
- Wifi set up, use [iwd](https://wiki.archlinux.org/title/Iwd) or [wpa_supplicant](https://wiki.archlinux.org/title/Wpa_supplicant#At_boot_(systemd))
  (I can't connect to [MSCHAPv2](https://wiki.archlinux.org/title/Iwd#EAP-PEAP) network with `iwd`, but it works with `wpa_supplicant`.) 
  
## [Security](https://wiki.archlinux.org/title/Security)
- Set up [Uncomplicated Firewall (ufw)](https://wiki.archlinux.org/title/Uncomplicated_Firewall)
  ```
  ufw default allow outgoing deny incoming deny routed
  ```
  This allow ssh incoming from local network `192.168.1.0/24` on `eth0` interface.
  ```
  ufw allow in on eth0 from 192.168.1.0/24 to any app ssh comment 'allow ssh incoming'
  ```
  Another example, allow other device on local network access [`transmission`](https://wiki.archlinux.org/title/Transmission) web interface:
  ```
  ufw allow in proto tcp from 192.168.1.0/24 to any port 9091 comment 'allow access transmission web interface'
  ```
- [Disk encryption](https://wiki.archlinux.org/title/Security#Storage)



