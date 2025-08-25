# lol99 - 당신의 LoL 파트너 매칭 플랫폼

"lol99"는 리그 오브 레전드(League of Legends) 플레이어들이 자신의 성향에 맞는 최고의 팀원을 찾고, 함께 소통하며 게임을 즐길 수 있도록 설계된 매칭 플랫폼입니다. Riot API와 연동하여 신뢰도 높은 유저 정보를 제공하며, 실시간 채팅을 통해 팀원 간의 원활한 소통을 지원합니다.

---
## 🎞️ 배포 주소

> ### [**⛪ lol99 서비스 바로가기**](https://lol99.kro.kr)
> ### [**📖 API Docs 바로가기**](https://api.lol99.kro.kr/docs)

---
## 🎞️ 프로젝트 발표 영상 & 발표 문서

> ### 🗓️ 프로젝트 기간: 2025.07.30 ~ 2025.08.27
> ### [ 발표 영상 ]( (링크를 입력해주세요) )
> ### [ 발표 문서 ]( (링크를 입력해주세요) )

---

## ✨ 주요 기능

- **강력한 사용자 인증**: Google 및 Kakao 소셜 로그인을 통해 사용자가 손쉽게 접근할 수 있습니다.
- **Riot 계정 연동**: 라이엇 계정 연동을 통해 채팅 서비스를 이용할시 사용자들이 각각 참여자의 정보를 한눈에 알아보기 쉽습니다
- **소환사 검색, 자동완성**: 데이터베이스에 검색된 유저를 기반으로 해시태그를 포함한 유저정보를 자동완성 시킴으로서 전적 검색시에 유저의 편의성을 향상 시켰습니다
- **실시간 소통**: WebSocket 기반의 실시간 채팅 기능을 통해 다양한 유저들과 매칭을 시도할 수 있습니다
- **전적검색**:riot api를 기반으로 리그오브레전드 유저들의 매치 기록 및 프로필을 검색 할 수 있습니다

---

## 📸 서비스 주요 화면

> `lol99` 프로젝트의 주요 기능 스크린샷을 추가해주세요.

|   메인 화면   |   소환사 검색   |   채팅 화면   |
|:--------:|:------:|:--------:|
| (이미지) |   (이미지)  | (이미지) |

---

## 🛠️ 기술 스택 및 아키텍처

### System Architecture

이 프로젝트는 Nginx를 리버스 프록시로 활용하여 안정적이고 효율적인 서비스 환경을 구축했습니다. Nginx는 SSL/TLS 처리를 담당하여 보안을 강화하고, 정적 파일 서빙 및 로드 밸런싱(추후 확장 시)의 이점을 가집니다. 사용자의 요청은 Nginx를 거쳐 Uvicorn ASGI 서버에서 실행되는 FastAPI 애플리케이션으로 전달됩니다. Certbot을 사용하여 ec2 인스턴스 주소에 SSL/TLS를 자체 인증받았습니다.


<br>

| Category | Technologies |
|:---:|:---:|
| **Backend** | ![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white) ![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white) ![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white) ![Uvicorn](https://img.shields.io/badge/Uvicorn-FF6200?style=for-the-badge&logo=uvicorn&logoColor=white) ![Pydantic](https://img.shields.io/badge/Pydantic-E92063?style=for-the-badge&logo=pydantic&logoColor=white) |
| **Database** | ![Tortoise ORM](https://img.shields.io/badge/Tortoise%20ORM-0062FF?style=for-the-badge&logoColor=white) ![aerich](https://img.shields.io/badge/aerich-39A722?style=for-the-badge&logoColor=white) ![MySQL](https://img.shields.io/badge/MySQL-4479A1?style=for-the-badge&logo=mysql&logoColor=white) |
| **Authentication** | ![JWT](https://img.shields.io/badge/JWT-000000?style=for-the-badge&logo=json-web-tokens&logoColor=white) ![OAuth2](https://img.shields.io/badge/OAuth2-FB5431?style=for-the-badge&logo=oauth&logoColor=white) ![Google](https://img.shields.io/badge/Google-4285F4?style=for-the-badge&logo=google&logoColor=white) ![Kakao](https://img.shields.io/badge/Kakao-FFCD00?style=for-the-badge&logo=kakaotalk&logoColor=black) |
| **Deployment** | ![Nginx](https://img.shields.io/badge/Nginx-009639?style=for-the-badge&logo=nginx&logoColor=white) ![Uvicorn](https://img.shields.io/badge/Uvicorn-FF6200?style=for-the-badge&logo=uvicorn&logoColor=white) ![AWS EC2](https://img.shields.io/badge/AWS%20EC2-FF9900?style=for-the-badge&logo=amazon-aws&logoColor=white) ![Certbot](https://img.shields.io/badge/Certbot-527D4D?style=for-the-badge&logo=lets-encrypt&logoColor=white) |
| **Testing** | ![Pytest](https://img.shields.io/badge/Pytest-0A9EDC?style=for-the-badge&logo=pytest&logoColor=white) |
| **Code Style & Linting** | ![Ruff](https://img.shields.io/badge/Ruff-000000?style=for-the-badge&logo=ruff&logoColor=white) ![Black](https://img.shields.io/badge/Black-000000?style=for-the-badge&logo=black&logoColor=white) |
| **CI/CD** | ![GitHub Actions](https://img.shields.io/badge/GitHub%20Actions-2088FF?style=for-the-badge&logo=github-actions&logoColor=white) |
---

## 📁 프로젝트 구조

```
lol99/
├── app/                # FastAPI 애플리케이션 루트
│   ├── apis/           # API 라우터 (엔드포인트) 정의
│   ├── config/         # 애플리케이션 설정 (환경 변수, DB 등)
│   ├── dtos/           # DTO (Data Transfer Objects) 정의
│   ├── models/         # Tortoise ORM 모델 (데이터베이스 스키마)
│   ├── services/       # 비즈니스 로직
│   └── utils/          # 유틸리티 함수
├── migrations/         # 데이터베이스 마이그레이션 (Aerich)
├── run.sh              # 애플리케이션 실행 스크립트
├── test.sh             # 테스트 실행 스크립트
└── pyproject.toml      # 프로젝트 의존성 및 메타데이터
```

---

## 👨‍👩‍👧‍👦 팀원 소개

> 잘생긴 BE 팀원 입니다 하하하하하하.

| <a href="https://github.com/wjdtjddns98"><img src="data:image/jpeg;base64,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" width=100px/><br/><sub><b>정성운</b></sub></a><br/> | <a href="https://github.com/park3hho"><img src="data:image/jpeg;base64,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" width=100px/><br/><sub><b>박찬호</b></sub></a><br/> |
|:---------------------------------------------------------------------------------------:|:---------------------------------------------------------------------------------------:|
|                                           역할                                            |                                           역할                                            |
|팀장|                                           팀원                                            |
---

## 🚀 로컬에서 시작하기

### 1. 사전 요구 사항

- **Python 3.12+**
- **uv**: 이 프로젝트는 `uv`를 사용하여 Python 패키지와 가상 환경을 관리합니다. (`pip install uv`로 설치할 수 있습니다.)
- **MySQL 데이터베이스**

### 2. 설치 및 실행

1.  **프로젝트 클론**
    ```bash
    git clone https://github.com/your-username/lol99.git
    cd lol99
    ```

2.  **가상 환경 생성 및 의존성 설치 (uv 사용)**
    ```bash
    uv venv
    source .venv/bin/activate  # Windows: .venv\Scripts\activate
    uv sync
    ```

3.  **환경 변수 설정**
    프로젝트 루트에 `.env` 파일을 생성하고, 아래 템플릿에 맞게 로컬 개발 환경을 설정합니다.
    ```env
    # Database
    DB_HOST=localhost
    DB_USER=your_db_user
    DB_PASSWORD=your_db_password
    DB_DATABASE=lol99
    DB_PORT=3306

    # ... (기타 소셜 로그인, JWT, Riot API 키 등)
    ```

4.  **데이터베이스 마이그레이션**
    ```bash
    aerich init-db
    ```

5.  **애플리케이션 실행**
    ```bash
    sh run.sh
    ```
    서버가 `http://localhost:8000`에서 실행됩니다.

---

## ✅ 테스트

프로젝트의 모든 테스트를 실행하려면 다음 명령어를 사용하세요.

```bash
sh test.sh
```

---

## 📖 프로젝트 규칙

### Branch Strategy
- **`main`**: 프로덕션 배포를 위한 브랜치입니다.
- **`dev`**: 개발된 기능들이 통합되는 개발 브랜치입니다. `main`으로 머지되기 전의 최신 상태를 유지합니다.
- **`feat/{기능이름}`**: 새로운 기능 개발을 위한 브랜치입니다. `dev` 브랜치에서 분기합니다.
- **`fix/{수정내용}`**: 버그 수정을 위한 브랜치입니다.

### Git Commit Convention
커밋 메시지는 어떤 작업인지 명확히 알 수 있도록 다음 접두사를 사용합니다.

| 접두사    | 설명                           |
| --------- | ------------------------------ |
| **Feat**      | 새로운 기능 구현               |
| **Fix**       | 버그 수정                      |
| **Docs**      | 문서 추가 및 수정 (README 등)  |
| **Style**     | 코드 포맷팅, 세미콜론 등 (동작 변경 없음) |
| **Refactor**  | 코드 리팩토링                  |
| **Test**      | 테스트 코드 추가/수정          |
| **Deploy**    | 배포 관련 작업                 |
| **Conf**      | 빌드, 환경 설정                |
| **Chore**     | 기타 잡일 (패키지 설치 등)     |

### Pull Request (PR) 규칙
- **PR 제목**: `[Feat] 소셜 로그인 기능 추가` 와 같이 `[접두사] 작업 요약` 형식으로 작성합니다.
- **PR 본문**:
  - **Description**: 변경 사항에 대한 상세한 설명을 작성합니다.
- **PR 전 확인 사항**:
  - `ruff check .` 및 `ruff format .`을 통해 코드 스타일을 점검합니다.
  - `sh test.sh`를 실행하여 모든 테스트가 통과하는지 확인합니다.
- 최소 1명 이상의 팀원에게 코드 리뷰 및 **Approve**를 받아야 머지할 수 있습니다.

---

## 📋 주요 문서

> [**API 명세서**](https://www.notion.so/API-23fcaf5650aa811f842eeb63bd04c509?source=copy_link)
>
> [**ERD**](https://www.notion.so/ERD-23fcaf5650aa8174bb27e862a5f90394?source=copy_link)
>
> [**요구사항 정의서**](https://docs.google.com/spreadsheets/d/1Nojzpg3ORKn5J-omW843KtdvDWUguABfjSboDbz4Ja0/edit?usp=sharing)
> 
> [**테이블 명세서**](https://www.notion.so/23fcaf5650aa81d79fc5dd218c294c7d?source=copy_link)