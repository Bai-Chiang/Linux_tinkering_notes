# Set up `slurm` on Arch Linux cluster

1. Install `slurm-llnl`
   ```
   # pacman -S slurm-llnl
   ```
1. Make sure all nodes have the same munge key `/etc/munge/munge.key`.
   You can simply copy the key from one node to all other nodes.
   To generate a new key run
   ```
   sudo -u munge mungekey --verbose
   ```
   You need to remove old key first.

1. Start and enable `munge.service` on all nodes.
   ```
   # systemctl enable --now munge.service
   ```

1. Generate configuration file form the [official website](https://slurm.schedmd.com/configurator.html).
   The easy version is available [here](https://slurm.schedmd.com/configurator.easy.html).
   Then put the configuration file `/etc/slurm-llnl/slurm.conf` on all nodes.

1. If using Linux cgroups for process tracking (ProctrackType=proctrack/cgroup in the slurm.conf file),
   create `/etc/slurm/cgroup.conf` on all compute nodes.
   See [`man 5 cgroup.conf`](https://slurm.schedmd.com/cgroup.conf.html) for more configuration details.

1. Start and enable `slurmd.service` on all compute nodes.
   ```
   # systemctl enable --now slurmd.service
   ```

1. Start and enable `slurmctld.service` on all control nodes.
   ```
   # systemctl enable --now slurmctld.service
   ```

