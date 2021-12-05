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

- [Secure Boot](https://wiki.archlinux.org/title/Unified_Extensible_Firmware_Interface/Secure_Boot#Signing_EFI_binaries)

  [Set up secure boot using your own keys.](https://wiki.archlinux.org/title/Unified_Extensible_Firmware_Interface/Secure_Boot#Using_your_own_keys) 
  Read [Rod Smith's secure boot guide](https://www.rodsbooks.com/efi-bootloaders/controlling-sb.html) and [ArchWiki page](https://wiki.archlinux.org/title/Unified_Extensible_Firmware_Interface/Secure_Boot) to understand secure boot.
  
  This method will replace default platform key with your own key,
  but some firmwares of plug-in cards are signed using Microsoft keys.
  These cards won't work during pre-boot environment,
  but still work after the OS is booted.
  This would be a problem for video cards, because before boot no video output you can't enter BIOS, 
  or PXE-booting NIC if you boot over network.
  Read [Rod Smith's secure boot guide](https://www.rodsbooks.com/efi-bootloaders/controlling-sb.html) and [ArchWiki page](https://wiki.archlinux.org/title/Unified_Extensible_Firmware_Interface/Secure_Boot) to understand secure boot.
  
  - Preparation
  
    ```
    # pacman -S efitools sbsigntools
    # mkdir /etc/efi-keys
    # cd /etc/efi-keys
    ```
  - Backup current keys

    ```
    # efi-readvar -v PK -o old_PK.esl
    # efi-readvar -v KEK -o old_KEK.esl
    # efi-readvar -v db -o old_db.esl
    # efi-readvar -v dbx -o old_dbx.esl
    ```
  - Create GUID for owner identification

    ```
    # uuidgen --random > GUID.txt
    ```
    
  - Generate Keys 
    
    Platform Key
    ```
    # openssl req -newkey rsa:4096 -nodes -keyout PK.key -new -x509 -sha256 -days 3650 -subj "/CN=my Platform Key/" -out PK.crt
    # openssl x509 -outform DER -in PK.crt -out PK.cer
    # cert-to-efi-sig-list -g "$(< GUID.txt)" PK.crt PK.esl
    # sign-efi-sig-list -g "$(< GUID.txt)" -k PK.key -c PK.crt PK PK.esl PK.auth
    ```
    Key Exchange Key
    ```
    # openssl req -newkey rsa:4096 -nodes -keyout KEK.key -new -x509 -sha256 -days 3650 -subj "/CN=my Key Exchange Key/" -out KEK.crt
    # openssl x509 -outform DER -in KEK.crt -out KEK.cer
    # cert-to-efi-sig-list -g "$(< GUID.txt)" KEK.crt KEK.esl
    # sign-efi-sig-list -g "$(< GUID.txt)" -k PK.key -c PK.crt KEK KEK.esl KEK.auth
    ```
    Database Key
    ```
    # openssl req -newkey rsa:4096 -nodes -keyout db.key -new -x509 -sha256 -days 3650 -subj "/CN=my Signature Database key/" -out db.crt
    # openssl x509 -outform DER -in db.crt -out db.cer
    # cert-to-efi-sig-list -g "$(< GUID.txt)" db.crt db.esl
    # sign-efi-sig-list -g "$(< GUID.txt)" -k KEK.key -c KEK.crt db db.esl db.auth
    ```
  
  - [Put firmware in "setup mode".]https://wiki.archlinux.org/title/Unified_Extensible_Firmware_Interface/Secure_Boot#Putting_firmware_in_%22Setup_Mode%22).
  
  Run command `bootctl status` if `Setup Mode: user` means you are in user mode, `Setup Mode: setup` means you are in setup mode.
  
  - Enroll keys into firmware

    Create directories and copy your previous created `*.auth` files to corresponding directory.
    ```
    # mkdir -p /etc/secureboot/keys/{db,dbx,KEK,PK}
    # cp /etc/efi-keys/PK.auth /etc/secureboot/keys/PK/
    # cp /etc/efi-keys/KEK.auth /etc/secureboot/keys/KEK/
    # cp /etc/efi-keys/db.auth /etc/secureboot/keys/db/
    ```
    Test run
    ```
    # sbkeysync --pk --dry-run --verbose
    ```
    Enroll your keys
    ```
    # sbkeysync --verbose
    ```
    If `sbkeytync` returns write error, run  command `chattr -i /sys/firmware/efi/efivars/{PK,KEK,db}*` then try again.
    
    Enroll your PK
    ```
    # sbkeysync --verbose --pk
    ```
    If failed, run command `efi-updatevar -f /usr/share/secureboot/keys/PK/PK.auth PK` then try again.
  
  - Setup [unified kernel image]((https://wiki.archlinux.org/title/Unified_kernel_image)
  
    To protect both initramfs and kernel we need to set up a unified kernel image.
  
    Modify `/etc/mkinitcpio.d/linux.preset`
    ```
    # mkinitcpio preset file for the 'linux' package

     ALL_config="/etc/mkinitcpio.conf"
     ALL_kver="/boot/vmlinuz-linux"
    +ALL_microcode=(/boot/*-ucode.img)

     PRESETS=('default' 'fallback')

     #default_config="/etc/mkinitcpio.conf"
     default_image="/boot/initramfs-linux.img"
     #default_options=""
    +default_efi_image="esp/EFI/Linux/archlinux-linux.efi"

     #fallback_config="/etc/mkinitcpio.conf"
     fallback_image="/boot/initramfs-linux-fallback.img"
     fallback_options="-S autodetect"
    +fallback_efi_image="esp/EFI/Linux/archlinux-linux-fallback.efi"
    ```
    added lines start with `+`.
  
    Creat `/etc/kernel/cmdline` with your kernel parameters
    ```
    # cp /proc/cmdline /etc/kernel/cmdline
    ```
    then delete entries `initrd=` in `/etc/kernel/cmdline`, you may need to add write permission `chmod u+w /etc/kernel/cmdline`.
    
    Regenerate the initramfs
    ```
    # mkinitcpio -P
    ```
    Add a pacman hook `/etc/pacman.d/hooks/99-secureboot.hook` to auto re-sign it when update
    ```
    [Trigger]
    Operation = Install
    Operation = Upgrade
    Type = Package
    Target = linux
    Target = systemd

    [Action]
    Description = Signing Kernel for SecureBoot
    When = PostTransaction
    Exec = /usr/bin/find /boot -type f ( -name 'archlinux-linux*.efi' -o -name systemd* ) -exec /usr/bin/sh -c 'if ! /usr/bin/sbverify --list {} 2>/dev/null | /usr/bin/grep -q "signature certificates"; then /usr/bin/sbsign --key /etc/efi-keys/db.key --cert /etc/efi-keys/db.crt --output "$1" "$1"; fi' _ {} ;
    Depends = sbsigntools
    Depends = findutils
    Depends = grep
    ```
    
    Sign the unified kernel image and check it works with reinstall `linux` package
    ```
    pacman -S linux
    ```
    Sign the boot manager
    ```
    # sbsign --key db.key --cert /etc/efi-keys/db.crt --output esp/EFI/BOOT/BOOTx64.EFI esp/EFI/BOOT/BOOTx64.EFI
    ```
  - Update boot entry
   
    update default boot entry in systemd-boot loader `/boot/loader/loader.conf`
    ```
    default  archlinux-linux.efi
    ...
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
