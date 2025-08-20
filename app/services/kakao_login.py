import requests
from fastapi import HTTPException

from app.config.settings import Settings

settings = Settings()
BASE_URL = settings.base_url

KAKAO_REST_API_KEY = settings.kakao_rest_api_key
KAKAO_TOKEN_URL = "https://kauth.kakao.com/oauth/token"

# 2. 토큰 요청 함수 (인가 코드를 인자로 받음)
def request_kakao_token(code: str, detail_uri):
    redirect_uri = f"{BASE_URL}{detail_uri}"
    data = {
        "grant_type": "authorization_code",
        "client_id": KAKAO_REST_API_KEY,
        "redirect_uri": redirect_uri,
        "code": code,
    }
    try:
        response = requests.post(KAKAO_TOKEN_URL, data=data)
        response.raise_for_status()  # HTTP 오류 발생 시 예외 발생
        token_info = response.json()  # 응답 본문을 JSON에서 Python 딕셔너리로 변환
        return token_info

    except requests.exceptions.RequestException as e:
        print(f"토큰 요청 중 오류 발생: {e}")
        raise HTTPException(status_code=500, detail="토큰 발급 실패")


def get_kakao_profile(access_token):
    url = "https://kapi.kakao.com/v2/user/me"
    headers = {"Authorization": f"Bearer {access_token}"}
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # HTTP 오류 발생 시 예외 발생
        user_info = response.json()
        print(f"email: {user_info}")
        return user_info["kakao_account"]["email"]

    except requests.exceptions.RequestException as e:
        print(f"API 호출 중 오류 발생: {e}")
        return None
