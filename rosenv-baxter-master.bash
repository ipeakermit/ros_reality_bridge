#!/bin/bash

source /opt/ros/${ROS_DISTRO}/setup.bash
source ~/ws_baxter/devel/setup.bash

#export ROS_MASTER_URI=http://127.0.0.1:11311
#export ROS_IP=127.0.0.1

# Preferred "universal" URI for mobility base (requires slightly smarter routing)
export ROS_MASTER_URI=http://10.42.1.1:11311/

# rosie brain - wireless interface
#export ROS_IP=10.234.2.48

# rosie brain - wired interface
export ROS_IP=10.42.1.4

export MB_LASER_BIRDCAGE_R2000=1
export MB_LASER_BIRDCAGE_R2000_IP=10.42.1.2
export MB_LASER_BIRDCAGE_R2000_FREQ=50
export MB_LASER_BIRDCAGE_R2000_SAMPLES=3600
