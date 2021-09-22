# Arch Linux Installation Notes

## Pre-installation

- Following official [Arch Linux Installation Guide](https://wiki.archlinux.org/title/Installation_guide).
- The patition scheme follows [this](https://wiki.archlinux.org/title/Parted#Partitioning).
  ```
  parted /dev/nvme0n1
  ```
  In `parted`
  ```
  mklabel gpt
  mkpart "EFI" fat32 1MiB 513MiB
  set 1 esp on
  mkpart "ROOT" btrfs 513MiB 100%
  ```
- Format root partition as [btrfs](https://btrfs.wiki.kernel.org/index.php/Using_Btrfs_with_Multiple_Devices#Filesystem_creation)
  and mount it to `/mnt` and create subvolumes `@` `@home` `@snapshots`.
  ```
  mount /dev/nvme0n1p1 /mnt
  btrfs subvolume create @
  btrfs subvolume create @home
  btrfs subvolume create @snapshots
  ```
  Unmount `/mnt` and remount subvolumes with

  ```
  mount -o ssd,noatime,compress=zstd:1,space_cache=v2,autodefrag,subvol=@arch /dev/nvme0n1p2 /mnt
  mkdir /mnt/.snapshots /mnt/home /mnt/boot
  mount -o ssd,noatime,compress=zstd:1,space_cache=v2,autodefrag,subvol=@arch_snapshots /dev/nvme0n1p2 /mnt/.snapshots
  mount -o ssd,noatime,compress=zstd:1,space_cache=v2,autodefrag,subvol=@home /dev/nvme0n1p2 /mnt/home
  ```

  - `ssd` for SSD optimizations
  - `noatime` improves performance for read intensive work-loads may break applications that rely on atime uptimes
  - `compress=zstd:1` [transparent compression](https://wiki.archlinux.org/title/btrfs#Compression)
      `zstd:1` for primary SSD and `zstd:3` for storage drive
  - ~~`discard=async` [SSD TRIM](https://wiki.archlinux.org/title/btrfs#SSD_TRIM)~~ 
      (Using `fstrim.timer` systemd unit file for [SSD TRIM](https://wiki.archlinux.org/title/Solid_state_drive#Periodic_TRIM) now)
  - `space_cache=v2` improves performance
  - `autodefrag` enable automatic file defragmentation, may increase read latency
  
  see [`btrfs(5)`](https://man.archlinux.org/man/btrfs.5#MOUNT_OPTIONS) for more mount options. 
- Other [Pre-installation](https://wiki.archlinux.org/title/Installation_guide#Pre-installation) steps.

## Installation

- Install base system with pacstrap
- `genfstab` may generate multiple `subvol` or `subvolid` options in `/mnt/etc/fstab` for btrfs file system.
  Only keep one option like `subvol=/@`. Remove `subvolid` option and other `subvol` option.
- Chroot in to new system.
- When configuring network, enable `systemd-networkd.service` and `systemd-resolved.service`.
  Create simple `systemd-networkd` configuration file fillowing [this example.](https://wiki.archlinux.org/title/Systemd-networkd#Wired_and_wireless_adapters_on_the_same_machine)
- [Install](https://wiki.archlinux.org/title/Systemd-boot#Installation) `systemd-boot` EFI boot manager.
  Set up [automatic update](https://wiki.archlinux.org/title/Systemd-boot#Automatic_update) the boot manager
  after updating `systemd`.
  Create [loader configuration](https://wiki.archlinux.org/title/Systemd-boot#Loader_configuration) file,
  and new [loader](https://wiki.archlinux.org/title/Systemd-boot#Adding_loaders).
  When using btrfs as root partition add kernel parameter [`rootflags=subvol=/path/to/subvolume`](https://wiki.archlinux.org/title/btrfs#Mounting_subvolume_as_root).
- Finish the [Installation Guide](https://wiki.archlinux.org/title/Installation_guide) and reboot.
    
## Post-installation
- Boot into new system.
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
- Install GPU driver and GUI components.



