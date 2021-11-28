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
  # passwd tux
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
  
- Install AUR helper [`paru`](https://github.com/morganamilo/paru)
  ```
  mkdir -p ~/.cache/paru
  cd ~/.cache/paru
  git clone https://aur.archlinux.org/paru.git
  cd paru
  makepkg -si
  ```
  
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
 
- dotfiles restore, based on [this](https://antelo.medium.com/how-to-manage-your-dotfiles-with-git-f7aeed8adf8b) guide

  - Login as user `tux`.
  
  - clone git-directory
    ```
    $ git clone --bare <dotfiles-repo-url> $HOME/.dotfiles
    $ alias dotfiles='/usr/bin/git --git-dir=$HOME/.dotfiles/ --work-tree=$HOME'
    ```
  - checkout. Because there may be some files like `.bashrc` or `.gitignore` in the home directory,
    first remove (since this is fresh installed system, we simply delete them) these conflicted files then checkout.
    ```
    $ dotfiles checkout 2>&1 | egrep "\s+\." | awk {'print $1'} | xargs -I{} rm {}
    $ dotfiles checkout
    ```
  - Let `git status` ignore untracked file  
    ```
    $ dotfiles config --local status.showUntrackedFiles no
    ```
  - Or you can put all these command in a single script like [this](https://github.com/Bai-Chiang/Linux_tinkering_notes/blob/main/restore_dotfiles.sh), then
    ```
    cd ~
    wget https://raw.githubusercontent.com/Bai-Chiang/Linux_tinkering_notes/main/restore_dotfiles.sh
    bash restore_dotfiles.sh
    ```
  - After setting up the desktop environment and ssh key (see below),
    follow [this](https://docs.github.com/en/authentication/connecting-to-github-with-ssh/adding-a-new-ssh-key-to-your-github-account) guide copy public key to GitHub via web interface.
    Then change the remove url in `~/.dotfiles/config`
    ```
    ...
    [remote "origin"]
        url = git@github.com:Bai-Chiang/dotfiles.git
    ...
    ```
    Then you can push to github repository using 
    ```
    dotfiles push
    ```
    You may need extra setup for the first time, follow the hints/suggestions.
  
- [SSH key](https://wiki.archlinux.org/title/SSH_keys)

  install `openssh` package.

  [Generate](https://wiki.archlinux.org/title/SSH_keys#Ed25519) new key pair
  ```
  $ ssh-keygen -t ed25519
  ```
  to [copy public key to remote server](https://wiki.archlinux.org/title/SSH_keys#Copying_the_public_key_to_the_remote_server) with ssh port 2222
  ```
  ssh-copy-id -i ~/.ssh/id_ed25519.pub -p 2222 username@remote-server.org
  ```
  
- Wifi set up, use [iwd](https://wiki.archlinux.org/title/Iwd) or [wpa_supplicant](https://wiki.archlinux.org/title/Wpa_supplicant#At_boot_(systemd))
  (I can't connect to [MSCHAPv2](https://wiki.archlinux.org/title/Iwd#EAP-PEAP) network with `iwd`, but it works with `wpa_supplicant`.) 
  Install `iwd` and enable `iwd.service`. Check whether wifi is block using command `rfkill list`. To unblock all wifi/bluetooth use `rfkill unblock all`, and reboot.
  Login as admin user `tux`.
  
  Connect wifi with an interactive prompt with command `iwctl`, follow [this](https://wiki.archlinux.org/title/Iwd#iwctl) to connect to wifi. eduroam setup follow [this](https://wiki.archlinux.org/title/Iwd#EAP-PEAP) guide.
  
- GUI
  - [Install driver](https://wiki.archlinux.org/title/Xorg#Driver_installation)
  - Install desktop environment/window manager
  - set up [XDG user directories](https://wiki.archlinux.org/title/XDG_user_directories) by installing `xdg-user-dirs` then run `xdg-user-dirs-update`.
  - Install [`xdg-utils`](https://wiki.archlinux.org/title/Xdg-utils), read [this](https://wiki.archlinux.org/title/Xdg-utils#xdg-settings) to set up default application.
  - Install extra [fonts](https://wiki.archlinux.org/title/Fonts) (like `ttf-hack` `ttf-jetbrains-mono`), [CJK](https://wiki.archlinux.org/title/Fonts#Pan-CJK) fonts (`noto-fonts-cjk`), [Emoji and Kaomoji](https://wiki.archlinux.org/title/Fonts#Emoji_and_symbols), and [`ttf-font-awesome`](https://archlinux.org/packages/community/any/ttf-font-awesome/).
  - [PipeWire](https://wiki.archlinux.org/title/PipeWire) and `pavucontrol`
  - [Flatpak](https://wiki.archlinux.org/title/Flatpak#Update_a_runtime_or_application)
    
    Add flatpak repo
    ```
    flatpak remote-add --user --if-not-exists flathub https://dl.flathub.org/repo/flathub.flatpakrepo
    ```
  - Theming
  
    When using window manager, there is no theming engine, and all GUI applications launch as default theme.
    I don't need all applications have consistant theming, but I do want them using dark theme instead of default light theme.
    For [GTK applications](https://wiki.archlinux.org/title/GTK#Themes) add `GTK_THEME=Adwaita:dark` to environment variable, also create `~/.config/settings.ini` then follow [this](https://wiki.archlinux.org/title/GTK#Basic_theme_configuration) guide set up a basic configuration.
    For Qt application using Adwaita-dark theme feels odd, I prefer using Breeze dark theme, but there is no easy way to specify the theme.
    So I copied `~/.config/kdeglobals` from another machine with Breeze-dark theme, then set `QT_QPA_PLATFORMTHEME=kde`.
    The config files `settings.ini` and `kdeglobals` could be backup using [this](https://antelo.medium.com/how-to-manage-your-dotfiles-with-git-f7aeed8adf8b) method, so you only need to set up once.

