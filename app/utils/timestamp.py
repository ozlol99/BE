import time
from datetime import datetime, timedelta


def format_time_ago_v1(timestamp_ms: int) -> str:
    # 1. 밀리초 타임스탬프를 datetime 객체로 변환
    timestamp_s = timestamp_ms / 1000
    target_time = datetime.fromtimestamp(timestamp_s)
    current_time = datetime.now()

    # 2. 현재 시간과의 차이 계산
    time_diff = current_time - target_time

    # 3. 조건에 따라 문자열 반환
    if time_diff < timedelta(minutes=1):
        return "방금 전"
    elif time_diff < timedelta(hours=1):
        minutes = int(time_diff.total_seconds() / 60)
        return f"{minutes}분 전"
    elif time_diff < timedelta(days=1):
        hours = int(time_diff.total_seconds() / 3600)
        return f"{hours}시간 전"
    elif time_diff < timedelta(weeks=1):
        days = time_diff.days
        return f"{days}일 전"
    elif time_diff < timedelta(weeks=4):  # 4주를 한 달의 근사치로 사용
        weeks = int(time_diff.days / 7)
        return f"{weeks}주 전"
    elif time_diff < timedelta(days=365):
        return "한 달 전"
    else:
        years = int(time_diff.days / 365)
        return f"{years}년 전"


# Helper function for time
def format_time_ago_v2(dt):
    if dt is None:
        return "N/A"
    now = time.time()
    created_at_ts = dt.timestamp()
    diff = int(now - created_at_ts)

    if diff < 60:
        return f"{diff}초 전"
    elif diff < 3600:
        return f"{diff // 60}분 전"
    elif diff < 86400:
        return f"{diff // 3600}시간 전"
    else:
        return f"{diff // 86400}일 전"
