#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import rospy, os
from pyproj import Proj
from std_msgs.msg import Float32MultiArray
from visualization_msgs.msg import Marker
import tf
from tf.transformations import euler_from_quaternion
from math import sqrt, pow, atan2, sin, cos
from nav_msgs.msg import Path                      # (주석 블록 그대로 둠)
import threading
import math

# ─── MORAI 전용 메시지 타입 추가 ──────────────────────────────────
from morai_msgs.msg import GPSMessage              # GPS
from sensor_msgs.msg import Imu                    # IMU(quaternion)

class GPS_to_UTM:
    def __init__(self):
        rospy.init_node('GPS_to_UTM', anonymous=True)

        # ───── 구독자 설정 (MORAI) ────────────────────────────────
        self.gps_sub = rospy.Subscriber("/gps", GPSMessage,     # ★ 변경
                                        self.gps_callback, queue_size=1)
        rospy.Subscriber("/imu", Imu,                           # ★ 변경
                         self.angle_callback,  queue_size=1)

        # ───── 퍼블리셔 ──────────────────────────────────────────
        self.gps_pub    = rospy.Publisher("/gps_map",   Float32MultiArray, queue_size=1)
        self.marker_pub = rospy.Publisher("/gps_marker", Marker,           queue_size=1)

        # ───── 기타 초기화 ───────────────────────────────────────
        self.proj_UTM = Proj(proj='utm', zone=52, ellps='WGS84', preserve_units=False)
        self.utm_msg  = Float32MultiArray()

        self.is_gps_data = False
        self.is_imu_data = False

        # 필요시 고정 오프셋 / 첫 점 오프셋
        self.east_offset  = 302473.617
        self.north_offset = 4123735.842

        # east0=302473.493  north0=4123735.536

        self.yaw = 0.0  # Yaw(rad)

        # TF 브로드캐스터
        self.tf_broadcaster = tf.TransformBroadcaster()

        # 데이터 수신 상태 확인
        self.check_data_thread = threading.Thread(target=self.check_data_status)
        self.check_data_thread.daemon = True
        self.check_data_thread.start()

        rospy.spin()

    def check_data_status(self):
        rate = rospy.Rate(1)  # 1 Hz
        while not rospy.is_shutdown():
            if not self.is_gps_data:
                rospy.logwarn("[1] Can't subscribe '/gps' topic... check MORAI GPS")
            if not self.is_imu_data:
                rospy.logwarn("[2] Can't subscribe '/imu' topic... check IMU sensor")
            self.is_gps_data = False
            self.is_imu_data = False
            rate.sleep()

    # ───── IMU 콜백 (quaternion → yaw) ──────────────────────────
    def angle_callback(self, msg: Imu):
        ori_q = msg.orientation
        (_, _, yaw) = euler_from_quaternion([ori_q.x, ori_q.y, ori_q.z, ori_q.w])
        self.yaw = yaw
        self.is_imu_data = True

    # ───── GPS 콜백 (lat/lon → UTM → map) ──────────────────────
    def gps_callback(self, gps_msg: GPSMessage):
        self.is_gps_data = True
        latitude  = gps_msg.latitude
        longitude = gps_msg.longitude
        altitude  = gps_msg.altitude

        utm_x, utm_y = self.proj_UTM(longitude, latitude)
        map_x = utm_x - self.east_offset
        map_y = utm_y - self.north_offset

        # ----- 좌표 퍼블리시 -------------------------------------------------
        self.utm_msg.data = [map_x, map_y]
        self.gps_pub.publish(self.utm_msg)

        # ----- 디버그용 yaw(deg) 출력 ----------------------------------------
        yaw_deg = math.degrees(self.yaw) % 360
        rospy.loginfo(f"Current Yaw in gps_callback: {yaw_deg:.2f}°")

        # ----- RViz Marker ---------------------------------------------------
        marker = Marker()
        marker.header.frame_id = "map"
        marker.header.stamp    = rospy.Time.now()
        marker.ns   = "vehicle"
        marker.id   = 0
        marker.type = Marker.CUBE
        marker.action = Marker.ADD
        marker.pose.position.x = map_x
        marker.pose.position.y = map_y
        marker.pose.position.z = 0.0

        q = tf.transformations.quaternion_from_euler(0, 0, self.yaw)
        marker.pose.orientation.x = q[0]
        marker.pose.orientation.y = q[1]
        marker.pose.orientation.z = q[2]
        marker.pose.orientation.w = q[3]

        marker.scale.x, marker.scale.y, marker.scale.z = 2.0, 1.0, 1.0
        marker.color.a, marker.color.r, marker.color.g, marker.color.b = 1.0, 0.0, 1.0, 0.0
        self.marker_pub.publish(marker)

        # ----- TF 브로드캐스트 -----------------------------------------------
        self.tf_broadcaster.sendTransform(
            (map_x, map_y, 0.0),
            q,
            rospy.Time.now(),
            "vehicle_frame",
            "map"
        )

        # ----- 콘솔 출력 ------------------------------------------------------
        os.system('clear')
        print(f'''
   -------------[ GPS ]--------------
   lat : {latitude}
   lon : {longitude}
   alt : {altitude}

        | WGS84 → UTM 52N
        V
   -------------[ UTM ]--------------
   X : {utm_x}
   Y : {utm_y}

        | apply offset
        V
   -------------[ MAP ]--------------
   map_x : {map_x}
   map_y : {map_y}
''')

if __name__ == '__main__':
    try:
        GPS_to_UTM = GPS_to_UTM()
    except rospy.ROSInterruptException:
        pass
