#!/usr/bin/env python3
import rospy
import sensor_msgs.point_cloud2 as pc2
from sensor_msgs.msg import PointCloud2
from visualization_msgs.msg import Marker, MarkerArray
from geometry_msgs.msg import Point
import numpy as np
import open3d as o3d
from sklearn.cluster import DBSCAN

class ObstacleClusteringMarker:
    def __init__(self):
        rospy.init_node('roi_obstacle_marker')
        self.sub = rospy.Subscriber('/lidar3D', PointCloud2, self.pointcloud_callback, queue_size=1)
        self.marker_pub = rospy.Publisher('/cluster_markers', MarkerArray, queue_size=1)

    def pointcloud_callback(self, msg):
        points = list(pc2.read_points(msg, field_names=("x", "y", "z"), skip_nans=True))
        if not points:
            return

        np_points = np.array(points)
        pcd = o3d.geometry.PointCloud()
        pcd.points = o3d.utility.Vector3dVector(np_points)

        # 1. RANSAC으로 지면 제거
        plane_model, inliers = pcd.segment_plane(distance_threshold=0.05,
                                                 ransac_n=3,
                                                 num_iterations=100)
        non_ground = pcd.select_by_index(inliers, invert=True)
        np_filtered = np.asarray(non_ground.points)

        # 2. ROI 필터링 (전방 10m, 좌우 3m, 지면 위 0.2m 이상만)
        roi_mask = (
            (np_filtered[:, 0] >= -5.0) & (np_filtered[:, 0] <= 10.0) &
            (np_filtered[:, 1] >= -3.0) & (np_filtered[:, 1] <= 3.0) &
            (np_filtered[:, 2] >= 0.2) & (np_filtered[:, 2] <= 2.5)
        )
        roi_points = np_filtered[roi_mask]

        if roi_points.shape[0] < 5:
            return

        # 3. DBSCAN 클러스터링
        db = DBSCAN(eps=0.5, min_samples=10).fit(roi_points)
        labels = db.labels_
        unique_labels = set(labels)

        marker_array = MarkerArray()
        marker_id = 0
        for label in unique_labels:
            if label == -1:
                continue  # 노이즈 제외

            cluster = roi_points[labels == label]
            center = np.mean(cluster, axis=0)

            # 마커 생성
            marker = Marker()
            marker.header.frame_id = "Lidar3D-1"
            marker.header.stamp = rospy.Time.now()
            marker.ns = "obstacle"
            marker.id = marker_id
            marker_id += 1
            marker.type = Marker.SPHERE
            marker.action = Marker.ADD
            marker.pose.position = Point(*center)
            marker.pose.orientation.w = 1.0
            marker.scale.x = marker.scale.y = marker.scale.z = 0.4
            marker.color.r = 1.0
            marker.color.a = 1.0
            marker_array.markers.append(marker)

        self.marker_pub.publish(marker_array)

if __name__ == "__main__":
    ObstacleClusteringMarker()
    rospy.spin()

