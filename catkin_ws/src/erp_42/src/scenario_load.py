#!/usr/bin/env python3
import rospy
from morai_msgs.srv import MoraiScenarioLoadSrv, MoraiScenarioLoadSrvRequest

class ScenarioLoader:
    def __init__(self):
        rospy.init_node('scenario_loader', anonymous=False)

        rospy.wait_for_service('/MoraiSimulator/ScenarioLoad')
        self.load_srv = rospy.ServiceProxy('/MoraiSimulator/ScenarioLoad', MoraiScenarioLoadSrv)

        self.req = MoraiScenarioLoadSrvRequest()
        self.req.file_path = "/home/unita/MoraiLauncher_Lin/MoraiLauncher_Lin_Data/SaveFile/Scenario/R_KR_PG_K-City/only_Obstacle.json"
        self.req.load_network_data = False

        rospy.Timer(rospy.Duration(10), self.call_service)

    def call_service(self, event):
        try:
            res = self.load_srv(self.req)
            if res.result:
                rospy.loginfo("[ScenarioLoader] Scenario loaded successfully")
            else:
                rospy.logwarn("[ScenarioLoader] Scenario load failed")
        except rospy.ServiceException as e:
            rospy.logerr(f"[ScenarioLoader] Service call failed: {e}")

if __name__ == "__main__":
    ScenarioLoader()
    rospy.spin()


# #!/usr/bin/env python3
# import rospy
# from std_msgs.msg import String

# class ScenarioPublisher:
#     def __init__(self, json_path, topic_name='/scenario_load'):
#         # 노드 초기화
#         rospy.init_node('scenario_publisher', anonymous=False)
       
#         # 퍼블리셔 생성
#         self.pub = rospy.Publisher(topic_name, String, queue_size=1)
       
#         # JSON 파일 경로
#         self.json_path = json_path
       
#         # 10초마다 publish_callback 호출
#         rospy.Timer(rospy.Duration(10.0), self.publish_callback)
       
#         rospy.loginfo(f"[ScenarioPublisher] Publishing '{json_path}' to '{topic_name}' every 10s")

#     def publish_callback(self, event):
#         try:
#             # 파일 읽기 (한 줄 문자열)
#             with open(self.json_path, 'r') as f:
#                 json_str = f.read().replace('\n', ' ')
           
#             # 퍼블리시
#             msg = String(data=json_str)
#             self.pub.publish(msg)
#             rospy.loginfo("[ScenarioPublisher] Published scenario JSON")
#         except Exception as e:
#             rospy.logerr(f"[ScenarioPublisher] Failed to read/publish JSON: {e}")

# if __name__ == '__main__':
#     # JSON 파일 경로를 여기에서 지정하세요
#     json_file = '/home/unita/MoraiLauncher_Lin/MoraiLauncher_Lin_Data/SaveFile/Scenario/R_KR_PG_K-City/only_Obstacle.json'
#     topic     = '/scenario_load'
   
#     sp = ScenarioPublisher(json_file, topic)
#     rospy.spin()