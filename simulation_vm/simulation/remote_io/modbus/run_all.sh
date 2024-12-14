#!/bin/bash

sim_path=/home/vagrant/GRFICSv2/simulation_vm/simulation/remote_io/modbus
sudo pkill simulation
./../../simulation &
sudo pkill python3
sudo python3 $sim_path/feed1.py &
sudo python3 $sim_path/feed2.py &
sudo python3 $sim_path/purge.py &
sudo python3 $sim_path/product.py &
sudo python3 $sim_path/tank.py &
sudo python3 $sim_path/analyzer.py &
