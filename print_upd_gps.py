import socket
from threading import Thread, Event
import time
import sys

import pynmea2

class GPSConnector:
    def __init__(self, network_type):
        self.gpsClient = None
        self.networkType = network_type
        self.connChk = False
        self.recvChk = False
        self.event = Event()

        self.pos_x = 126.773287
        self.pos_y = 37.229319

    def __del__(self):
        print('gps_del')

    def connect(self, host, port, topic):
        if self.networkType == 'UDP':
            try:
                self.gpsClient = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                self.gpsClient.setblocking(False)
                self.gpsClient.settimeout(1)
                self.gpsClient.bind((host, port))

                self.gpsRecvThread = Thread(target=self.position, args=())
                self.gpsRecvThread.setDaemon(True)
                self.gpsRecvThread.start()

            except Exception as e:
                print(f'gps_connect: {e}')
                return False

        else:
            from morai_msgs.msg import GPSMessage
            import rospy
            self.gpsClient = rospy.Subscriber(topic, GPSMessage, self.gpsCB)
            try:
                rospy.wait_for_message(topic, GPSMessage, timeout=1)
            except rospy.exceptions.ROSException:
                pass

        self.connChk = True
        return True

    def gpsCB(self, data):
        self.pos_x = data.longitude
        self.pos_y = data.latitude
        self.recvChk = True

    def disconnect(self):
        if self.networkType == 'UDP':
            if self.connChk:
                self.connChk = False
                if hasattr(self, 'gpsRecvThread') and self.gpsRecvThread.is_alive():
                    self.event.set()
                    self.gpsRecvThread.join()
                if self.gpsClient:
                    self.gpsClient.close()

        else:
            if self.gpsClient:
                self.gpsClient.unregister()

    def position(self):
        while True:
            try:
                if self.event.is_set():
                    break
                datas, host = self.gpsClient.recvfrom(8196)
                asciiDatas = datas.decode('ascii')
                gpdatas = asciiDatas.split('\r\n')

                gpgga = pynmea2.parse(gpdatas[0])

                lats = gpgga.latitude
                longs = gpgga.longitude
                self.pos_y = lats
                self.pos_x = longs  # longitude is negative

                self.recvChk = True

            except socket.timeout:
                if self.recvChk:
                    continue
                else:
                    self.recvChk = False
                    break
            except Exception as e:
                print(f'gps_position: {e}')
                break

    def getPose(self):
        return (self.pos_x, self.pos_y)

    def isConnected(self):
        return self.connChk

    def isReceiving(self):
        return self.recvChk


def main():
    # GPS Connector 초기화
    gps = GPSConnector('UDP')

    # 연결 설정
    host = '127.0.0.1'
    port = 9099

    print(f"GPS 연결 시도 중... ({host}:{port})")

    if not gps.connect(host, port, None):
        print("GPS 연결 실패!")
        return

    print("GPS 연결 성공!")
    print("GPS 데이터를 기다리는 중...")
    print("종료하려면 Ctrl+C를 누르세요.\n")

    try:
        while True:
            # 현재 위치 가져오기
            pos_x, pos_y = gps.getPose()

            # 연결 상태 확인
            conn_status = "연결됨" if gps.isConnected() else "연결 끊어짐"
            recv_status = "수신 중" if gps.isReceiving() else "수신 없음"

            # 위치 정보 출력
            print(f"[{time.strftime('%H:%M:%S')}] "
                  f"위도: {pos_y:.6f}, 경도: {pos_x:.6f} | "
                  f"상태: {conn_status}, {recv_status}")

            # 1초 대기
            time.sleep(1)

    except KeyboardInterrupt:
        print("\n\n프로그램 종료 중...")

    finally:
        # 연결 해제
        gps.disconnect()
        print("GPS 연결 해제 완료")


if __name__ == "__main__":
    main()
