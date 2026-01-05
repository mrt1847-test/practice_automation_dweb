# G마켓 자동화 테스트 프로젝트

BDD(Behavior-Driven Development) 방식의 G마켓 구매 플로우 자동화 테스트 프로젝트입니다.

## 설치 방법

### 1. Pipenv 설치 (아직 설치하지 않은 경우)

```bash
pip install pipenv
```

### 2. 가상환경 생성 및 패키지 설치

**방법 1: requirements.txt 사용 (권장)**
```bash
pipenv install -r requirements.txt
```

**방법 2: Pipfile이 이미 있는 경우**
```bash
pipenv install
```

이 명령어는 다음을 수행합니다:
- 가상환경 자동 생성
- `requirements.txt` 또는 `Pipfile`에서 패키지 설치
- `Pipfile`과 `Pipfile.lock` 자동 생성

### 3. 가상환경 활성화

```bash
pipenv shell
```

### 4. Playwright 브라우저 설치

```bash
playwright install
```

또는 Chromium만 설치:
```bash
playwright install chromium
```

### 5. 환경 변수 설정 (.env 파일)

프로젝트 루트에 `.env` 파일을 생성하고 회원 종류별 계정 정보를 설정하세요.

**환경별 분기:**
- `config.json`의 `environment` 설정에 따라 자동으로 분기됩니다
- **dev 환경**: `DEV_` 접두사가 붙은 환경 변수 사용
- **stg/prod 환경**: 접두사 없이 기본 환경 변수 사용 (stg와 prod는 동일한 계정 정보 사용)

#### Stg/Prod 환경 설정 예시:
```bash
# .env 파일 (stg 또는 prod 환경 - config.json에서 "environment": "stg" 또는 "prod"로 설정)
# 일반회원
NORMAL_MEMBER_ID=일반회원아이디
NORMAL_MEMBER_PASSWORD=일반회원비밀번호

# 클럽회원
CLUB_MEMBER_ID=클럽회원아이디
CLUB_MEMBER_PASSWORD=클럽회원비밀번호

# 사업자회원
BUSINESS_MEMBER_ID=사업자회원아이디
BUSINESS_MEMBER_PASSWORD=사업자회원비밀번호
```

#### Dev 환경 설정 예시:
```bash
# .env 파일 (dev 환경 - config.json에서 "environment": "dev"로 설정)
# 일반회원
DEV_NORMAL_MEMBER_ID=dev일반회원아이디
DEV_NORMAL_MEMBER_PASSWORD=dev일반회원비밀번호

# 클럽회원
DEV_CLUB_MEMBER_ID=dev클럽회원아이디
DEV_CLUB_MEMBER_PASSWORD=dev클럽회원비밀번호

# 사업자회원
DEV_BUSINESS_MEMBER_ID=dev사업자회원아이디
DEV_BUSINESS_MEMBER_PASSWORD=dev사업자회원비밀번호
```

**주의:** 
- `.env` 파일은 `.gitignore`에 포함되어 있어 Git에 커밋되지 않습니다. 실제 계정 정보를 안전하게 관리하세요.
- `config.json`의 `environment` 값을 변경하면 자동으로 해당 환경의 계정 정보를 사용합니다.

**참고:**
- `pipenv install`을 실행하면 `Pipfile`과 `Pipfile.lock`이 생성됩니다
- 이후 패키지 설치/업데이트는 `pipenv install <package>` 또는 `pipenv update`를 사용하세요
- 가상환경을 나가려면 `exit` 명령어를 사용하세요

## 테스트 실행

**참고:** pipenv 환경에서는 `pipenv run pytest` 또는 `pipenv shell` 후 `pytest`를 사용하세요.

### 전체 테스트 실행
```bash
pipenv run pytest
```

또는 가상환경 활성화 후:
```bash
pipenv shell
pytest --cache-clear
```

### 특정 feature 파일 실행

먼저 `test_features.py`에서 특정 feature 파일만 로드하도록 수정:
```python
# test_features.py
from pytest_bdd import scenarios
scenarios("features/purchase_flow.feature")  # 특정 파일만 지정
```

그 후 실행:
```bash
pipenv run pytest --cache-clear -m test_001 -v
```

> **참고**: `-m test_001` 옵션은 특정 feature 파일에 마커(태그)를 추가한 후 해당 마커가 있는 테스트만 실행하는 명령어입니다.
> 
> Feature 파일에 마커를 추가하려면 feature 파일 상단에 태그를 추가하세요:
> ```gherkin
> @test_001
> Feature: Purchase Flow
>   ...
> ```
> 
> 이렇게 하면 `-m test_001` 옵션으로 해당 feature 파일의 시나리오만 실행할 수 있습니다.

### 특정 시나리오 실행
```bash
pipenv run pytest --cache-clear -k "무통장입금" -v
```

### 디버그 모드로 실행
```bash
pipenv run pytest --cache-clear -vv -s --log-cli-level=DEBUG
```

## 프로젝트 구조

```
.
├── features/              # Gherkin feature 파일들
│   └── purchase_flow.feature
├── steps/                 # Step definitions
│   ├── home_steps.py
│   ├── login_steps.py
│   ├── search_steps.py
│   ├── product_steps.py
│   ├── cart_steps.py
│   ├── checkout_steps.py
│   └── order_steps.py
├── pages/                  # Page Object Model
│   ├── base_page.py
│   ├── home_page.py
│   ├── login_page.py
│   ├── search_page.py
│   ├── product_page.py
│   ├── cart_page.py
│   └── checkout_page.py
├── conftest.py            # Pytest 설정 및 fixtures
├── test_features.py       # Feature 파일 등록
├── pytest.ini             # Pytest 설정
└── requirements.txt       # 패키지 의존성
```

## 주요 기능

- BDD 방식의 테스트 작성 (Gherkin)
- Page Object Model 패턴 사용
- Playwright를 이용한 브라우저 자동화
- TestRail 연동 (태그 기반)
- 모듈 단위 fixture scope로 상태 공유

## 참고사항

- 브라우저는 기본적으로 headless=False로 실행됩니다 (화면에 표시)
- `conftest.py`에서 브라우저 설정을 변경할 수 있습니다
- 각 시나리오는 독립적으로 실행 가능하며, Given에서 필요한 상태를 보장합니다
