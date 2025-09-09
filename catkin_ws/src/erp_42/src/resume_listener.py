#!/usr/bin/env python3

import rospy
from std_msgs.msg import String, Bool

class ResumeListener:
    def __init__(self):
        rospy.init_node('resume_listener', anonymous=True)
        self.stop_pub = rospy.Publisher('/stop_flag', Bool, queue_size=1)
        self.override_pub = rospy.Publisher('/override_stop_flag', Bool, queue_size=1)
        rospy.Subscriber('/resume_cmd', String, self.resume_callback)
        rospy.spin()

    def resume_callback(self, msg):
        if msg.data.lower() == "go":
            rospy.loginfo("🚗 재출발 명령 수신 → 장애물 무시 및 주행 재개")
            self.override_pub.publish(Bool(data=True))  # 회피 무시 모드 활성화
            self.stop_pub.publish(Bool(data=False))     # PurePursuit 주행 재개
        elif msg.data.lower() == "cancel":
            rospy.loginfo("🛑 회피 무시 모드 취소")
            self.override_pub.publish(Bool(data=False))  # 회피 무시 모드 비활성화

if __name__ == '__main__':
    try:
        ResumeListener()
    except rospy.ROSInterruptException:
        pass





# #!/usr/bin/env python3
# import rospy
# from std_msgs.msg import String, Bool

# class ResumeListener:
#     def __init__(self):
#         rospy.init_node('resume_listener', anonymous=True)
#         self.pub = rospy.Publisher('/stop_flag', Bool, queue_size=1)
#         rospy.Subscriber('/resume_cmd', String, self.resume_callback)
#         rospy.spin()

#     def resume_callback(self, msg):
#         if msg.data.lower() == "go":
#             rospy.loginfo("재출발 명령 수신 → 주행 재개")
#             self.pub.publish(Bool(data=False))

# if __name__ == '__main__':
#     try:
#         ResumeListener()
#     except rospy.ROSInterruptException:
#         pass
