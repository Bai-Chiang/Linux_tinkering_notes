# Arch Linux Post-installation configurations

- Disable bell sound

  To disable bell sound on tab-completion, uncomment the line `set bell-style none` in `/etc/inputrc`.
  Edit `/etc/vimrc` add line `set belloff=all` after `runtime! archlinux.vim`, to disable bell sound in vim.
  Then relogin to take effect.
  Add line `export LESS="$LESS -Q"` to the end of `/etc/profile` also disable the bell sound in `less`.
 
- Default editor

  Add line `export EDITOR=/usr/bin/vim` to the end of `/etc/profile` to set vim as default editor.
  
- Install `base-devel` package group, which provides soem essential packages like `sudo`, `grep` etc.
  
- [Add](https://wiki.archlinux.org/title/Users_and_groups#Example_adding_a_user) new admin user `tux`,
  ```
  # useradd -m -G wheel tux
  ```
  Edit `sudoers` file with `visudo` command.
  Uncomment `%wheel ALL=(ALL) ALL` allow members in `wheel` group gain `sudo` access,
  or `%wheel ALL=(ALL) NOPASSWD: ALL` execute any command without password (insecure!).
  
- [Enable parallel download for `pacman`](https://wiki.archlinux.org/title/Pacman#Enabling_parallel_downloads)
  
  Uncomment line `ParallelDownloads` in `/etc/pacman.conf`.
  
- Install [`reflector`](https://wiki.archlinux.org/title/reflector) to select the most up-to-date mirrors based on country.
  [Edit](https://wiki.archlinux.org/title/reflector#systemd_service) configuration file `/etc/xdg/reflector/reflector.conf`
  ```
  --save /etc/pacman.d/mirrorlist
  --country us
  --protocol https
  --latest 5
  --sort age
  ```
  and enable `reflector.timer` to update mirrorlist weekly.
  
- [Install](https://wiki.archlinux.org/title/Pacman#Cleaning_the_package_cache) ` pacman-contrib` package,
  then enable `paccache.timer` to delete unused pacman cache weekly.

- Enable `fstrim.timer` provided by `util-linux` package for [Periodic SSD TRIM](https://wiki.archlinux.org/title/Solid_state_drive#Periodic_TRIM).

- To setup btrfs snapshot and rollback solution, install `snapper` and `cronie` package,
  then follow [this](https://wiki.archlinux.org/title/snapper#Configuration_of_snapper_and_mount_point) guide.
  ```
  # umount /.snapshots
  # rm -r /.snapshots
  # snapper -c root create-config /
  # btrfs subvolume delete /.snapshots
  # mkdir /.snapshots
  ```
  The btrfs subvolumes layout in [the Arch Linux installation note](https://github.com/Bai-Chiang/Linux_tinkering_notes/blob/main/Arch_Linux_installation.md)
  already follows [this](https://wiki.archlinux.org/title/snapper#Suggested_filesystem_layout) suggested guide layout, so the mount entry already in `fstab`.
  ```
  # mount -a
  # chmod -R 750 /.snapshots
  ```
  Also create new config for home
  ```
  # snapper -c home create-config /home
  ```
  [Edit](https://wiki.archlinux.org/title/snapper#Set_snapshot_limits) snapshots limit for both root and home in config files
  `/etc/snapper/configs/root`and `/etc/snapper/configs/home`.
  ```
  NUMBER_MIN_AGE="1800"
  NUMBER_LIMIT="10"
  NUMBER_LIMIT_IMPORTANT="10"
  
  TIMELINE_MIN_AGE="1800"
  TIMELINE_LIMIT_HOURLY="5"
  TIMELINE_LIMIT_DAILY="7"
  TIMELINE_LIMIT_WEEKLY="0"
  TIMELINE_LIMIT_MONTHLY="0"
  TIMELINE_LIMIT_YEARLY="0"
  ```
  To restore to previous state, follow [this](https://wiki.archlinux.org/title/snapper#Restoring_/_to_its_previous_snapshot) guide.

- [Automatically creating snapshots upon a pacman transaction](https://wiki.archlinux.org/title/snapper#Wrapping_pacman_transactions_in_snapshots)

  Install `rsync` and `snap-pac` package, then create pacman hook `/etc/pacman.d/hooks/50-bootbackup.hook` to backup /boot partition
  ```
  [Trigger]
  Operation = Upgrade
  Operation = Install
  Operation = Remove
  Type = Path
  Target = usr/lib/modules/*/vmlinuz

  [Action]
  Depends = rsync
  Description = Backing up /boot...
  When = PostTransaction
  Exec = /usr/bin/rsync -a --delete /boot /.bootbackup
  ```
  
- Wifi set up, use [iwd](https://wiki.archlinux.org/title/Iwd) or [wpa_supplicant](https://wiki.archlinux.org/title/Wpa_supplicant#At_boot_(systemd))
  (I can't connect to [MSCHAPv2](https://wiki.archlinux.org/title/Iwd#EAP-PEAP) network with `iwd`, but it works with `wpa_supplicant`.) 
