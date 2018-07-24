#!/usr/bin/env python
import numpy as np
import actionlib
import rospy
import tf
from move_base_msgs.msg import MoveBaseAction, MoveBaseGoal
from std_msgs.msg import String
import nav_msgs.srv
from nav_msgs.msg import Path
from geometry_msgs.msg import PoseStamped


class Pose:
    def __init__(self, x=0.0, y=0.0, theta=0.0):
        self.x = x
        self.y = y
        self.theta = theta


class MovoTeleop:
    def __init__(self):
        self.rate = rospy.Rate(10)
        self.pose = Pose()
        # self.curr_state = 'standby'
        self.listener = tf.TransformListener()
        # self.ready_to_go = False
        self.pose_stamped = None

    def update_pose(self):
        while not rospy.is_shutdown():
            try:
                (trans, rot) = self.listener.lookupTransform('/map', '/base_link', rospy.Time(0))
                z_rot = tf.transformations.euler_from_quaternion(rot)[2]
                self.pose.x, self.pose.y = round(trans[0], 4), round(trans[1], 4)
                self.pose.theta = np.rad2deg(z_rot)
                self.pose_stamped = PoseStamped()
                self.pose_stamped.header.stamp = rospy.Time.now()
                self.pose_stamped.header.frame_id = '/map'
                self.pose_stamped.pose.position.x = trans[0]
                self.pose_stamped.pose.position.y = trans[1]
                self.pose_stamped.pose.position.z = trans[2]
                self.pose_stamped.pose.orientation.x = rot[0]
                self.pose_stamped.pose.orientation.y = rot[1]
                self.pose_stamped.pose.orientation.z = rot[2]
                self.pose_stamped.pose.orientation.w = rot[3]
                self.rate.sleep()
                return
            except (tf.LookupException, tf.ConnectivityException, tf.ExtrapolationException):
                continue

    # def move2goal(self, goal_x, goal_y, goal_theta):
    #     # assert self.curr_state == 'navigating'
    #     print 'moving to ({},{},{})'.format(goal_x, goal_y, goal_theta)
    #     try:
    #         result = movebase_client(goal_x, goal_y, goal_theta)
    #         if result:
    #             rospy.loginfo('Goal execution done!')
    #     except rospy.ROSInterruptException:
    #         rospy.loginfo('Navigation got interrupted.')

    def move2goal(self, pose_stamped):
        try:
            result = movebase_client(pose_stamped)
            if result:
                rospy.loginfo('Goal execution done!')
        except rospy.ROSInterruptException:
            rospy.loginfo('Navigation got interrupted.')


def movebase_client(pose_stamped):
    move_base_client.wait_for_server()
    goal = MoveBaseGoal(target_pose=pose_stamped)
    move_base_client.send_goal(goal)
    wait = client.wait_for_result()
    if not wait:
        rospy.logerr("Action server not available!")
        rospy.signal_shutdown("Action server not available!")
    else:
        movo_nav_finished_publisher.publish("")
        return client.get_result()

# def movebase_client(goal_x, goal_y, goal_theta):
#     client = actionlib.SimpleActionClient('movo_move_base', MoveBaseAction)
#     client.wait_for_server()

#     goal = MoveBaseGoal()
#     goal.target_pose.header.frame_id = "map"
#     goal.target_pose.header.stamp = rospy.Time.now()
#     goal.target_pose.pose.positioheadern.x = goal_x
#     goal.target_pose.pose.position.y = goal_y

#     # print 'GOAL:', goal_theta
#     yaw = np.deg2rad(goal_theta)
#     quaternion = tf.transformations.quaternion_from_euler(0, 0, yaw)
#     # print 'Q GOAL:', quaternion
#     goal.target_pose.pose.orientation.x = quaternion[0]
#     goal.target_pose.pose.orientation.y = quaternion[1]
#     goal.target_pose.pose.orientation.z = quaternion[2]
#     goal.target_pose.pose.orientation.w = quaternion[3]

#     client.send_goal(goal)
#     wait = client.wait_for_result()
#     if not wait:
#         rospy.logerr("Action server not available!")
#         rospy.signal_shutdown("Action server not available!")
#     else:
#         movo_nav_finished_publisher.publish("")
#         return client.get_result()

def waypoint_callback(data):
    waypointPath = data
    # path_to_visualize = generate_navigation_plan(movo.pose_stamped, waypointPath.poses[0])
    for pose_stamped in waypointPath.poses:
        pose_stamped.header.stamp = rospy.Time.now()  # TODO: is this necessary?
        path_to_visualize = generate_navigation_plan(movo.pose_stamped, pose_stamped)
        movo_plan_publisher.publish(path_to_visualize)
        print 'Simulated path published! Num poses:', len(path_to_visualize.poses)
        movo.move2goal(pose_stamped)

# def waypoint_callback(data):
#     print 'waypoint callback:', data.data
#     pose = data.data.split(';')
#     print 'pose:', pose
#     movo.curr_state = 'navigating'
#     # print 'set state to navigating'
#     for p in pose:
#         pose_data = p.split(',')
#         assert len(pose_data) == 3
#         goal_x = float(pose_data[0])
#         goal_y = float(pose_data[1])
#         goal_theta = float(pose_data[2])
#         movo.move2goal(goal_x, goal_y, goal_theta)
#     # print 'set state to standby'
#     movo.curr_state = 'standby'


# def state_request_callback(data):
#     if not movo.ready_to_go:
#         print 'Movocontrol is initialized and ready to go!'
#         movo.ready_to_go = True
#     assert (movo.curr_state in ['standby', 'navigating'])
#     movo_state_publisher.publish(movo.curr_state)


# def poserequest_callback(data):
#     # print 'poserequest_callback'
#     movo.update_pose()
#     movo_pose_publisher.publish('{},{},{}'.format(movo.pose.x, movo.pose.y, movo.pose.theta))


# def initialize_request_callback(data):
#     print 'resetting movocontrol_nav...'
#     # movo.__init__()
#     # movo.ready_to_go = False


# def waypoint_pose_stamp_callback(data):
#     print 'waypoint pose stamp callback'
#     assert isinstance(data.data, PoseStamped)
#     path = generate_navigation_plan(movo.pose_stamped, data.data)
#     print 'PATH:', path
#     movo_plan_publisher.publish(path)


def generate_navigation_plan(start, goal, tolerance=0.3):
    """
    :type start: geometry_msgs.msg.PoseStamped
    :type goal: geometry_msgs.msg.PoseStamped
    :type tolerance: float
    :return: nav_msgs.msg.Path
    """
    try:
        return get_plan(start, goal, tolerance)
    except rospy.ServiceException as exc:
        print 'Service did not process request: ' + str(exc)


if __name__ == '__main__':
    try:
        listener = tf.TransformListener()
        rospy.init_node('movo_controller', anonymous=True)
        movo = MovoTeleop()
        move_base_client = actionlib.SimpleActionClient('movo_move_base', MoveBaseAction)
        # movo_state_publisher = rospy.Publisher('holocontrol/ros_movo_state_pub', String, queue_size=1)
        movo_pose_publisher = rospy.Publisher('holocontrol/ros_movo_pose_pub', String, queue_size=0)
        # movo_pose_publisher = rospy.Publisher('holocontrol/ros_movo_pose_pub', PoseStamped, queue_size=0)
        movo_plan_publisher = rospy.Publisher('holocontrol/simulated_nav_path', Path, queue_size=1)
        # rospy.Subscriber('holocontrol/movo_state_request', String, state_request_callback)
        # rospy.Subscriber('holocontrol/movo_pose_request', String, poserequest_callback)
        movo_nav_finished_publisher = rospy.Publisher('holocontrol/nav_finished', String, queue_size=1)
        # rospy.Subscriber('holocontrol/unity_waypoint_pub', String, waypoint_callback)
        rospy.Subscriber('holocontrol/unity_waypoint_pub', Path, waypoint_callback)
        # rospy.Subscriber('holocontrol/init_movocontrol_request', String, initialize_request_callback)
        # rospy.Subscriber('holocontrol/waypoint_pose_stamped', PoseStamped, waypoint_pose_stamp_callback)
        path_planning_service = '/move_base/GlobalPlanner/make_plan'
        get_plan = rospy.ServiceProxy(path_planning_service, nav_msgs.srv.GetPlan)
    except (rospy.ROSInterruptException, KeyboardInterrupt):
        print 'ROS exception :('
    while not rospy.is_shutdown():
        # movo_pose_publisher.publish(movo.pose_stamped)
        movo_pose_publisher.publish(movo.pose)
        # movo_state_publisher.publish(movo.curr_state)
        rospy.sleep()
