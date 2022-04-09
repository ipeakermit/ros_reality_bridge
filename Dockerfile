# https://hub.docker.com/r/davetcoleman/baxter_simulator/~/dockerfile/
# vicariousinc/baxter-simulator:kinetic
# Run simulated Baxter in Gazebo

#FROM osrf/ros:kinetic-desktop-full-jessie
FROM osrf/ros:kinetic-desktop-full
MAINTAINER Dave Coleman dave@dav.ee

ENV TERM xterm

# Setup catkin workspace
ENV CATKIN_WS=/root/ws_baxter
WORKDIR $CATKIN_WS/src

# Download source code
#RUN wstool init . && \
#    wstool merge https://raw.githubusercontent.com/vicariousinc/baxter_simulator/${ROS_DISTRO}-gazebo7/baxter_simulator.rosinstall && \
#    wstool update

# LAST KNOWN GOOD - Baxter component git commits
#baxter
#commit d2f2ebd1166b944096febc8a3b014a5d9d810e64
#baxter_common
#commit 15825273de1fe6b8b1b2c6069692d767c69ff503
#baxter_examples
#commit 033756294b59f038869d97e59b5d9b28fe64d9e5
#baxter_interface
#commit aea70d96eb0fb0a99084dcb02d467785dde8fe52
#baxter_simulator
#commit 762854f16ce09e152cfab065bd70471ff7051657
#baxter_tools
#commit 0da6ea300e1f8050ffe8d78421dcc6b8fec983a2

COPY 02proxy /etc/apt/apt.conf.d/02proxy

# Update apt-get because previous images clear this cache
# Commands are combined in single RUN statement with "apt/lists" folder removal to reduce image size
RUN apt-get -qq update && \
    # Install some base dependencies
    apt-get -qq install -y \
        # Some source builds require a package.xml be downloaded via wget from an external location
        wget \
        # Required for rosdep command
        sudo

RUN sudo apt-key del 421C365BD9FF1F717815A3895523BAEEB01FA116
RUN sudo -E apt-key adv --keyserver 'hkp://keyserver.ubuntu.com:80' --recv-key C1CF6E31E6BADE8868B172B4F42ED6FBAB17C654

RUN apt-get -qq update && \
    apt -qq install -y \
        # Required for installing dependencies
        python-rosdep \
        # Preferred build tool
        python-catkin-tools
    # Download all dependencies

RUN apt -qq update && apt -y dist-upgrade
RUN apt-get update && apt-get -y install vim-tiny

COPY src $CATKIN_WS/src
 
# explicit dependency on moveit?
#RUN apt-get update && \
    #apt install -y ros-${ROS_DISTRO}-moveit-core

#RUN apt -qq update && \
#    rosdep update && \
#    rosdep install -y --from-paths . --ignore-src --rosdistro ${ROS_DISTRO} --as-root=apt:false --os=ubuntu:xenial && \
#    # Clear apt-cache to reduce image size
#    rm -rf /var/lib/apt/lists/*

# Replacing shell with bash for later docker build commands
RUN mv /bin/sh /bin/sh-old && \
    ln -s /bin/bash /bin/sh

# Build repo
WORKDIR $CATKIN_WS
ENV PYTHONIOENCODING UTF-8
RUN catkin config --extend /opt/ros/${ROS_DISTRO} --cmake-args -DCMAKE_BUILD_TYPE=Release && \
    # Status rate is limited so that just enough info is shown to keep Docker from timing out, but not too much
    # such that the Docker log gets too long (another form of timeout)
    # changed --jobs flag to 4 to speed up the build process
    catkin build --jobs 4 --limit-status-rate 0.001 --no-notify

COPY rosenv-baxter-master.bash rosenv-baxter-master.bash
RUN chmod +x rosenv-baxter-master.bash
COPY launch.bash launch.bash
COPY tf.launch tf.launch
RUN chmod +x launch.bash
