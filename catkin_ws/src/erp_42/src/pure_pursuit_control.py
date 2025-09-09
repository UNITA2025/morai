#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import rospy, os, math, numpy as np
from math import sqrt, atan2, sin
from geometry_msgs.msg import Point
from nav_msgs.msg import Path
from morai_msgs.msg import CtrlCmd, EgoVehicleStatus
from std_msgs.msg import Bool

class PurePursuit:
    def __init__(self):
        rospy.init_node('pure_pursuit', anonymous=True)

        self.cmd_pub = rospy.Publisher('/ctrl_cmd', CtrlCmd, queue_size=1)
        rospy.Subscriber('/local_path', Path, self.path_callback)
        rospy.Subscriber('/Ego_topic', EgoVehicleStatus, self.status_callback)
        rospy.Subscriber('/stop_flag', Bool, self.stop_flag_callback)

        self.is_path = False
        self.is_status = False
        self.stop_flag = False

        self.forward_point = Point()
        self.vehicle_length = 1.63
        self.lfd = 3.5
        self.cur_speed = 0.0

        self.ctrl_cmd_msg = CtrlCmd()
        rate = rospy.Rate(10)

        while not rospy.is_shutdown():
            if self.is_path and self.is_status:
                if not self.stop_flag:
                    self.pure_pursuit_control()
                else:
                    print("[STOP] 현재 정지 상태입니다.")
                    self.publish_stop()
            else:
                os.system('clear')
                if not self.is_path:
                    print("[1] '/local_path' 미수신")
                if not self.is_status:
                    print("[2] '/Ego_topic' 미수신")
            rate.sleep()

    def pure_pursuit_control(self):
        self.lfd = max(2.0, 0.8 * self.cur_speed)

        self.is_look_forward_point = False
        for pose in self.path.poses:
            dx = pose.pose.position.x
            dy = pose.pose.position.y
            if sqrt(dx*dx + dy*dy) >= self.lfd:
                self.forward_point = pose.pose.position
                self.is_look_forward_point = True
                break

        if not self.is_look_forward_point:
            rospy.logwarn("No forward point found")
            self.publish_stop()
            return

        theta = atan2(self.forward_point.y, self.forward_point.x)
        steer_rad = atan2(2 * self.vehicle_length * sin(theta), self.lfd)
        steer_rad = np.clip(steer_rad, np.radians(-30), np.radians(30))

        self.ctrl_cmd_msg.longlCmdType = 2
        self.ctrl_cmd_msg.steering = steer_rad
        self.ctrl_cmd_msg.velocity = 55.56
        self.ctrl_cmd_msg.accel = 0.0
        self.ctrl_cmd_msg.brake = 0.0
        self.cmd_pub.publish(self.ctrl_cmd_msg)

        os.system('clear')
        print(f"▶ fp=({self.forward_point.x:.2f},{self.forward_point.y:.2f}) | "
              f"θ={theta:.3f} rad | steer={np.degrees(steer_rad):.1f}° | "
              f"lfd={self.lfd:.2f} m | v={self.cur_speed*3.6:.1f} km/h")

    def publish_stop(self):
        self.ctrl_cmd_msg.steering = 0.0
        self.ctrl_cmd_msg.velocity = 0.0
        self.ctrl_cmd_msg.brake = 1.0
        self.cmd_pub.publish(self.ctrl_cmd_msg)

    def path_callback(self, msg):
        self.path = msg
        self.is_path = True

    def status_callback(self, msg):
        self.cur_speed = msg.velocity.x
        self.is_status = True

    def stop_flag_callback(self, msg):
        self.stop_flag = msg.data

if __name__ == '__main__':
    try:
        PurePursuit()
    except rospy.ROSInterruptException:
        pass
