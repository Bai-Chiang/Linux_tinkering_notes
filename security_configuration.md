# Basic security setup

see [ArchWiki-security](https://wiki.archlinux.org/title/Security) for more details and complete security practice.

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
- [non-root partition encryption]
