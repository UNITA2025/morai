#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import rospy, os, math, numpy as np
from math import sqrt, atan2, sin
from geometry_msgs.msg import Point
from nav_msgs.msg import Path
from morai_msgs.msg import CtrlCmd, EgoVehicleStatus
from visualization_msgs.msg import MarkerArray

class PurePursuit:
    def __init__(self):
        rospy.init_node('pure_pursuit', anonymous=True)

        self.cmd_pub = rospy.Publisher('/ctrl_cmd', CtrlCmd, queue_size=1)
        rospy.Subscriber('/local_path', Path, self.path_callback)
        rospy.Subscriber('/Ego_topic', EgoVehicleStatus, self.status_callback)
        rospy.Subscriber('/red_markers', MarkerArray, self.obstacle_callback)

        self.is_path = False
        self.is_status = False
        self.is_obstacle = False
        self.closest_obstacle_y = 0.0
        self.closest_obstacle_dist = float('inf')

        self.obstacle_distance_threshold = 15.0

        self.forward_point = Point()
        self.vehicle_length = 1.63
        self.lfd = 3.5
        self.cur_speed = 0.0

        self.vehicle_y = 0.0
        self.direction = ""

        self.ctrl_cmd_msg = CtrlCmd()
        rate = rospy.Rate(10)

        while not rospy.is_shutdown():
            if self.is_path and self.is_status:
                if self.is_obstacle:
                    rospy.logwarn("⚠ 장애물 감지됨! 감속 및 회피 조향")
                    self.pure_pursuit_control(slowdown=True, avoid=True)
                else:
                    self.pure_pursuit_control(slowdown=False, avoid=False)
            else:
                if not self.is_path:
                    print("[1] '/local_path' 미수신")
                if not self.is_status:
                    print("[2] '/Ego_topic' 미수신")
            rate.sleep()

    def pure_pursuit_control(self, slowdown=False, avoid=False):
        self.is_look_forward_point = False

        for pose in self.path.poses:
            dx = pose.pose.position.x
            dy = pose.pose.position.y
            if sqrt(dx*dx + dy*dy) >= self.lfd:
                self.forward_point = pose.pose.position
                self.is_look_forward_point = True
                break

        if not self.is_look_forward_point:
            rospy.logwarn("전방 추적점 없음 → 차량 정지")
            self.publish_stop()
            return

        theta = atan2(self.forward_point.y, self.forward_point.x)

        if avoid and self.closest_obstacle_dist < self.obstacle_distance_threshold:
            avoid_weight = (self.obstacle_distance_threshold - self.closest_obstacle_dist) / self.obstacle_distance_threshold
            max_avoid_angle_deg = 30
            avoid_angle_rad = math.radians(max_avoid_angle_deg) * avoid_weight

            if self.closest_obstacle_y > 0:
                theta -= avoid_angle_rad  # 왼쪽 장애물 → 오른쪽 회피
            else:
                theta += avoid_angle_rad  # 오른쪽 장애물 → 왼쪽 회피

            # 장애물 거리 기반으로 lfd, 속도 조절
            self.lfd = np.clip(8.0 - 0.4 * self.closest_obstacle_dist, 3.0, 6.0)
            speed_kmh = np.clip(1.0 + 0.4 * self.closest_obstacle_dist, 1.0, 5.0)
        else:
            self.lfd = max(4.0, 0.8 * self.cur_speed)
            speed_kmh = 20.0

        steer_rad = atan2(2 * self.vehicle_length * sin(theta), self.lfd)
        steer_rad = np.clip(steer_rad, np.radians(-40), np.radians(40))

        self.ctrl_cmd_msg.longlCmdType = 2
        self.ctrl_cmd_msg.steering = steer_rad
        self.ctrl_cmd_msg.velocity = speed_kmh
        self.ctrl_cmd_msg.accel = 0.0
        self.ctrl_cmd_msg.brake = 0.0
        self.cmd_pub.publish(self.ctrl_cmd_msg)

        os.system('clear')
        rospy.loginfo(f"▶ θ={theta:.3f} rad | steer={np.degrees(steer_rad):.1f}° | "
                      f"lfd={self.lfd:.2f} m | 회피={'YES' if avoid else 'NO'} | "
                      f"속도={speed_kmh:.1f} km/h | 장애물={self.closest_obstacle_dist:.1f} m, y={self.closest_obstacle_y:.2f}")

        rospy.loginfo(f"⚠ 회피={'YES' if self.is_obstacle else 'NO'} | "
                      f"장애물 위치: {self.direction} | "
                      f"거리: {self.closest_obstacle_dist:.2f} m | y={self.closest_obstacle_y:.2f}")

    def obstacle_callback(self, msg):
        self.is_obstacle = False
        self.closest_obstacle_dist = float('inf')
        self.closest_obstacle_y = 0.0

        valid_markers = [m for m in msg.markers if m.action == 0]
        if not valid_markers:
            rospy.loginfo("🟢 유효한 장애물 없음")
            return

        for marker in valid_markers:
            x = marker.pose.position.x
            y = marker.pose.position.y
            distance = math.sqrt(x**2 + y**2)
            if distance < self.closest_obstacle_dist:
                self.closest_obstacle_dist = distance
                self.closest_obstacle_y = y

        if self.closest_obstacle_dist <= self.obstacle_distance_threshold:
            self.is_obstacle = True

        self.direction = "왼쪽 (Left)" if self.closest_obstacle_y > 0 else "오른쪽 (Right)"

    def publish_stop(self):
        self.ctrl_cmd_msg.steering = 0.0
        self.ctrl_cmd_msg.velocity = 0.0
        self.ctrl_cmd_msg.brake = 1.0
        self.cmd_pub.publish(self.ctrl_cmd_msg)

    def path_callback(self, msg):
        self.path = msg
        self.is_path = True

    def status_callback(self, msg):
        self.vehicle_y = msg.position.y
        self.cur_speed = msg.velocity.x
        self.is_status = True

if __name__ == '__main__':
    try:
        PurePursuit()
    except rospy.ROSInterruptException:
        pass



# ~20250630 현재 위치기준으로 장애물 왼쪽/오른쪽 판단.
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-

# import rospy, os, math, numpy as np
# from math import sqrt, atan2, sin
# from geometry_msgs.msg import Point
# from nav_msgs.msg import Path
# from morai_msgs.msg import CtrlCmd, EgoVehicleStatus
# from visualization_msgs.msg import Marker, MarkerArray

# class PurePursuit:
#     def __init__(self):
#         rospy.init_node('pure_pursuit', anonymous=True)

#         self.cmd_pub = rospy.Publisher('/ctrl_cmd', CtrlCmd, queue_size=1)
#         rospy.Subscriber('/local_path', Path, self.path_callback)
#         rospy.Subscriber('/Ego_topic', EgoVehicleStatus, self.status_callback)
#         rospy.Subscriber('/red_markers', MarkerArray, self.obstacle_callback)

#         self.is_path = False
#         self.is_status = False
#         self.is_obstacle = False
#         self.closest_obstacle_y = 0.0
#         self.closest_obstacle_dist = float('inf')

#         self.obstacle_distance_threshold = 15.0

#         self.forward_point = Point()
#         self.vehicle_length = 1.63
#         self.lfd = 3.5
#         self.cur_speed = 0.0

#         self.vehicle_y = 0.0

#         self.direction = 0.0

#         self.ctrl_cmd_msg = CtrlCmd()
#         rate = rospy.Rate(10)

#         while not rospy.is_shutdown():
#             if self.is_path and self.is_status:
#                 if self.is_obstacle:
#                     rospy.logwarn("⚠ 장애물 감지됨! 감속 및 회피 조향")
#                     self.pure_pursuit_control(slowdown=True, avoid=True)
#                 else:
#                     self.pure_pursuit_control(slowdown=False, avoid=False)
#             else:
#                 if not self.is_path:
#                     print("[1] '/local_path' 미수신")
#                 if not self.is_status:
#                     print("[2] '/Ego_topic' 미수신")
#             rate.sleep()

#     def pure_pursuit_control(self, slowdown=False, avoid=False):
#         # self.lfd = max(2.0, 0.8 * self.cur_speed)
#         self.lfd = max(4.0, 0.8 * self.cur_speed)
#         self.is_look_forward_point = False

#         for pose in self.path.poses:
#             dx = pose.pose.position.x
#             dy = pose.pose.position.y
#             if sqrt(dx*dx + dy*dy) >= self.lfd:
#                 self.forward_point = pose.pose.position
#                 self.is_look_forward_point = True
#                 break

#         if not self.is_look_forward_point:
#             rospy.logwarn("전방 추적점 없음 → 차량 정지")
#             self.publish_stop()
#             return

#         theta = atan2(self.forward_point.y, self.forward_point.x)

#         if avoid and self.closest_obstacle_dist < self.obstacle_distance_threshold:
#             avoid_weight = (self.obstacle_distance_threshold - self.closest_obstacle_dist) / self.obstacle_distance_threshold
#             max_avoid_angle_deg = 30
#             avoid_angle_rad = math.radians(max_avoid_angle_deg) * avoid_weight

#             if self.closest_obstacle_y > 0:
#                 theta -= avoid_angle_rad  # 왼쪽 장애물 → 오른쪽 회피
#             else:
#                 theta += avoid_angle_rad  # 오른쪽 장애물 → 왼쪽 회피

#         steer_rad = atan2(2 * self.vehicle_length * sin(theta), self.lfd)
#         steer_rad = np.clip(steer_rad, np.radians(-40), np.radians(40))

#         # ✅ 속도 제어 로직 개선
#         if slowdown and self.closest_obstacle_dist < self.obstacle_distance_threshold:
#             speed_kmh = 5.0  # 장애물 회피 시 10km/h 고정
#         else:
#             speed_kmh = 20.0  # 장애물 없을 때는 25km/h

#         self.ctrl_cmd_msg.longlCmdType = 2
#         self.ctrl_cmd_msg.steering = steer_rad
#         self.ctrl_cmd_msg.velocity = speed_kmh 
#         self.ctrl_cmd_msg.accel = 0.0
#         self.ctrl_cmd_msg.brake = 0.0
#         self.cmd_pub.publish(self.ctrl_cmd_msg)


#         os.system('clear')
#         rospy.loginfo(f"▶ θ={theta:.3f} rad | steer={np.degrees(steer_rad):.1f}° | "
#               f"lfd={self.lfd:.2f} m | 회피={'YES' if avoid else 'NO'} | "
#               f"속도={speed_kmh:.1f} km/h | 장애물={self.closest_obstacle_dist:.1f} m, y={self.closest_obstacle_y:.2f}")

#         rospy.loginfo(f"⚠ 회피={'YES' if self.is_obstacle else 'NO'} | "
#             f"장애물 위치: {self.direction} | "
#             f"거리: {self.closest_obstacle_dist:.2f} m | y={self.closest_obstacle_y:.2f}")
        


#     def obstacle_callback(self, msg):
#         self.is_obstacle = False
#         self.closest_obstacle_dist = float('inf')
#         self.closest_obstacle_y = 0.0

#         valid_markers = [m for m in msg.markers if m.action == 0]  # Marker.ADD

#         if not valid_markers:
#             rospy.loginfo("🟢 유효한 장애물 없음")
#             return

#         for marker in valid_markers:
#             x = marker.pose.position.x
#             y = marker.pose.position.y
#             distance = math.sqrt(x**2 + y**2)
#             if distance < self.closest_obstacle_dist:
#                 self.closest_obstacle_dist = distance
#                 self.closest_obstacle_y = y

#         if self.closest_obstacle_dist <= self.obstacle_distance_threshold:
#             self.is_obstacle = True

#         self.direction = "왼쪽 (Left)" if self.closest_obstacle_y > 0 else "오른쪽 (Right)"
 



#     def publish_stop(self):
#         self.ctrl_cmd_msg.steering = 0.0
#         self.ctrl_cmd_msg.velocity = 0.0
#         self.ctrl_cmd_msg.brake = 1.0
#         self.cmd_pub.publish(self.ctrl_cmd_msg)

#     def path_callback(self, msg):
#         self.path = msg
#         self.is_path = True

#     def status_callback(self, msg):
#         self.vehicle_y = msg.position.y
#         self.cur_speed = msg.velocity.x
#         self.is_status = True

# if __name__ == '__main__':
#     try:
#         PurePursuit()
#     except rospy.ROSInterruptException:
#         pass




# 장애물 인식 ok. 주행 어색함.
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-

# import rospy, os, math, numpy as np
# from math import sqrt, atan2, sin
# from geometry_msgs.msg import Point
# from nav_msgs.msg import Path
# from morai_msgs.msg import CtrlCmd, EgoVehicleStatus
# from visualization_msgs.msg import Marker, MarkerArray

# class PurePursuit:
#     def __init__(self):
#         rospy.init_node('pure_pursuit', anonymous=True)

#         self.cmd_pub = rospy.Publisher('/ctrl_cmd', CtrlCmd, queue_size=1)
#         rospy.Subscriber('/local_path', Path, self.path_callback)
#         rospy.Subscriber('/Ego_topic', EgoVehicleStatus, self.status_callback)
#         rospy.Subscriber('/red_markers', MarkerArray, self.obstacle_callback)

#         self.is_path = False
#         self.is_status = False
#         self.is_obstacle = False
#         self.obstacle_distance_threshold = 15.0
#         self.closest_obstacle_y = 0.0

#         self.forward_point = Point()
#         self.vehicle_length = 1.63
#         self.lfd = 3.5
#         self.cur_speed = 0.0

#         self.ctrl_cmd_msg = CtrlCmd()
#         rate = rospy.Rate(10)

#         while not rospy.is_shutdown():
#             self.avoid = False
#             if self.is_path and self.is_status:
#                 if self.is_obstacle:
#                     rospy.logwarn("⚠ 장애물 감지됨! 감속 및 회피 조향")
#                     self.pure_pursuit_control(slowdown=True, avoid=True)
#                 else:
#                     self.pure_pursuit_control(slowdown=False, avoid=False)
#             else:
#                 os.system('clear')
#                 if not self.is_path:
#                     print("[1] '/local_path' 미수신")
#                 if not self.is_status:
#                     print("[2] '/Ego_topic' 미수신")
#             rate.sleep()

#     def pure_pursuit_control(self, slowdown=False, avoid=False):
#         self.lfd = max(2.0, 0.8 * self.cur_speed)
#         self.is_look_forward_point = False

#         for pose in self.path.poses:
#             dx = pose.pose.position.x
#             dy = pose.pose.position.y
#             if sqrt(dx*dx + dy*dy) >= self.lfd:
#                 self.forward_point = pose.pose.position
#                 self.is_look_forward_point = True
#                 break

#         if not self.is_look_forward_point:
#             rospy.logwarn("전방 추적점 없음 → 차량 정지")
#             self.publish_stop()
#             return

#         theta = atan2(self.forward_point.y, self.forward_point.x)

#         if avoid:
#             # 좌우 회피
#             if self.closest_obstacle_y > 0:
#                 theta -= math.radians(10)  # 왼쪽 장애물 → 오른쪽 회피
#             else:
#                 theta += math.radians(10)  # 오른쪽 장애물 → 왼쪽 회피

#         steer_rad = atan2(2 * self.vehicle_length * sin(theta), self.lfd)
#         steer_rad = np.clip(steer_rad, np.radians(-30), np.radians(30))

#         self.ctrl_cmd_msg.longlCmdType = 2
#         self.ctrl_cmd_msg.steering = steer_rad
#         self.ctrl_cmd_msg.velocity = 1.39 if slowdown else 15.0  # 5km/h or normal
#         self.ctrl_cmd_msg.accel = 0.0
#         self.ctrl_cmd_msg.brake = 0.0
#         self.cmd_pub.publish(self.ctrl_cmd_msg)

#         os.system('clear')
#         print(f"▶ θ={theta:.3f} rad | steer={np.degrees(steer_rad):.1f}° | "
#               f"lfd={self.lfd:.2f} m | 회피={'YES' if avoid else 'NO'} | "
#               f"속도={self.ctrl_cmd_msg.velocity*3.6:.1f} km/h")

#     def obstacle_callback(self, msg):
#         self.is_obstacle = False

#         # 유효한 마커만 검사 (ADD만)
#         valid_markers = [m for m in msg.markers if m.action == Marker.ADD]

#         if not valid_markers:
#             rospy.loginfo("🟢 유효한 장애물 없음 (마커는 있지만 전부 DELETE)")
#             return

#         for marker in valid_markers:
#             x = marker.pose.position.x
#             y = marker.pose.position.y
#             distance = math.sqrt(x**2 + y**2)
#             if distance <= self.obstacle_distance_threshold:
#                 self.is_obstacle = True
#                 break

#         rospy.loginfo(f"⚠ 회피={'YES' if self.is_obstacle else 'NO'} (유효 마커 수: {len(valid_markers)})")


#     def publish_stop(self):
#         self.ctrl_cmd_msg.steering = 0.0
#         self.ctrl_cmd_msg.velocity = 0.0
#         self.ctrl_cmd_msg.brake = 1.0
#         self.cmd_pub.publish(self.ctrl_cmd_msg)

#     def path_callback(self, msg):
#         self.path = msg
#         self.is_path = True

#     def status_callback(self, msg):
#         self.cur_speed = msg.velocity.x
#         self.is_status = True

# if __name__ == '__main__':
#     try:
#         PurePursuit()
#     except rospy.ROSInterruptException:
#         pass



# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-

# import rospy, os, math, numpy as np
# from math import sqrt, atan2, sin
# from geometry_msgs.msg import Point
# from nav_msgs.msg import Path
# from sensor_msgs.msg import PointCloud2
# import sensor_msgs.point_cloud2 as pc2
# from morai_msgs.msg import CtrlCmd, EgoVehicleStatus
# from visualization_msgs.msg import MarkerArray

# class PurePursuit:
#     def __init__(self):
#         rospy.init_node('pure_pursuit', anonymous=True)

#         # 퍼블리셔 / 서브스크라이버
#         self.cmd_pub = rospy.Publisher('/ctrl_cmd', CtrlCmd, queue_size=1)
#         rospy.Subscriber('/local_path', Path, self.path_callback)
#         rospy.Subscriber('/Ego_topic',  EgoVehicleStatus, self.status_callback)
#         # rospy.Subscriber('/filtered_lidar3D', PointCloud2, self.obstacle_callback)
#         rospy.Subscriber('/red_markers', MarkerArray, self.marker_callback)

#         # 상태 변수
#         self.is_path   = False
#         self.is_status = False
#         self.is_obstacle = False  # 장애물 여부 플래그
#         self.obstacle_side = None

#         self.forward_point  = Point()
#         self.vehicle_length = 1.63
#         self.lfd            = 3.5
#         self.cur_speed      = 0.0

#         self.ctrl_cmd_msg = CtrlCmd()
#         rate = rospy.Rate(10)

#         while not rospy.is_shutdown():
#             if self.is_path and self.is_status:
#                 if self.is_obstacle:
#                     self.avoidance_obstacle()
#                 else:
#                     self.pure_pursuit_control()
#             else:
#                 os.system('clear')
#                 if not self.is_path:   print("[1] '/local_path' 미수신")
#                 if not self.is_status: print("[2] '/Ego_topic'  미수신")
#             rate.sleep()

#     # -------------------- Pure Pursuit 제어 --------------------
#     def pure_pursuit_control(self):
#         self.lfd = max(2.0, 0.8 * self.cur_speed)

#         self.is_look_forward_point = False
#         for pose in self.path.poses:
#             dx = pose.pose.position.x
#             dy = pose.pose.position.y
#             if sqrt(dx*dx + dy*dy) >= self.lfd:
#                 self.forward_point = pose.pose.position
#                 self.is_look_forward_point = True
#                 break

#         if not self.is_look_forward_point:
#             rospy.logwarn("No forward point found")
#             self.publish_stop()
#             return

#         theta      = atan2(self.forward_point.y, self.forward_point.x)
#         steer_rad  = atan2(2 * self.vehicle_length * sin(theta), self.lfd)
#         steer_rad  = np.clip(steer_rad, np.radians(-30), np.radians(30))

#         self.ctrl_cmd_msg.longlCmdType = 2
#         self.ctrl_cmd_msg.steering     = steer_rad
#         self.ctrl_cmd_msg.velocity     = 20.0    # ✅ 장애물 없을 때: 20 km/h
#         self.ctrl_cmd_msg.accel        = 0.0
#         self.ctrl_cmd_msg.brake        = 0.0
#         self.cmd_pub.publish(self.ctrl_cmd_msg)

#         os.system('clear')
#         print(f"[NORMAL] θ={theta:.3f} rad | steer={np.degrees(steer_rad):.1f}° | "
#               f"lfd={self.lfd:.2f} m | v={self.cur_speed*3.6:.1f} km/h")

#     # -------------------- 장애물 회피 제어 --------------------
#     def avoidance_obstacle(self):
#         self.lfd = max(2.0, 0.8 * self.cur_speed)
#         self.is_look_forward_point = False

#         # 회피 방향 설정
#         direction = 1.0 if self.obstacle_side == 'right' else -1.0  # 우측 장애물 → 좌측으로 회피

#         for pose in self.path.poses:
#             dx = pose.pose.position.x
#             dy = pose.pose.position.y
#             if sqrt(dx*dx + dy*dy) >= self.lfd and direction * dy > 1.0:
#                 self.forward_point = pose.pose.position
#                 self.is_look_forward_point = True
#                 break

#         if not self.is_look_forward_point:
#             rospy.logwarn("No forward point found (obstacle)")
#             self.publish_stop()
#             return

#         theta      = atan2(self.forward_point.y, self.forward_point.x)
#         steer_rad  = atan2(2 * self.vehicle_length * sin(theta), self.lfd)
#         steer_rad  = np.clip(steer_rad, np.radians(-30), np.radians(30))

#         self.ctrl_cmd_msg.longlCmdType = 2
#         self.ctrl_cmd_msg.steering     = steer_rad
#         self.ctrl_cmd_msg.velocity     = 5.00
#         self.ctrl_cmd_msg.accel        = 0.0
#         self.ctrl_cmd_msg.brake        = 0.0
#         self.cmd_pub.publish(self.ctrl_cmd_msg)

#         os.system('clear')
#         print(f"[AVOIDING {self.obstacle_side.upper()}] θ={theta:.3f} rad | steer={np.degrees(steer_rad):.1f}° | "
#             f"lfd={self.lfd:.2f} m | v={self.cur_speed*3.6:.1f} km/h")

#     # -------------------- 장애물 판단 --------------------
#     def obstacle_callback(self, msg):
#         points = pc2.read_points(msg, field_names=("x", "y", "z"), skip_nans=True)
#         self.is_obstacle = False
#         min_dist = float('inf')
#         closest_y = 0.0

#         for p in points:
#             x, y, z = p
#             dist = math.sqrt(x**2 + y**2 + z**2)
#             if 0 < x < 20.0 and abs(y) < 3.0:
#                 if dist < min_dist:
#                     min_dist = dist
#                     closest_y = y
#                     self.is_obstacle = True

#         # 장애물 방향 판단
#         if self.is_obstacle:
#             self.obstacle_side = 'left' if closest_y > 0 else 'right'
#             print(f"[OBSTACLE DETECTED] x={x:.2f}, y={closest_y:.2f} → side: {self.obstacle_side}")
#         else:
#             self.obstacle_side = None

#     def marker_callback(self, msg):
#         self.is_obstacle = False
#         self.obstacle_side = None

#         min_dist = float('inf')
#         closest_y = 0.0

#         for marker in msg.markers:
#             x = marker.pose.position.x
#             y = marker.pose.position.y
#             z = marker.pose.position.z

#             dist = math.sqrt(x**2 + y**2 + z**2)

#             if 0 < x < 20.0 and abs(y) < 3.0:  # ROI 범위 내 마커
#                 if dist < min_dist:
#                     min_dist = dist
#                     closest_y = y
#                     self.is_obstacle = True

#         if self.is_obstacle:
#             self.obstacle_side = 'left' if closest_y > 0 else 'right'
#             print(f"[MARKER DETECTED] x={x:.2f}, y={closest_y:.2f} → side: {self.obstacle_side}")


#     # -------------------- 헬퍼 --------------------
#     def publish_stop(self):
#         self.ctrl_cmd_msg.steering = 0.0
#         self.ctrl_cmd_msg.velocity = 0.0
#         self.ctrl_cmd_msg.brake    = 1.0
#         self.cmd_pub.publish(self.ctrl_cmd_msg)

#     def path_callback(self, msg):
#         self.path    = msg
#         self.is_path = True

#     def status_callback(self, msg):
#         self.cur_speed  = msg.velocity.x
#         self.is_status  = True

# if __name__ == '__main__':
#     try:
#         PurePursuit()
#     except rospy.ROSInterruptException:
#         pass
