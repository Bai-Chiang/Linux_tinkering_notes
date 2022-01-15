Setup Fedora CoreOS as a disposable VM to run container applications.

- Install [libvirt](https://wiki.archlinux.org/title/Libvirt) and [QEMU](https://wiki.archlinux.org/title/QEMU).
- Install and configure [podman](https://wiki.archlinux.org/title/Podman)
- [Crate an Ignition Config](https://docs.fedoraproject.org/en-US/fedora-coreos/producing-ign/)
  This is a two step process. First create a YAML-formatted Butane config which is easy to understand by human.
  Then run Butane to convert this YAML file into a JSON Ignition config that is easy for machine to read.
  - Pull Butane container
    ```
    podman pull quay.io/coreos/butane:release
    ```
