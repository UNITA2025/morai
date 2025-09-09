#!/usr/bin/env python3
import rospy
import math
import os
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
        
        # self.roi_angle_deg = 30    # 너무 작게 해서 가까워지면 point cloud 많이 안찍혀서 장애물 인식 제대로 안되는거 같음.
        self.roi_angle_deg = 60
        self.vert_min_deg = -7
        self.vert_max_deg = +3

        # MORAI에서 수동으로 보면서 파라미터 조정.
        self.dbscan_eps = 0.5     # 0.5m 거리의 점을 하나의 cluster로 묶어줌. -> 0.5m 거리내의 장애물은 구분 안됌.
        self.dbscan_min_samples = 70    # 0.5m 거리내에 80개의 점이 존재하면 red marker가 찍히게 된다.

    def callback(self, msg):
        # Convert PointCloud2 to list of (x, y, z)
        points = []
        for p in pc2.read_points(msg, field_names=("x", "y", "z"), skip_nans=True):
            x, y, z = p
            horiz_angle = math.degrees(math.atan2(y, x))
            vert_angle = math.degrees(math.atan2(z, math.hypot(x, y)))
            
            if abs(horiz_angle) <= self.roi_angle_deg and self.vert_min_deg <= vert_angle <= self.vert_max_deg:
                points.append([x, y, z])
        
        if not points:
            return

        points_np = np.array(points)

        # Remove ground using RANSAC
        try:
            ransac = RANSACRegressor(residual_threshold=0.1)    # 작을수록 땅 잘지움. 클수록 약간만 굴곡있어도 평지로 판단해줘서 안좋음.
            ransac.fit(points_np[:, [0, 1]], points_np[:, 2])
            inlier_mask = ransac.inlier_mask_
            ground_removed = points_np[~inlier_mask]
        except Exception as e:
            rospy.logwarn(f"RANSAC failed: {e}")
            ground_removed = points_np

        # DBSCAN Clustering
        clustering = DBSCAN(eps=self.dbscan_eps, min_samples=self.dbscan_min_samples)
        labels = clustering.fit_predict(ground_removed)

        unique_labels = set(labels)
        markers = MarkerArray()
        header = msg.header

        # # ✅ 기존 마커 삭제
        delete_all_marker = Marker()
        delete_all_marker.action = Marker.DELETEALL
        delete_all_marker.header = header
        # delete_all_marker.header.frame_id = "map"  # global_path와 동일한 frame으로 지정
        markers.markers.append(delete_all_marker)

        original_indices = np.arange(len(points_np))
        non_ground_indices = original_indices[~inlier_mask]

        obstacle_count = 0

        for idx, label in enumerate(unique_labels):
            if label == -1:
                continue  # noise

            cluster_mask = (labels == label)
            cluster_points = ground_removed[cluster_mask]
            # if cluster_points.shape[0] < 0.2:
            #     continue
            centroid = np.mean(cluster_points, axis=0)
            distance = np.linalg.norm(centroid[:2])
            if distance > 15.0 :
                continue

            # Marker 생성
            marker = Marker()
            marker.header = header
            # marker.header.frame_id = "map"  # 또는 'odom', 'world' 등 global_path에서 사용하는 frame
            marker.ns = "clusters"
            marker.id = idx
            marker.type = Marker.SPHERE
            marker.action = Marker.ADD
            marker.pose.position.x = centroid[0]
            marker.pose.position.y = centroid[1]
            marker.pose.position.z = centroid[2]
            marker.pose.orientation.w = 1.0
            marker.scale.x = marker.scale.y = marker.scale.z = 0.3
            marker.color.r = 1.0
            marker.color.g = 0.0
            marker.color.b = 0.0
            marker.color.a = 0.8
            markers.markers.append(marker)

            obstacle_count += 1

        self.pub_markers.publish(markers)

        # 퍼블리시 필터링된 포인트클라우드
        filtered_pc2 = pc2.create_cloud_xyz32(header, ground_removed.tolist())
        self.pub_filtered.publish(filtered_pc2)

        # ✅ 터미널 상단 한줄 출력
        os.system('clear')
        print(f"[LIDAR ROI] 현재 장애물 수: {obstacle_count}")

if __name__ == "__main__":
    try:
        LidarROIFilter()
        rospy.spin()
    except rospy.ROSInterruptException:
        pass




# #!/usr/bin/env python3
# import rospy
# import math
# import sensor_msgs.point_cloud2 as pc2
# from sensor_msgs.msg import PointCloud2
# from std_msgs.msg import Header
# from visualization_msgs.msg import Marker, MarkerArray
# import numpy as np
# from sklearn.cluster import DBSCAN
# from sklearn.linear_model import RANSACRegressor

# class LidarROIFilter:
#     def __init__(self):
#         rospy.init_node('lidar_roi_filter', anonymous=True)

#         self.sub = rospy.Subscriber("/lidar3D", PointCloud2, self.callback)
#         self.pub_filtered = rospy.Publisher("/filtered_lidar3D", PointCloud2, queue_size=1)
#         self.pub_markers = rospy.Publisher("/red_markers", MarkerArray, queue_size=1)
        
#         self.roi_angle_deg = 20
#         self.vert_min_deg = -7
#         self.vert_max_deg = +3

#         self.dbscan_eps = 0.3
#         self.dbscan_min_samples = 10

#     def callback(self, msg):
#         # Convert PointCloud2 to list of (x, y, z)
#         points = []
#         for p in pc2.read_points(msg, field_names=("x", "y", "z"), skip_nans=True):
#             x, y, z = p
#             horiz_angle = math.degrees(math.atan2(y, x))
#             vert_angle = math.degrees(math.atan2(z, math.hypot(x, y)))
            
#             if abs(horiz_angle) <= self.roi_angle_deg and self.vert_min_deg <= vert_angle <= self.vert_max_deg:
#                 points.append([x, y, z])
        
#         if not points:
#             rospy.loginfo("No points in ROI")
#             return

#         points_np = np.array(points)

#         # Remove ground using RANSAC
#         try:
#             ransac = RANSACRegressor(residual_threshold=0.2)
#             ransac.fit(points_np[:, [0, 1]], points_np[:, 2])
#             inlier_mask = ransac.inlier_mask_
#             ground_removed = points_np[~inlier_mask]
#         except Exception as e:
#             rospy.logwarn(f"RANSAC failed: {e}")
#             ground_removed = points_np

#         # DBSCAN Clustering
#         clustering = DBSCAN(eps=self.dbscan_eps, min_samples=self.dbscan_min_samples)
#         labels = clustering.fit_predict(ground_removed)

#         unique_labels = set(labels)
#         markers = MarkerArray()
#         header = msg.header

#         original_indices = np.arange(len(points_np))
#         non_ground_indices = original_indices[~inlier_mask]

#         for idx, label in enumerate(unique_labels):
#             if label == -1:
#                 continue  # noise

#             cluster_mask = (labels == label)
#             cluster_points = ground_removed[cluster_mask]

#             # 각 클러스터의 원래 인덱스를 계산
#             cluster_indices_in_original = non_ground_indices[cluster_mask]
#             cluster_inlier_flags = inlier_mask[cluster_indices_in_original]

#             # 만약 클러스터의 대부분이 지면이라면 무시
#             # 작을수록 0.5 -> 0.1 지면 잘 지워진다는데 별 차이 없는듯?
#             # if np.mean(cluster_inlier_flags) > 0.1:
#             #     continue

#             # Centroid 및 거리 계산
#             centroid = np.mean(cluster_points, axis=0)
#             distance = np.linalg.norm(centroid[:2])
#             if distance > 30.0:
#                 continue

#             # Marker 생성
#             marker = Marker()
#             marker.header = header
#             marker.ns = "clusters"
#             marker.id = idx
#             marker.type = Marker.SPHERE
#             marker.action = Marker.ADD
#             marker.pose.position.x = centroid[0]
#             marker.pose.position.y = centroid[1]
#             marker.pose.position.z = centroid[2]
#             marker.pose.orientation.w = 1.0
#             marker.scale.x = marker.scale.y = marker.scale.z = 0.3
#             marker.color.r = 1.0
#             marker.color.g = 0.0
#             marker.color.b = 0.0
#             marker.color.a = 0.8
#             markers.markers.append(marker)


#         self.pub_markers.publish(markers)

#         # Convert filtered points to PointCloud2
#         filtered_pc2 = pc2.create_cloud_xyz32(header, ground_removed.tolist())
#         self.pub_filtered.publish(filtered_pc2)

# if __name__ == "__main__":
#     try:
#         LidarROIFilter()
#         rospy.spin()
#     except rospy.ROSInterruptException:
#         pass


