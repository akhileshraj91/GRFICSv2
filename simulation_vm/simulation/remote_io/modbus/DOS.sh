#!/bin/bash

sim_path=/home/vagrant/GRFICSv2/simulation_vm/simulation/remote_io/modbus
sudo pkill simulation
./../../simulation &
sudo pkill python3
python3 $sim_path/feed1.py &
python3 $sim_path/feed2.py &