#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import rospy, tf, math
import numpy as np
from math import sqrt, pow, atan2, sin, cos
from nav_msgs.msg import Path
from std_msgs.msg import Float32MultiArray, Float32
from geometry_msgs.msg import PoseStamped
from visualization_msgs.msg import Marker
from sensor_msgs.msg import Imu                      # ★ MORAI IMU(quaternion) 추가
from tf.transformations import euler_from_quaternion


class PathPublisher:
    def __init__(self):
        rospy.init_node('path_pub', anonymous=True)

        # Subscribers ---------------------------------------------------------
        rospy.Subscriber("/gps_map",   Float32MultiArray, self.gps_callback)
        rospy.Subscriber("/global_path", Path,            self.global_path_callback)
        # rospy.Subscriber("/fused_path", Path, self.fused_path_callback)
        rospy.Subscriber("/imu", Imu,                     self.imu_callback)  # ★ 변경

        # Publishers ----------------------------------------------------------
        self.local_path_pub         = rospy.Publisher('/local_path', Path,    queue_size=1)
        self.current_pos_marker_pub = rospy.Publisher('/current_position_marker',
                                                      Marker, queue_size=1)

        # Initialize variables -----------------------------------------------
        self.global_path_msg = Path()
        self.is_status = False

        self.x = 0.0
        self.y = 0.0
        self.yaw = 0.0        # Vehicle's heading angle [rad]

        # TF broadcaster
        self.tf_broadcaster = tf.TransformBroadcaster()

        rate = rospy.Rate(20)  # 20 Hz
        while not rospy.is_shutdown():
            if self.is_status:
                self.process_local_path()
            rate.sleep()

    # -------------------------------------------------------------------------
    def process_local_path(self):
        x, y = self.x, self.y

        # TF transform broadcast ---------------------------------------------
        self.tf_broadcaster.sendTransform(
            (x, y, 0),
            tf.transformations.quaternion_from_euler(0, 0, self.yaw),
            rospy.Time.now(),
            'vehicle_frame',
            'map'
        )

        # Marker for current position ----------------------------------------
        current_pos_marker = Marker()
        current_pos_marker.header.frame_id = 'map'
        current_pos_marker.header.stamp = rospy.Time.now()
        current_pos_marker.ns = 'current_position'
        current_pos_marker.id = 0
        current_pos_marker.type = Marker.CUBE
        current_pos_marker.action = Marker.ADD
        current_pos_marker.pose.position.x = x
        current_pos_marker.pose.position.y = y
        current_pos_marker.pose.position.z = 0.0
        q = tf.transformations.quaternion_from_euler(0, 0, self.yaw)
        current_pos_marker.pose.orientation.x = q[0]
        current_pos_marker.pose.orientation.y = q[1]
        current_pos_marker.pose.orientation.z = q[2]
        current_pos_marker.pose.orientation.w = q[3]
        current_pos_marker.scale.x = 1.0
        current_pos_marker.scale.y = 1.0
        current_pos_marker.scale.z = 1.0
        current_pos_marker.color.a = 1.0
        current_pos_marker.color.r = 0.0
        current_pos_marker.color.g = 0.0
        current_pos_marker.color.b = 1.0
        self.current_pos_marker_pub.publish(current_pos_marker)

        # Local path creation -------------------------------------------------
        local_path_msg = Path()
        local_path_msg.header.frame_id = 'vehicle_frame'
        local_path_msg.header.stamp = rospy.Time.now()

        for wp in self.global_path_msg.poses:
            dx = wp.pose.position.x - x
            dy = wp.pose.position.y - y
            local_x = dx * cos(-self.yaw) - dy * sin(-self.yaw)
            local_y = dx * sin(-self.yaw) + dy * cos(-self.yaw)

            p = PoseStamped()
            p.header.frame_id = 'vehicle_frame'
            p.header.stamp = rospy.Time.now()
            p.pose.position.x = local_x
            p.pose.position.y = local_y
            p.pose.position.z = 0.0
            p.pose.orientation.w = 1.0
            local_path_msg.poses.append(p)

        self.local_path_pub.publish(local_path_msg)

    # -------------------------------------------------------------------------
    def gps_callback(self, msg: Float32MultiArray):
        self.x, self.y = msg.data[0], msg.data[1]
        self.is_status = True

    def global_path_callback(self, msg: Path):
        self.global_path_msg = msg
        self.is_status = True

    # IMU(quaternion) → yaw(rad) ---------------------------------------------
    def imu_callback(self, msg: Imu):
        q = msg.orientation
        (_, _, yaw) = euler_from_quaternion([q.x, q.y, q.z, q.w])
        self.yaw = yaw
        self.is_status = True

    # def fused_path_callback(self, path_msg):
    #     ...

# -----------------------------------------------------------------------------
if __name__ == '__main__':
    try:
        PathPublisher()
    except rospy.ROSInterruptException:
        pass
