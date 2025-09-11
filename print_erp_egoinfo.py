import time
import sys
from EgoInfoReceiver import EgoInfoReceiver


class EgoInfoMonitor:
    def __init__(self):
        self.ego_receiver = None
        self.connected = False
        self.receiving = False
        self.last_data = None
        self.data_count = 0

    def data_callback(self, parsed_data):
        """EgoInfo 데이터 수신 콜백 함수"""
        if parsed_data:  # 데이터가 있을 때만 처리
            self.receiving = True
            self.last_data = parsed_data
            self.data_count += 1
        else:
            self.receiving = False

    def connect(self, host, port):
        """EgoInfo 수신기 연결"""
        try:
            self.ego_receiver = EgoInfoReceiver(host, port, self.data_callback)
            self.connected = True
            return True
        except Exception as e:
            self.connected = False
            raise e

    def disconnect(self):
        """연결 해제"""
        if self.ego_receiver:
            del self.ego_receiver
            self.ego_receiver = None
        self.connected = False
        self.receiving = False

    def get_ego_data(self):
        """현재 EgoInfo 데이터 반환"""
        return self.last_data if self.last_data else [None] * 25


def print_separator():
    print("=" * 120)


def format_value(value, precision=3):
    """값이 None인 경우 처리"""
    if value is None:
        return "N/A"
    if isinstance(value, (int, float)):
        return f"{value:.{precision}f}"
    return str(value)


def format_gear(gear_value):
    """기어 상태를 문자열로 변환"""
    if gear_value is None:
        return "N/A"

    gear_map = {
        0: "P(주차)",
        1: "R(후진)",
        2: "N(중립)",
        3: "D(전진)",
        4: "Manual"
    }
    return gear_map.get(gear_value, f"Unknown({gear_value})")


def format_ctrl_mode(ctrl_mode):
    """제어 모드를 문자열로 변환"""
    if ctrl_mode is None:
        return "N/A"

    mode_map = {
        0: "Manual",
        1: "Auto",
        2: "Emergency"
    }
    return mode_map.get(ctrl_mode, f"Unknown({ctrl_mode})")


def main():
    # EgoInfo Monitor 초기화
    ego_monitor = EgoInfoMonitor()

    # 연결 설정
    ego_host = '127.0.0.1'
    ego_port = 9097  # EgoInfo 포트 (필요에 따라 변경)

    print("🚗 EgoInfo 데이터 모니터링 시스템")
    print_separator()
    print(f"EgoInfo 연결 시도 중... ({ego_host}:{ego_port})")

    # EgoInfo 연결
    try:
        ego_monitor.connect(ego_host, ego_port)
        print("✓ EgoInfo 연결 성공!")
    except Exception as e:
        print(f"✗ EgoInfo 연결 실패: {e}")
        sys.exit(1)

    print("\n데이터 수신 대기 중...")
    print("종료하려면 Ctrl+C를 누르세요.")
    print_separator()

    try:
        while True:
            # 현재 시간
            current_time = time.strftime('%H:%M:%S')

            # EgoInfo 데이터 가져오기
            ego_data = ego_monitor.get_ego_data()

            # 연결 상태
            ego_status = "🟢 연결됨" if ego_monitor.connected else "🔴 연결 끊어짐"
            ego_recv_status = "📡 수신 중" if ego_monitor.receiving else "❌ 수신 없음"

            # 데이터 파싱 (EgoInfoReceiver의 _parsed_data 순서에 따라)
            if len(ego_data) >= 25:
                ctrl_mode, gear, signed_vel, map_id, accel, brake = ego_data[0:6]
                size_x, size_y, size_z, overhang, wheelbase, rear_overhang = ego_data[6:12]
                pos_x, pos_y, pos_z = ego_data[12:15]
                roll, pitch, yaw = ego_data[15:18]
                vel_x, vel_y, vel_z = ego_data[18:21]
                acc_x, acc_y, acc_z = ego_data[21:24]
                steer = ego_data[24]
            else:
                # 데이터가 없을 때 기본값
                ctrl_mode = gear = signed_vel = map_id = accel = brake = None
                size_x = size_y = size_z = overhang = wheelbase = rear_overhang = None
                pos_x = pos_y = pos_z = roll = pitch = yaw = None
                vel_x = vel_y = vel_z = acc_x = acc_y = acc_z = steer = None

            print(f"\n[{current_time}] EgoInfo 데이터 현황 (수신 횟수: {ego_monitor.data_count})")
            print("-" * 120)

            # 연결 상태
            print(f"🚗 EgoInfo 상태: {ego_status} | {ego_recv_status}")
            print()

            # 기본 차량 정보
            print("📊 차량 기본 정보:")
            print(f"   제어 모드: {format_ctrl_mode(ctrl_mode)} | 기어: {format_gear(gear)} | 맵 ID: {format_value(map_id, 0)}")
            print(f"   속도: {format_value(signed_vel, 2)} km/h | 가속페달: {format_value(accel, 3)} | 브레이크: {format_value(brake, 3)}")
            print(f"   조향각: {format_value(steer, 3)}°")
            print()

            # 위치 및 자세 정보
            print("📍 위치 및 자세:")
            print(f"   위치(m): X={format_value(pos_x, 2)} Y={format_value(pos_y, 2)} Z={format_value(pos_z, 2)}")
            print(f"   자세(rad): Roll={format_value(roll, 4)} Pitch={format_value(pitch, 4)} Yaw={format_value(yaw, 4)}")
            print()

            # 속도 정보
            print("🏃 속도 정보:")
            print(f"   선속도(m/s): X={format_value(vel_x, 3)} Y={format_value(vel_y, 3)} Z={format_value(vel_z, 3)}")
            print()

            # 가속도 정보
            print("⚡ 가속도 정보:")
            print(f"   가속도(m/s²): X={format_value(acc_x, 3)} Y={format_value(acc_y, 3)} Z={format_value(acc_z, 3)}")
            print()

            # 차량 치수 정보
            print("📐 차량 치수:")
            print(f"   크기(m): 길이={format_value(size_x, 2)} 폭={format_value(size_y, 2)} 높이={format_value(size_z, 2)}")
            print(f"   오버행: 전={format_value(overhang, 2)} 휠베이스={format_value(wheelbase, 2)} 후={format_value(rear_overhang, 2)}")

            print("-" * 120)

            # 1초 대기
            time.sleep(1)

    except KeyboardInterrupt:
        print("\n\n프로그램 종료 중...")

    finally:
        # 연결 해제
        print("EgoInfo 연결 해제 중...")
        try:
            ego_monitor.disconnect()
            print("✓ EgoInfo 연결 해제 완료")
        except Exception as e:
            print(f"✗ EgoInfo 연결 해제 실패: {e}")

        print("모든 연결이 정리되었습니다.")


if __name__ == "__main__":
    main()
