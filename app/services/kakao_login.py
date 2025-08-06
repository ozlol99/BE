import os

import dotenv
import requests
from fastapi import HTTPException

dotenv.load_dotenv()

# 2. 토큰 요청 함수 (인가 코드를 인자로 받음)
def request_kakao_token(code: str):
    KAKAO_TOKEN_URL = "https://kauth.kakao.com/oauth/token"
    KAKAO_REST_API_KEY = os.getenv("a04159cc219d093bdcde9d55ea4b88fc")
    REDIRECT_URI = "http://127.0.0.1:8000/kakao-login"

    data = {
        "grant_type": "authorization_code",
        "client_id": KAKAO_REST_API_KEY,
        "redirect_uri": REDIRECT_URI,
        "code": code,
    }

    try:
        response = requests.post(KAKAO_TOKEN_URL, data=data)
        response.raise_for_status()  # HTTP 오류 발생 시 예외 발생

        # 응답 본문을 JSON에서 Python 딕셔너리로 변환
        token_info = response.json()

        # 각 변수에 잘 담겼는지 확인합니다. (디버깅용)
        print("Access Token:", token_info["access_token"])
        print("Token Type:", token_info["token_type"])
        print("Refresh Token:", token_info["refresh_token"])
        print("ID Token:", token_info["id_token"])
        print("Expires In:", token_info["expires_in"])
        print("Refresh Token Expires In:", token_info["refresh_token_expires_in"])

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
        print(f"email{user_info['email']}")
        return user_info

    except requests.exceptions.RequestException as e:
        print(f"API 호출 중 오류 발생: {e}")
        return None
