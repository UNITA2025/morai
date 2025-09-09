#!/usr/bin/env python3

import rospy
from std_msgs.msg import Bool
from visualization_msgs.msg import MarkerArray

class ObjectStopper:
    def __init__(self):
        rospy.init_node('object_detector', anonymous=True)
        self.pub = rospy.Publisher('/stop_flag', Bool, queue_size=1)
        rospy.Subscriber('/red_markers', MarkerArray, self.marker_callback)
        rospy.Subscriber('/override_stop_flag', Bool, self.override_callback)

        self.override_active = False
        rospy.loginfo("✅ ObjectStopper 노드 초기화 완료, /red_markers 및 /override_stop_flag 구독 시작")
        rospy.spin()

    def override_callback(self, msg):
        self.override_active = msg.data
        if self.override_active:
            rospy.logwarn("🚧 장애물 무시 모드 활성화됨 (/override_stop_flag=True)")
        else:
            rospy.loginfo("✅ 장애물 무시 모드 비활성화됨 (/override_stop_flag=False)")

    def marker_callback(self, msg):
        if self.override_active:
            self.pub.publish(Bool(data=False))
            rospy.loginfo("🟦 장애물 무시 중 → 정지명령 보내지 않음")
            return

        obstacle_count = len(msg.markers)
        if obstacle_count > 1:
            rospy.loginfo(f"🟥 물체 {obstacle_count}개 감지됨 → 정지")
            self.pub.publish(Bool(data=True))
        else:
            rospy.loginfo("🟩 장애물 없음 → 정상 주행")
            self.pub.publish(Bool(data=False))

if __name__ == '__main__':
    try:
        ObjectStopper()
    except rospy.ROSInterruptException:
        pass







# #!/usr/bin/env python3

# import rospy
# from std_msgs.msg import Bool
# from visualization_msgs.msg import MarkerArray

# class ObjectStopper:
#     def __init__(self):
#         rospy.init_node('object_detector', anonymous=True)
#         self.pub = rospy.Publisher('/stop_flag', Bool, queue_size=1)
#         rospy.Subscriber('/red_markers', MarkerArray, self.marker_callback)
#         rospy.loginfo("✅ ObjectStopper 노드 초기화 완료, /red_markers 구독 시작")
#         rospy.spin()

#     def marker_callback(self, msg):
#         obstacle_count = len(msg.markers)
#         if obstacle_count > 1:
#             rospy.loginfo(f"🟥 물체 {obstacle_count}개 감지됨 → 정지")
#             self.pub.publish(Bool(data=True))
#         else:
#             rospy.loginfo("🟩 장애물 없음 → 정상 주행")
#             self.pub.publish(Bool(data=False))

# if __name__ == '__main__':
#     try:
#         ObjectStopper()
#     except rospy.ROSInterruptException:
#         pass
