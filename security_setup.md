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
  In that case we need to enroll Microsoft's key, but that defeat the benefits of using your own key.
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
  
  - [Put firmware in "setup mode".](https://wiki.archlinux.org/title/Unified_Extensible_Firmware_Interface/Secure_Boot#Putting_firmware_in_%22Setup_Mode%22)
  
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
    If `sbkeytync` returns write error or can't create key file, run  command `chattr -i /sys/firmware/efi/efivars/{PK,KEK,db}*` then try again.
    
    Enroll your PK
    ```
    # sbkeysync --verbose --pk
    ```
    If failed, run command `efi-updatevar -f /etc/secureboot/keys/PK/PK.auth PK` then try again.
  
  - Setup [unified kernel image](https://wiki.archlinux.org/title/Unified_kernel_image)
  
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
    -#default_options=""
    +default_options="--splash /usr/share/systemd/bootctl/splash-arch.bmp"
    +default_efi_image="/boot/EFI/Linux/archlinux-linux.efi"

     #fallback_config="/etc/mkinitcpio.conf"
     fallback_image="/boot/initramfs-linux-fallback.img"
    -fallback_options="-S autodetect"
    +fallback_options="-S autodetect --splash /usr/share/systemd/bootctl/splash-arch.bmp"
    +fallback_efi_image="/boot/EFI/Linux/archlinux-linux-fallback.efi"
    ```
    added lines start with `+` deleted line start with `-`. Here we added Arch Linux logo to splash screen.
    
    Also modify other kernel presets you installed. For example, change `linux` to `linux-zen` in `/etc/mkinitcpio.d/linux-zen.preset` for `linux-zen` kernel.  
  
    Creat `/etc/kernel/cmdline` with your kernel parameters
    ```
    # cp /proc/cmdline /etc/kernel/cmdline
    ```
    then delete entries `initrd=` in `/etc/kernel/cmdline`, you may need to add write permission `chmod u+w /etc/kernel/cmdline`.
    
    Regenerate the initramfs
    ```
    # mkinitcpio -P
    ```
    Add pacman hooks to update and re-sign systemd-boot when systemd is updated
    
    `/etc/pacman.d/hooks/100-systemd-boot.hook`
    ```
    [Trigger]
    Type = Package
    Operation = Upgrade
    Target = systemd

    [Action]
    Description = Gracefully upgrading systemd-boot...
    When = PostTransaction
    Exec = /usr/bin/systemctl restart systemd-boot-update.service
    ```
    
    `/etc/pacman.d/hooks/99-secureboot.hook`
    ```
    [Trigger]
    Operation = Install
    Operation = Upgrade
    Type = Package
    Target = linux*
    Target = systemd

    [Action]
    Description = Signing Kernel for SecureBoot
    When = PostTransaction
    Exec = /usr/bin/find /boot -type f ( -name 'archlinux-linux*.efi' -o -name systemd* -o -name BOOTX64.EFI ) -exec /usr/bin/sh -c 'if ! /usr/bin/sbverify --list {} 2>/dev/null | /usr/bin/grep -q "signature certificates"; then /usr/bin/sbsign --key /etc/efi-keys/db.key --cert /etc/efi-keys/db.crt --output "$1" "$1"; fi' _ {} ;
    Depends = sbsigntools
    Depends = findutils
    Depends = grep
    ```
    
    Sign the unified kernel image and boot manager also check the pacman hook works with reinstalling `systemd` package
    ```
    pacman -S systemd
    ```

  - Update boot entry
   
    update default boot entry in systemd-boot loader `/boot/loader/loader.conf`
    ```
    default  archlinux-linux.efi
    ...
    ```
    and optionally clear entries in `/boot/loader/entries`.
  - (optional) [enroll Microsoft's key for UEFI drivers, option ROMs etc.](https://wiki.archlinux.org/title/Unified_Extensible_Firmware_Interface/Secure_Boot#Dual_booting_with_other_operating_systems)

    
 
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
  
- Encrypt non-root partition, like external hard drive
  
  - Create a key file
  
    ```
    # dd bs=512 count=4 if=/dev/random of=/path/to/mykeyfile iflag=fullblock
    # chmod 600 /path/to/mykeyfile
    ```
  
  - Setup LUKS encryption on partition `/dev/sdX1`
  
    ```
    # cryptsetup --type luks2 --verify-passphrase --sector-size 4096 --key-file=/path/to/mykeyfile --verbose luksFormat /dev/sdX1
    ```
  - Create filesystem
    ```
    # cryptsetup open --key-file /path/to/mykeyfile /dev/sdX1 crypt_device_name
    # mkfs.btrfs --label crypt_device_label /dev/mapper/crypt_device_name
    # cryptsetup close crypt_device_name
    ```
  - Now you could decrypt device using 
    ```
    # cryptsetup open --key-file /path/to/mykeyfile LABEL=crypt_device_label crypt_mapping_name
    ```
    then mount with
    ```
    # mount /dev/mapper/crypt_mapping_name /mnt
    ```
  - Or add entry to `/etc/crypttab`

    ```
    # <name>              <device>                    <password>             <options>
    crypt_mapping_name     LABEL=crypt_device_label    /path/to/mykeyfile     noauto
    ```
    Now you can decrypt the drive using 
    ```
    # systemctl start systemd-cryptsetup@crypt_mapping_name.service
    ```
  - (Optional) [Enroll TPM 2.0 key](https://wiki.archlinux.org/title/Trusted_Platform_Module#systemd-cryptenroll)
    ```
    # systemd-cryptenroll --tpm2-device=auto --tpm2-pcrs=0+7 /dev/sdX1
    ```
    test the key
    ```
    # /usr/lib/systemd/systemd-cryptsetup attach crypt_device_name /dev/sdX1 - tpm2-device=auto
    ```
    now you should be able to `mount /dev/mapper/crypt_mapping_name /mnt`
  
    update `/etc/crypttab`
    ```
    # <name>              <device>                    <password>             <options>
    crypt_mapping_name     LABEL=crypt_device_label    -                      noauto,tpm2-device=auto
    ```
  
