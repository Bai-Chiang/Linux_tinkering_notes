Setup Fedora CoreOS as a disposable VM to run container applications.

- Install [libvirt](https://wiki.archlinux.org/title/Libvirt) and [QEMU](https://wiki.archlinux.org/title/QEMU).
- Install [podman](https://wiki.archlinux.org/title/Podman)
- You may need to reboot machine after theses installation.
- [Crate an Ignition Config](https://docs.fedoraproject.org/en-US/fedora-coreos/producing-ign/)
  This is a two step process. First create a YAML-formatted Butane config which is easy to understand by human.
  Then run Butane to convert this YAML file into a JSON Ignition config that is easy for machine to read.
  - Pull Butane container
    ```
    podman pull quay.io/coreos/butane:release
    ```
  - Create an alias
    ```
    alias butane='podman run --rm --interactive       \
                  --security-opt label=disable        \
                  --volume ${PWD}:/pwd --workdir /pwd \
                  quay.io/coreos/butane:release'
    ```
  - Create `example.bu`
    ```
    variant: fcos
    version: 1.4.0
    passwd:
      users:
        - name: core
          ssh_authorized_keys:
            - ssh-ed25519 AAAA...
    storage:
      files:
        - path: /etc/hostname
          mode: 0644
          contents:
            inline: myhostname
    systemd:
      units:
        - name: hello.service
          enabled: true
          contents: |
            [Unit]
            Description=MyApp
            After=network-online.target
            Wants=network-online.target

            [Service]
            TimeoutStartSec=0
            ExecStartPre=-/bin/podman kill busybox1
            ExecStartPre=-/bin/podman rm busybox1
            ExecStartPre=/bin/podman pull busybox
            ExecStart=/bin/podman run --name busybox1 busybox /bin/sh -c "trap 'exit 0' INT TERM; while true; do echo Hello World; sleep 1; done"

            [Install]
            WantedBy=multi-user.target
    ```
    First two lines are the OS variants and specification version for butane config, see [this](https://coreos.github.io/butane/specs/).
    Then we add ssh authentication key to the default user `core`. The line `- ssh-ed22519 AAA...` is the line in `~/.ssh/id_ed25519.pub` after you set up your ssh key authentication.
    Next, we specify the host name as `myhostname`.
    We also created a systemd service `hello.service` which will start at boot.
    
    If you want to assign [network configuration](https://docs.fedoraproject.org/en-US/fedora-coreos/sysconfig-network-configuration/) add these lines under `files:` section
    ```
    - path: /etc/NetworkManager/system-connections/enp1s0.nmconnection
      mode: 0600
      contents:
        inline: |
          [connection]
          id=enp1s0
          type=ethernet
          interface-name=enp1s0
          [ipv4]
          address1=192.168.122.10/24,192.168.122.1
          dhcp-hostname=myhostname
          dns=9.9.9.9;
          dns-search=
          may-fail=false
          method=manual
    ```
  - Generate `example.ign`
    ```
    butane --pretty --strict example.bu > example.ign
    ```
- [Download](https://getfedora.org/en/coreos/download) and verify Fedora CoreOS stable version.
  You may need to extract it `unxz fedora-coreos-*.qcow2.xz`.
- Create new VM. Paste these lines to `example_ignition.sh`
  ```
  IGNITION_CONFIG="/path/to/example.ign"
  IMAGE="/path/to/image.qcow2"
  VM_NAME="fcos-example"
  VCPUS="2"
  RAM_MB="2048"
  DISK_GB="10"
  
  virt-install \
    --connect qemu:///system \
    --name ${VM_NAME} \
    --memory ${RAM_MB} \
    --cpu host,topology.sockets=1,topology.cores=${VCPUS},topology.threads=1 \
    --os-variant detect=off,require=on,name=fedora-coreos-stable \
    --network network=default,model.type=virtio \
    --import \
    --graphics none \
    --noautoconsole \
    --disk size=${DISK_GB},bus=virtio,backing_store=${IMAGE} \
    --qemu-commandline="-fw_cfg name=opt/com.coreos/config,file=${IGNITION_CONFIG}"
  ```
  If you want to connect to a bridge network called `br0` in the host, change the `--network` line to 
  `--network bridge=br0,model.type=virtio \`
  
  then run the script with
  ```
  bash example_ignition.sh
  ```
- Find out the virtual machine ip adress from `virt-manager`. Now you shoud be able to login with
  ```
  ssh core@ip.address
  ```
  and you can check the `hello.service` we defined in `butane.bu` is running with
  ```
  systemctl status hello.service
  ```
