#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import rospy
from math import sqrt
from geometry_msgs.msg import PoseStamped
from nav_msgs.msg import Path
from std_msgs.msg import Float32MultiArray
from sensor_msgs.msg import NavSatFix

class ReadPathPublisher:
    def __init__(self):
        rospy.init_node('read_path_pub', anonymous=True)
        
        # 퍼블리셔 설정
        self.global_path_pub = rospy.Publisher('/global_path', Path, queue_size=1)
        # 글로벌 경로 메시지 초기화
        self.global_path_msg = Path()
        self.global_path_msg.header.frame_id = 'map'

        # 경로 점 읽기
        # self.read_path_from_file('/home/unita/catkin_ws/src/erp_42/src/map/sh.txt')
        # self.read_path_from_file('/home/unita/catkin_ws/src/erp_42/src/map/test 2.txt')
        #self.read_path_from_file('/home/unita/catkin_ws/src/erp_42/src/map/test 3.txt')
        #self.read_path_from_file('/home/unita/catkin_ws/src/erp_42/src/map/test 2.txt')
        self.read_path_from_file('/home/han/catkin_ws/src/erp_42/src/map/test502.txt')
        # self.read_path_from_file('/home/unita/catkin_ws/src/erp_42/src/map/test.txt')

        # 현재 퍼블리시할 인덱스 초기화
        self.current_index = 0

        # GPS 데이터를 위한 변수 초기화
        self.current_x = 0.0
        self.current_y = 0.0
        self.gps_received = False

        # GPS 구독자 설정 (GPS_to_UTM 노드에서 퍼블리시하는 /gps_map 토픽)
        rospy.Subscriber("/gps_map", Float32MultiArray, self.gps_utm_callback)

        # 타이머를 사용하여 주기적으로 글로벌 경로 퍼블리시 (예: 10Hz)
        self.publish_timer = rospy.Timer(rospy.Duration(0.1), self.publish_global_path)

        rospy.loginfo("ReadPathPublisher initialized.")

    def read_path_from_file(self, file_path):
        with open(file_path, 'r') as f:
            lines = f.readlines()

        for idx, line in enumerate(lines):
            tmp = line.strip().split()
            if len(tmp) >= 2:
                x = float(tmp[0])
                y = float(tmp[1])
                read_pose = PoseStamped()
                read_pose.header.frame_id = 'map'
                read_pose.header.seq = idx  # 시퀀스 번호 추가
                read_pose.header.stamp = rospy.Time.now()
                read_pose.pose.position.x = x
                read_pose.pose.position.y = y
                read_pose.pose.position.z = 0.0
                read_pose.pose.orientation.w = 1.0
                self.global_path_msg.poses.append(read_pose)

        rospy.loginfo(f"Number of points in the path: {len(self.global_path_msg.poses)}")
    
    def gps_utm_callback(self, msg):
        # GPS_to_UTM 노드에서 변환된 좌표를 받아서 현재 위치로 사용
        if len(msg.data) >= 2:
            self.current_x = msg.data[0]
            self.current_y = msg.data[1]
            self.gps_received = True
            rospy.loginfo(f"GPS Updated: x = {self.current_x}, y = {self.current_y}")
        else:
            rospy.logwarn("Received GPS data with insufficient length.")

    def publish_global_path(self, event):
        if not self.gps_received:
            return  # GPS 데이터가 수신될 때까지 대기

        # 헤더의 타임스탬프 업데이트
        self.global_path_msg.header.stamp = rospy.Time.now()

        # 차량의 현재 위치를 기준으로 가장 가까운 경로 점의 인덱스 찾기
        self.current_index = self.find_closest_waypoint(self.current_x, self.current_y)

        # 슬라이싱을 사용하여 경로의 일부만 선택
        slice_length = 120  # 한 번에 퍼블리시할 경로 점의 개수

        # 슬라이스 범위 계산
        start_idx = self.current_index
        end_idx = start_idx + slice_length

        # 경로의 끝을 넘어가지 않도록 조정
        if end_idx > len(self.global_path_msg.poses):
            end_idx = len(self.global_path_msg.poses)

        sliced_poses = self.global_path_msg.poses[start_idx:end_idx]

        # 새로운 Path 메시지 생성
        sliced_path = Path()
        sliced_path.header.frame_id = 'map'
        sliced_path.header.stamp = rospy.Time.now()
        sliced_path.poses = sliced_poses

        # 글로벌 경로 퍼블리시
        self.global_path_pub.publish(sliced_path)

    def find_closest_waypoint(self, x, y):
        min_distance = float('inf')
        closest_idx = 0

        for i, waypoint in enumerate(self.global_path_msg.poses):
            dx = waypoint.pose.position.x - x
            dy = waypoint.pose.position.y - y
            distance = sqrt(dx**2 + dy**2)
            if distance < min_distance:
                min_distance = distance
                closest_idx = i

        return closest_idx

if __name__ == '__main__':
    try:
        read_path_publisher = ReadPathPublisher()
        rospy.spin()
    except rospy.ROSInterruptException:
        pass
