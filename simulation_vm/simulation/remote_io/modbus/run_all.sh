#!/bin/bash

sim_path=/home/vagrant/GRFICSv2/simulation_vm/simulation/remote_io/modbus
<<<<<<< HEAD
=======
sudo pkill simulation
./../../simulation &
>>>>>>> 464fd55 (recent updates)
sudo pkill python3
sudo python3 $sim_path/feed1.py &
sudo python3 $sim_path/feed2.py &
sudo python3 $sim_path/purge.py &
sudo python3 $sim_path/product.py &
sudo python3 $sim_path/tank.py &
<<<<<<< HEAD
sudo python3 $sim_path/analyzer.py &
=======
sudo python3 $sim_path/analyzer.py &
>>>>>>> 464fd55 (recent updates)
