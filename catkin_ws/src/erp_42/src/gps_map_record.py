#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MORAI SIM GPS → UTM 변환 → Path 누적 + txt 저장 노드
(첫 점을 원점으로 삼아 오프셋 적용)
"""
import rospy
from pyproj import Transformer
from math import hypot
from nav_msgs.msg import Path
from geometry_msgs.msg import PoseStamped
from morai_msgs.msg import GPSMessage          # ★ MORAI 전용

class MapMakerMorai:
    def __init__(self):
        rospy.init_node('map_maker_morai', anonymous=True)

        # ───── 구독자 ──────────────────────────────────────────
        rospy.Subscriber('/gps', GPSMessage, self.gps_callback)

        # ───── Path 메시지 초기화 ──────────────────────────────
        self.path_msg               = Path()
        self.path_msg.header.frame_id = 'map'

        # ───── 좌표변환기: (lon, lat) → UTM 52N ───────────────
        self.tf = Transformer.from_crs(
            'epsg:4326',       # WGS-84 (lon, lat, deg)
            'epsg:32652',      # UTM zone 52N (meters)   ← 한국 중부권
            always_xy=True)

        # ───── 오프셋 및 이전점 저장용 ─────────────────────────
        self.east0 = None   # 첫 번째 점의 UTM X
        self.north0 = None  # 첫 번째 점의 UTM Y
        self.prev_x = 0.0
        self.prev_y = 0.0

        # ───── 파일 출력 ──────────────────────────────────────
        # save_path = '/home/unita/catkin_ws/src/erp_42/src/map/sh.txt'
        # save_path = '/home/unita/catkin_ws/src/erp_42/src/map/test 2.txt'
        save_path = '/home/han/catkin_ws/src/erp_42/src/map/test502.txt'
        # save_path = '/home/unita/catkin_ws/src/erp_42/src/map/test.txt'
        self.f = open(save_path, 'w')

        rospy.loginfo('[MapMaker] node started')
        rospy.spin()         # 콜백만 돌면 되므로 loop 不要

        # 노드 종료 시 파일 닫기
        self.f.close()

    # ──────────────────────────────────────────────────────────
    def gps_callback(self, msg: GPSMessage):
        """
        morai_msgs/GPSMessage
        float64 latitude   [deg]
        float64 longitude  [deg]
        float64 altitude   [m]
        (eastOffset, northOffset 등 추가 필드가 있어도 여기서는 사용 X)
        """
        # 1) 위도·경도 → UTM
        utm_x, utm_y = self.tf.transform(msg.longitude, msg.latitude)
        z            = msg.altitude

        # 2) 첫 점을 원점(0,0)으로 삼아 오프셋 고정
        if self.east0 is None:
            self.east0  = utm_x
            self.north0 = utm_y
            rospy.loginfo(f'[MapMaker] offset set  east0={self.east0:.3f}  '
                          f'north0={self.north0:.3f}')

        x = utm_x - self.east0
        y = utm_y - self.north0

        # 3) 10 cm 이상 움직였을 때만 기록
        if hypot(x - self.prev_x, y - self.prev_y) < 0.10:
            return

        # ─── 파일 저장 (tab 구분) ───────────────────────────
        self.f.write(f'{x:.3f}\t{y:.3f}\t{z:.3f}\n')

        # ─── Path 메시지에 포인트 추가 ────────────────────
        pose                 = PoseStamped()
        pose.header.frame_id = 'map'
        pose.pose.position.x = x
        pose.pose.position.y = y
        pose.pose.position.z = z
        pose.pose.orientation.w = 1.0
        self.path_msg.poses.append(pose)

        # (필요하면 별도 퍼블리셔로 self.path_msg 송신 가능)

        # ─── 상태 갱신 & 로그 ──────────────────────────────
        self.prev_x, self.prev_y = x, y
        rospy.loginfo_throttle(1.0,
            f'[MapMaker] (x,y)=({x:.3f},{y:.3f})  '
            f'(ΔE,ΔN)=({x-self.prev_x:+.3f},{y-self.prev_y:+.3f})')

# ─────────────────────────────────────────────────────────────
if __name__ == '__main__':
    try:
        MapMakerMorai()
    except rospy.ROSInterruptException:
        pass
