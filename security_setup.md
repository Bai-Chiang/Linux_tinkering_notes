# Basic security setup

see [ArchWiki-security](https://wiki.archlinux.org/title/Security) for more details and complete security practice.

- Login as new user make sure `sudo` is working.
  [Disable root login](https://wiki.archlinux.org/title/Sudo#Disable_root_login) 
  by deleting root password `sudo passwd -d root` and 
  locking root account `sudo passwd -l root`.

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
- [Swap encryption](https://wiki.archlinux.org/title/Dm-crypt/Swap_encryption) (without suspend-to-disk/hibernation)
  
  First deactive existing swap partition
  ```
  # swapoff /dev/nvme0n1p2
  ```
  Then we need to find out its persistent partition name.
  Simple naming like `/dev/sdX` may change, and causing cryptab swap to format your data.
  By default, `dm-crypt` and `mkswap` will remove UUID and LABEL on that partition.
  So we need to create a small filesystem to provide UUID or LABEL,
  and specify a swap offset.
  
  Create a filesystem with label cryptswap
  ```
  # mkfs.ext2 -L cryptswap /dev/nvme0n1p2 1M
  ```
  uncomment and modify the entry in `/etc/crypttab`
  ```
  # <name> <device>         <password>    <options>
  swap     LABEL=cryptswap  /dev/urandom  swap,offset=2048,...
  ```
  change <device> column to `LABEL=cryptswap`, anc add `offset=2048` to <options>, that means 2048 512-byte sectors which is 1MiB. Keep other options as default.
  
  Update `/etc/fstab`
  ```
  # <filesystem>    <dir>  <type>  <options>  <dump>  <pass>
  /dev/mapper/swap  none   swap    defaults   0       0
  ```
