ssh mb@mb
rosrun baxter_tools tuck_arms.py -u
roslaunch vxlab.launch

[NGV box]
log in as "demo"
run Unity Hub 
open project "ros_reality" (Unity 2021.1.5F1)
From the project hierarchy, select websocket client, verify correct URI ws://10.42.1.254:9090 (alternatively 10.234.2.49)
From project hierarchy, select robot factory, verify URDF Parser absolute path to "standard_baxter_urdf.xml" (searchable with ros_reality project)
Press play on Unity IDE
Black meshlike texture flat stands in for the lack of Kinect data

Troubleshooting
- if greyed out, restart app, Unity or (close) SteamVR
- check using the correct controller
- network degradation, requires restart/pause or network cable directly between PC and mb switch

[Kinect, Rosie]
ssh vxlab@rosie (or ssh vxlab@rosiew)
cd ~/vxlab/rosie/people_perception
./run

[Kinect, Unity]
Enabling point cloud (Unity): Reference Transform, underneath: Kinect2_link_pivot, check/unceck "Depth Ros Geometry View (Script)"

Action:
- Jack, tidy up for packaging
- IanP/Jack, test wired networking
