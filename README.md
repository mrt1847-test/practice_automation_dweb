# G마켓 웹 자동화 테스트 프로젝트

Playwright와 pytest-bdd를 사용한 G마켓 웹사이트 자동화 테스트 프로젝트입니다.

## 📋 목차

- [프로젝트 개요](#프로젝트-개요)
- [아키텍처](#아키텍처)
- [프로젝트 구조](#프로젝트-구조)
- [설치 및 설정](#설치-및-설정)
- [실행 방법](#실행-방법)
- [주요 특징](#주요-특징)
- [TestRail 연동](#testrail-연동)

## 🎯 프로젝트 개요

이 프로젝트는 G마켓 웹사이트의 주요 기능을 자동화 테스트하는 BDD(Behavior-Driven Development) 기반 테스트 프레임워크입니다.

### 기술 스택

- **Python 3.11**
- **Playwright** - 브라우저 자동화
- **pytest** - 테스트 프레임워크
- **pytest-bdd** - BDD 시나리오 실행
- **TestRail** - 테스트 결과 관리

## 🏗️ 아키텍처

### 1. BDD (Behavior-Driven Development)

Gherkin 문법을 사용하여 비즈니스 요구사항을 자연어로 작성합니다.

```gherkin
Feature: G마켓 구매 플로우
  Scenario: 상품 검색
    Given 사용자가 G마켓 홈페이지에 접속한다
    And 사용자가 로그인되어 있다
    When 사용자가 "노트북"을 검색한다
    Then 검색 결과 페이지가 표시된다
```

### 2. Page Object Model (POM)

페이지별 로직과 로케이터를 분리하여 유지보수성을 높였습니다.

- **`pages/`**: 페이지별 Page Object 클래스
  - 로케이터 정의
  - 페이지별 기본 동작 메서드

- **`steps/`**: BDD Step Definitions
  - Page Object 메서드 조합
  - Given/When/Then 데코레이터

### 3. 독립적인 시나리오 패턴

각 시나리오는 독립적으로 실행 가능하며, **Given에서 필요한 상태를 보장**합니다.

#### Then: 증명 (검증만)
```python
@then("검색 결과 페이지가 표시된다")
def search_results_page_is_displayed(page):
    """검증만 수행"""
    search_page = SearchPage(page)
    assert search_page.is_search_results_displayed()
```

#### Given: 보장 (확인 + 필요시 생성)
```python
@given("검색 결과 페이지가 표시된다")
def search_results_page_is_displayed_given(page):
    """상태 확인 후, 없으면 강제로 생성"""
    search_page = SearchPage(page)
    if search_page.is_search_results_displayed():
        return  # 이미 상태가 맞음
    
    # 상태가 아니면 검색 수행
    home_page = HomePage(page)
    home_page.search_product("노트북")
```

이 패턴의 장점:
- ✅ 각 시나리오를 독립적으로 실행 가능
- ✅ 실패 격리: 한 시나리오 실패가 다른 시나리오에 영향 없음
- ✅ 재실행 안전: 같은 시나리오를 여러 번 실행해도 안전
- ✅ 디버깅 용이: 특정 시나리오만 재실행 가능

## 📁 프로젝트 구조

```
practice_automation_dweb/
├── features/              # BDD Feature 파일 (Gherkin)
│   ├── purchase_flow.feature
│   └── example.feature
│
├── steps/                 # Step Definitions
│   ├── home_steps.py
│   ├── login_steps.py
│   ├── search_steps.py
│   ├── product_steps.py
│   ├── cart_steps.py
│   └── checkout_steps.py
│
├── pages/                 # Page Object 클래스
│   ├── base_page.py       # 기본 Page Object
│   ├── home_page.py
│   ├── login_page.py
│   ├── search_page.py
│   ├── product_page.py
│   └── cart_page.py
│
├── utils/                 # 유틸리티
│   ├── testrail_step.py
│   └── step_log_capture.py
│
├── conftest.py           # pytest 설정 및 fixtures
├── pytest.ini            # pytest 설정
├── Pipfile               # 의존성 관리
└── README.md
```

## 🚀 설치 및 설정

### 1. 필수 요구사항

- Python 3.11
- pipenv (또는 pip)

### 2. 의존성 설치

```bash
# pipenv 사용
pipenv install

# 또는 pip 사용
pip install -r requirements.txt
```

### 3. Playwright 브라우저 설치

```bash
playwright install chromium
```

### 4. 환경 변수 설정

TestRail 연동을 위한 환경 변수 설정이 필요합니다 (선택사항).

## ▶️ 실행 방법

### 전체 테스트 실행

```bash
pytest
```

### 특정 Feature 파일 실행

```bash
pytest features/purchase_flow.feature
```

### 특정 시나리오 실행

```bash
pytest features/purchase_flow.feature::상품_검색
```

### 태그로 실행

```bash
# 특정 TestRail case ID로 실행
pytest -m C12345

# 여러 태그
pytest -m "C12345 or C12346"
```

### 상세 로그와 함께 실행

```bash
pytest -v -s
```

## ✨ 주요 특징

### 1. 독립적인 시나리오

각 시나리오는 독립적으로 실행 가능합니다:

```gherkin
@C12345
Scenario: 상품 검색
  Given 사용자가 G마켓 홈페이지에 접속한다
  And 사용자가 로그인되어 있다
  When 사용자가 "노트북"을 검색한다
  Then 검색 결과 페이지가 표시된다

@C12346
Scenario: 상품 선택
  Given 검색 결과 페이지가 표시된다  # ← 자동으로 상태 보장
  When 사용자가 첫 번째 상품을 선택한다
  Then 상품 상세 페이지가 표시된다
```

### 2. Page Object와 Step 분리

**Page Object (`pages/`)**: 로케이터와 기본 동작
```python
class SearchPage(BasePage):
    FIRST_PRODUCT = "a.item:first-child"
    
    def select_first_product(self) -> None:
        self.click(self.FIRST_PRODUCT)
```

**Step (`steps/`)**: BDD 시나리오 조합
```python
@when("사용자가 첫 번째 상품을 선택한다")
def user_selects_first_product(page):
    search_page = SearchPage(page)
    search_page.select_first_product()
```

### 3. 로그인 상태 유지

`conftest.py`에서 세션 단위로 로그인 상태를 유지하여 테스트 실행 시간을 단축합니다.

### 4. TestRail 자동 연동

각 시나리오의 태그(`@C12345`)를 기반으로 TestRail에 자동으로 결과를 기록합니다.

## 🔗 TestRail 연동

### 설정

`conftest.py`에서 TestRail 설정을 확인하세요.

### 사용 방법

Feature 파일에서 태그를 사용하여 TestRail case ID를 지정:

```gherkin
@C12345
Scenario: 상품 검색
  Given ...
  When ...
  Then ...
```

테스트 실행 시 자동으로 TestRail에 결과가 기록됩니다.

## 📝 예시

### Feature 파일 예시

```gherkin
# language: ko
Feature: G마켓 구매 플로우
  로그인부터 구매까지의 전체 플로우를 단계별로 테스트합니다.

  @C12345
  Scenario: 상품 검색
    Given 사용자가 G마켓 홈페이지에 접속한다
    And 사용자가 로그인되어 있다
    When 사용자가 "노트북"을 검색한다
    Then 검색 결과 페이지가 표시된다

  @C12346
  Scenario: 상품 선택
    Given 검색 결과 페이지가 표시된다
    When 사용자가 첫 번째 상품을 선택한다
    Then 상품 상세 페이지가 표시된다
```

### Step Definition 예시

```python
from pytest_bdd import given, when, then
from pages.search_page import SearchPage

@when("사용자가 첫 번째 상품을 선택한다")
def user_selects_first_product(page):
    search_page = SearchPage(page)
    search_page.select_first_product()
```

### Page Object 예시

```python
class SearchPage(BasePage):
    FIRST_PRODUCT = "a.item:first-child"
    
    def select_first_product(self) -> None:
        self.page.wait_for_load_state("networkidle")
        self.click(self.FIRST_PRODUCT, timeout=10000)
```

## 📚 참고 자료

- [Playwright 문서](https://playwright.dev/python/)
- [pytest-bdd 문서](https://pytest-bdd.readthedocs.io/)
- [Gherkin 문법](https://cucumber.io/docs/gherkin/)

## 🤝 기여

이슈나 개선 사항이 있으면 이슈를 등록해주세요.

## 📄 라이선스

이 프로젝트는 내부 사용을 위한 프로젝트입니다.



