from datetime import datetime, timedelta

def format_time_ago(timestamp_ms: int) -> str:
    """
    주어진 유닉스 타임스탬프(밀리초)를 현재 시간과 비교하여 "방금 전", "N분 전" 등으로 표현합니다.

    Args:
        timestamp_ms (int): 비교할 시간의 유닉스 타임스탬프 (밀리초).

    Returns:
        str: 현재 시간과 비교하여 포맷된 문자열.
    """
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
