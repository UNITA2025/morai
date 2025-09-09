#!/usr/bin/env python3
import rospy
import math
import sensor_msgs.point_cloud2 as pc2
from sensor_msgs.msg import PointCloud2
from std_msgs.msg import Header
from visualization_msgs.msg import Marker, MarkerArray
import numpy as np
from sklearn.cluster import DBSCAN
from sklearn.linear_model import RANSACRegressor

class LidarROIFilter:
    def __init__(self):
        rospy.init_node('lidar_roi_filter', anonymous=True)

        self.sub = rospy.Subscriber("/lidar3D", PointCloud2, self.callback)
        self.pub_filtered = rospy.Publisher("/filtered_lidar3D", PointCloud2, queue_size=1)
        self.pub_markers = rospy.Publisher("/red_markers", MarkerArray, queue_size=1)
        
        self.roi_angle_deg = 20
        self.vert_min_deg = -5
        self.vert_max_deg = 12

        self.dbscan_eps = 0.3
        self.dbscan_min_samples = 10

    def callback(self, msg):
        points = pc2.read_points(msg, field_names=("x", "y", "z"), skip_nans=True)
        roi_points = []

        for point in points:
            x, y, z = point
            horiz_angle = math.degrees(math.atan2(y, x))
            distance = math.sqrt(x**2 + y**2 + z**2)

            if distance == 0:
                continue

            vert_angle = math.degrees(math.asin(z / distance))

            if (-self.roi_angle_deg <= horiz_angle <= self.roi_angle_deg and
                self.vert_min_deg <= vert_angle <= self.vert_max_deg):
                roi_points.append([x, y, z])


        if roi_points:
            roi_np = np.array(roi_points)
            non_ground_points = self.remove_ground_plane(roi_np)

            if len(non_ground_points) == 0:
                return

            dbscan = DBSCAN(eps=self.dbscan_eps, min_samples=self.dbscan_min_samples)
            labels = dbscan.fit_predict(non_ground_points)

            cluster_centers = self.calculate_cluster_centers(non_ground_points, labels)
            self.publish_red_markers(cluster_centers)
            self.publish_filtered_cloud(non_ground_points)

    def remove_ground_plane(self, points):
        """
        RANSAC을 이용해 ground plane 제거
        가정: 지면은 z축 기준으로 평평한 plane (ax + by + c = z 형태)
        """
        X = points[:, :2]  # x, y
        Z = points[:, 2]   # z

        if len(X) >= 10:
            model = RANSACRegressor(residual_threshold=0.1, min_samples=50)
            model.fit(X, Z)
        else:
            print("⚠ 데이터가 너무 적어 RANSAC을 적용할 수 없습니다.")
    

        inliers = model.inlier_mask_  # 지면 포인트 (제거 대상)
        outliers = np.logical_not(inliers)

        return points[outliers]

    def calculate_cluster_centers(self, points, labels):
        cluster_centers = []
        unique_labels = np.unique(labels)
        
        for label in unique_labels:
            if label == -1:
                continue
            cluster_points = points[labels == label]
            center = np.mean(cluster_points, axis=0)
            cluster_centers.append(center)

        return cluster_centers

    def publish_filtered_cloud(self, points):
        header = Header()
        header.stamp = rospy.Time.now()
        header.frame_id = "Lidar3D-1"
        # header.frame_id = "lidar_frame"

        filtered_cloud = pc2.create_cloud_xyz32(header, points)
        self.pub_filtered.publish(filtered_cloud)

    def publish_red_markers(self, cluster_centers):
        marker_array = MarkerArray()
        
        for i, center in enumerate(cluster_centers):
            distance = math.sqrt(center[0]**2 + center[1]**2 + center[2]**2)
            if distance > 30.0:
                continue  # 100m 넘는 건 무시

            marker = Marker()
            marker.header.frame_id = "Lidar3D-1"
            # marker.header.frame_id = "lidar_frame"
            marker.header.stamp = rospy.Time.now()
            marker.ns = "cluster_centers"
            marker.id = i
            marker.type = Marker.SPHERE
            marker.action = Marker.ADD
            marker.pose.position.x = center[0]
            marker.pose.position.y = center[1]
            marker.pose.position.z = center[2]
            marker.scale.x = 0.2
            marker.scale.y = 0.2
            marker.scale.z = 0.2
            marker.color.r = 1.0
            marker.color.g = 0.0
            marker.color.b = 0.0
            marker.color.a = 1.0
            # marker.lifetime = rospy.Duration(0.5)

            marker_array.markers.append(marker)

        self.pub_markers.publish(marker_array)


    def run(self):
        rospy.spin()

if __name__ == '__main__':
    try:
        node = LidarROIFilter()
        node.run()
    except rospy.ROSInterruptException:
        pass





# #!/usr/bin/env python3
# import rospy
# import math
# import socket
# import numpy as np
# import sensor_msgs.point_cloud2 as pc2
# from sensor_msgs.msg import PointCloud2, PointField
# from std_msgs.msg import Header
# from visualization_msgs.msg import Marker, MarkerArray
# from sklearn.cluster import DBSCAN
# from sklearn.linear_model import RANSACRegressor
# import threading

# UDP_IP = "127.0.0.1"
# UDP_PORT = 9090

# class LidarROIFilter:
#     def __init__(self):
#         rospy.init_node('lidar_udp_filter_node', anonymous=True)

#         # 10초마다 마커 삭제
#         rospy.Timer(rospy.Duration(10.0), self.clear_red_markers)


#         # 퍼블리셔
#         self.pub_lidar = rospy.Publisher("/lidar3D", PointCloud2, queue_size=1)
#         self.pub_filtered = rospy.Publisher("/filtered_lidar3D", PointCloud2, queue_size=1)
#         self.pub_markers = rospy.Publisher("/red_markers", MarkerArray, queue_size=1)

#         # 서브스크라이버
#         self.sub = rospy.Subscriber("/lidar3D", PointCloud2, self.callback)

#         # ROI 파라미터
#         self.roi_angle_deg = 60
#         self.vert_min_deg = -7
#         self.vert_max_deg = +5

#         self.dbscan_eps = 0.3
#         self.dbscan_min_samples = 10

#     def start_udp_listener(self):
#         """UDP로 들어오는 LiDAR 데이터를 PointCloud2로 변환하여 퍼블리시"""
#         sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#         sock.bind((UDP_IP, UDP_PORT))
#         rospy.loginfo(f"[UDP Listener] Listening on {UDP_IP}:{UDP_PORT}")

#         while not rospy.is_shutdown():
#             try:
#                 data, addr = sock.recvfrom(65536)  # 데이터 수신
#                 if len(data) < 12:
#                     rospy.logwarn("[UDP Listener] Received packet too small.")
#                     continue

#                 # 유효한 길이 (12바이트 단위로 맞춤)
#                 valid_len = (len(data) // 12) * 12
#                 trimmed = data[:valid_len]

#                 # float32 x,y,z 형태로 변환
#                 points = np.frombuffer(trimmed, dtype=np.float32).reshape(-1, 3)

#                 # PointCloud2 메시지 생성
#                 header = Header()
#                 header.stamp = rospy.Time.now()
#                 header.frame_id = "lidar_frame"
#                 cloud_msg = pc2.create_cloud_xyz32(header, points.tolist())
#                 self.pub_lidar.publish(cloud_msg)

#             except Exception as e:
#                 rospy.logwarn(f"[UDP Listener] Error: {e}")

#     def callback(self, msg):
#         points = pc2.read_points(msg, field_names=("x", "y", "z"), skip_nans=True)
#         roi_points = []

#         for point in points:
#             x, y, z = point
#             horiz_angle = math.degrees(math.atan2(y, x))
#             distance = math.sqrt(x**2 + y**2 + z**2)

#             if distance == 0:
#                 continue

#             vert_angle = math.degrees(math.asin(z / distance))

#             if (-self.roi_angle_deg <= horiz_angle <= self.roi_angle_deg and
#                 self.vert_min_deg <= vert_angle <= self.vert_max_deg):
#                 roi_points.append([x, y, z])

#         if roi_points:
#             roi_np = np.array(roi_points)
#             non_ground_points = self.remove_ground_plane(roi_np)

#             if len(non_ground_points) == 0:
#                 return

#             dbscan = DBSCAN(eps=self.dbscan_eps, min_samples=self.dbscan_min_samples)
#             labels = dbscan.fit_predict(non_ground_points)

#             cluster_centers = self.calculate_cluster_centers(non_ground_points, labels)
#             self.publish_red_markers(cluster_centers)
#             self.publish_filtered_cloud(non_ground_points)

#     # def remove_ground_plane(self, points):
#     #     X = points[:, :2]
#     #     Z = points[:, 2]

#     #     if len(X) >= 10:
#     #         model = RANSACRegressor(residual_threshold=0.1, min_samples=50)
#     #         model.fit(X, Z)
#     #         inliers = model.inlier_mask_
#     #         outliers = np.logical_not(inliers)
#     #         return points[outliers]
#     #     else:
#     #         rospy.logwarn("⚠ 데이터가 너무 적어 RANSAC을 적용할 수 없습니다.")
#     #         return points

#     def remove_ground_plane(self, points):
#         X = points[:, :2]  # x, y
#         Z = points[:, 2]   # z
#         n_samples = len(X)

#         if n_samples >= 10:
#             min_samples = min(50, n_samples)  # n_samples보다 크지 않도록 제한
#             try:
#                 model = RANSACRegressor(residual_threshold=0.1, min_samples=min_samples)
#                 model.fit(X, Z)
#                 inliers = model.inlier_mask_
#                 outliers = np.logical_not(inliers)
#                 return points[outliers]
#             except Exception as e:
#                 rospy.logwarn(f"[Ground Removal] RANSAC failed: {e}")
#                 return points
#         else:
#             rospy.logwarn("⚠ 데이터가 너무 적어 RANSAC을 적용할 수 없습니다.")
#             return points



#     def calculate_cluster_centers(self, points, labels):
#         cluster_centers = []
#         unique_labels = np.unique(labels)
        
#         for label in unique_labels:
#             if label == -1:
#                 continue
#             cluster_points = points[labels == label]
#             center = np.mean(cluster_points, axis=0)
#             cluster_centers.append(center)

#         return cluster_centers

#     def publish_filtered_cloud(self, points):
#         header = Header()
#         header.stamp = rospy.Time.now()
#         header.frame_id = "lidar_frame"
#         cloud = pc2.create_cloud_xyz32(header, points)
#         self.pub_filtered.publish(cloud)

#     def publish_red_markers(self, cluster_centers):
#         marker_array = MarkerArray()
        
#         for i, center in enumerate(cluster_centers):
#             distance = np.linalg.norm(center)
#             if distance > 30.0:
#                 continue

#             marker = Marker()
#             marker.header.frame_id = "lidar_frame"
#             marker.header.stamp = rospy.Time.now()
#             marker.ns = "cluster_centers"
#             marker.id = i
#             marker.type = Marker.SPHERE
#             marker.action = Marker.ADD
#             marker.pose.position.x = center[0]
#             marker.pose.position.y = center[1]
#             marker.pose.position.z = center[2]
#             marker.scale.x = marker.scale.y = marker.scale.z = 0.2
#             marker.color.r = 1.0
#             marker.color.g = 0.0
#             marker.color.b = 0.0
#             marker.color.a = 1.0
#             marker_array.markers.append(marker)

#         self.pub_markers.publish(marker_array)

#     def clear_red_markers(self, event):
#         delete_array = MarkerArray()

#         for i in range(100):  # id 범위는 여유 있게 충분히 잡기 (예: 0~99)
#             marker = Marker()
#             marker.header.frame_id = "lidar_frame"
#             marker.header.stamp = rospy.Time.now()
#             marker.ns = "cluster_centers"
#             marker.id = i
#             marker.action = Marker.DELETE
#             delete_array.markers.append(marker)

#         self.pub_markers.publish(delete_array)
#         rospy.loginfo("[Marker] 클러스터 마커 삭제됨 (10초 주기)")


#     def run(self):
#         # UDP 수신 쓰레드 시작
#         udp_thread = threading.Thread(target=self.start_udp_listener)
#         udp_thread.daemon = True
#         udp_thread.start()

#         # ROS 루프
#         rospy.spin()

# if __name__ == '__main__':
#     try:
#         node = LidarROIFilter()
#         node.run()
#     except rospy.ROSInterruptException:
#         pass






