# 최신 ubuntu 이미지를 기반으로 설정
FROM python:3.13-slim
# 사용자
LABEL authors="sungwoon"

# 작업 디렉토리 설정
WORKDIR /app

# uv 설치 (Rust 기반이지만 바이너리 제공됨)
RUN pip install uv

# 전체 소스 코드와 의존성 파일 모두 복사
COPY . .

# 의존성 설치
# 이제 소스 코드가 컨테이너에 있으므로 'uv'가 패키지를 올바르게 빌드할 수 있습니다.
RUN uv pip install ."[dev]" --system

# 애플리케이션 실행
CMD ["bash", "./run.sh"]