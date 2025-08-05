# 최신의 ubuntu 이미지를 기반으로 설정
FROM python:3.13-slim
# 사용자
LABEL authors="sungwoon"

# 작업 디렉토리 설정
WORKDIR /app

# uv 설치 (Rust 기반이지만 바이너리 제공됨)
RUN pip install uv

#aerich migrate




# 의존성 정보 복사
COPY pyproject.toml .
COPY uv.lock .

# 의존성 설치
RUN uv pip install -r pyproject.toml --system

# 소스 코드 복사
COPY . .

CMD ["bash", "./run.sh"]
