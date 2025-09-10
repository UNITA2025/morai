import time
import sys
from GPSprocess import GPSConnector
from IMUprocess import IMUConnector, IMUINFO


def print_separator():
    print("=" * 100)


def format_value(value, precision=6):
    """값이 None인 경우 처리"""
    if value is None:
        return "N/A"
    return f"{value:.{precision}f}"


def main():
    # GPS와 IMU Connector 초기화
    gps = GPSConnector('UDP')
    imu = IMUConnector('UDP')

    # 연결 설정
    gps_host = '127.0.0.1'
    gps_port = 9098
    imu_host = '127.0.0.1'
    imu_port = 9096

    print("GPS & IMU 데이터 모니터링 시스템")
    print_separator()
    print(f"GPS 연결 시도 중... ({gps_host}:{gps_port})")
    print(f"IMU 연결 시도 중... ({imu_host}:{imu_port})")

    # GPS 연결
    try:
        gps.connect(gps_host, gps_port, None)
        print("✓ GPS 연결 성공!")
    except Exception as e:
        print(f"✗ GPS 연결 실패: {e}")

    # IMU 연결
    try:
        imu.connect(imu_host, imu_port, None)
        print("✓ IMU 연결 성공!")
    except Exception as e:
        print(f"✗ IMU 연결 실패: {e}")

    print("\n데이터 수신 대기 중...")
    print("종료하려면 Ctrl+C를 누르세요.")
    print_separator()

    try:
        while True:
            # 현재 시간
            current_time = time.strftime('%H:%M:%S')

            # GPS 데이터 가져오기
            pos_x, pos_y = gps.getPose()
            gps_connected = gps.connChk
            gps_receiving = gps.recvChk

            # IMU 데이터 가져오기
            imu_data = imu.getIMU()
            imu_connected = imu.connChk
            imu_receiving = imu.recvChk

            # 연결 상태 표시
            gps_status = "🟢 연결됨" if gps_connected else "🔴 연결 끊어짐"
            gps_recv_status = "📡 수신 중" if gps_receiving else "❌ 수신 없음"
            imu_status = "🟢 연결됨" if imu_connected else "🔴 연결 끊어짐"
            imu_recv_status = "📡 수신 중" if imu_receiving else "❌ 수신 없음"

            # 화면 클리어 (선택사항)
            # print("\033[H\033[J", end="")

            print(f"\n[{current_time}] 센서 데이터 현황")
            print("-" * 100)

            # GPS 정보 출력
            print(f"📍 GPS 상태: {gps_status} | {gps_recv_status}")
            print(f"   위치: 위도 {format_value(pos_y)}°, 경도 {format_value(pos_x)}°")

            print()

            # IMU 정보 출력
            print(f"🧭 IMU 상태: {imu_status} | {imu_recv_status}")
            print(f"   자세(Orientation): X={format_value(imu_data.orientation_x, 4)} "
                  f"Y={format_value(imu_data.orientation_y, 4)} "
                  f"Z={format_value(imu_data.orientation_z, 4)} "
                  f"W={format_value(imu_data.orientation_w, 4)}")

            print(f"   각속도(Angular Velocity): X={format_value(imu_data.angular_velocity_x, 3)} "
                  f"Y={format_value(imu_data.angular_velocity_y, 3)} "
                  f"Z={format_value(imu_data.angular_velocity_z, 3)} rad/s")

            print(f"   선형가속도(Linear Acceleration): X={format_value(imu_data.linear_acceleration_x, 3)} "
                  f"Y={format_value(imu_data.linear_acceleration_y, 3)} "
                  f"Z={format_value(imu_data.linear_acceleration_z, 3)} m/s²")

            print("-" * 100)

            # 1초 대기
            time.sleep(1)

    except KeyboardInterrupt:
        print("\n\n프로그램 종료 중...")

    finally:
        # 연결 해제
        print("센서 연결 해제 중...")
        try:
            gps.disconnect()
            print("✓ GPS 연결 해제 완료")
        except Exception as e:
            print(f"✗ GPS 연결 해제 실패: {e}")

        try:
            imu.disconnect()
            print("✓ IMU 연결 해제 완료")
        except Exception as e:
            print(f"✗ IMU 연결 해제 실패: {e}")

        print("모든 연결이 정리되었습니다.")


if __name__ == "__main__":
    main()
