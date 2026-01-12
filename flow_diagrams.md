# G마켓 자동화 테스트 프로젝트 - 플로우 다이어그램

Mermaid Live Editor (https://mermaid.live)에서 사용할 수 있는 다이어그램 코드입니다.

**⚠️ 중요: Mermaid Live Editor에 붙여넣을 때는 아래 각 코드 블록의 내용만 복사하세요!**
- ```mermaid 와 ``` 사이의 코드만 복사
- 마크다운 형식(---, ## 등)은 제외

---

## 1. 프로젝트 아키텍처 다이어그램

```mermaid
graph TB
    subgraph L1["📋 L1: 비즈니스 계층"]
        direction LR
        F1(Feature Files<br/>.feature<br/>Gherkin 시나리오)
    end
    
    subgraph L2["⚡ L2: 행위 계층"]
        direction LR
        S1(Step Definitions<br/>steps/*.py<br/>@given @when @then)
    end
    
    subgraph L3["🎯 L3: 객체 계층"]
        direction LR
        P1(Page Objects<br/>home_page, login_page<br/>search_page 등)
    end
    
    subgraph L4["🔧 L4: 엔진 계층"]
        direction LR
        E1(conftest.py<br/>Fixtures & Hooks)
        E2(PlaywrightSharedState<br/>Browser/Context/Page)
        E1 --> E2
    end
    
    subgraph TR["📊 TestRail 통합"]
        direction LR
        TR1(Session Hooks)
        TR2(TestRail API)
        TR1 --> TR2
    end
    
    L1 --> L2
    L2 --> L3
    L3 --> E2
    
    L1 -.->|C12345 태그| TR1
    E2 -.->|스크린샷| TR1
    
    Config(Config/Utils<br/>config.json<br/>credentials.py<br/>urls.py)
    E1 -.-> Config
    S1 -.-> Config
    P1 -.-> Config
    
    style L1 fill:#f8f5fc,stroke:#ce93d8,stroke-width:2px
    style L2 fill:#e8f7fd,stroke:#81d4fa,stroke-width:2px
    style L3 fill:#f1f8e9,stroke:#aed581,stroke-width:2px
    style L4 fill:#fff8e5,stroke:#ffcc80,stroke-width:2px
    style TR fill:#e8f5f3,stroke:#80deea,stroke-width:2px
    style Config fill:#fce4ec,stroke:#f48fb1,stroke-width:2px
    
    style F1 fill:#f3e5f5
    style S1 fill:#e1f5fe
    style P1 fill:#e8f5e9
    style E1 fill:#fff3e0
    style E2 fill:#fff3e0
    style TR1 fill:#e0f2f1
    style TR2 fill:#b2dfdb
```

---

## 2. 구매 플로우 시퀀스 다이어그램

```mermaid
sequenceDiagram
    participant Test as pytest
    participant Feature as purchase_flow.feature
    participant Steps as Step Definitions
    participant Pages as Page Objects
    participant Browser as Playwright Browser
    participant TR as TestRail
    
    Test->>Feature: 시나리오 실행
    Test->>TR: Session Start (Run 생성)
    
    Note over Feature: Scenario 1: 로그인
    Feature->>Steps: Given 홈페이지 접속
    Steps->>Pages: HomePage.navigate()
    Pages->>Playwright: page.goto(BASE_URL)
    
    Feature->>Steps: When 로그인 버튼 클릭
    Steps->>Pages: HomePage.click_login()
    Pages->>Playwright: 클릭 동작
    
    Feature->>Steps: And 일반회원 로그인
    Steps->>Pages: LoginPage.login_as()
    Pages->>Playwright: 입력 및 클릭
    
    Note over Feature: Scenario 2: 검색
    Feature->>Steps: Given 로그인되어 있음
    Steps->>Pages: HomePage.is_logged_in()
    
    Feature->>Steps: When "물티슈" 검색
    Steps->>Pages: HomePage.fill_search_input()<br/>HomePage.click_search_button()
    Pages->>Playwright: 검색 실행
    
    Note over Feature: Scenario 3: 상품 클릭
    Feature->>Steps: When 모듈 내 상품 클릭
    Steps->>Pages: SearchPage.click_product()
    Pages->>Playwright: 상품 클릭
    
    Note over Feature: Scenario 4: 구매하기
    Feature->>Steps: When 구매하기 버튼 클릭
    Steps->>Pages: ProductPage.click_purchase()
    Pages->>Playwright: 구매하기 클릭
    
    Note over Feature: Scenario 5: 주문 생성
    Feature->>Steps: When 무통장입금 선택
    Steps->>Pages: CheckoutPage.select_payment()
    Pages->>Playwright: 결제 수단 선택
    
    Feature->>Steps: And 주문 생성
    Steps->>Pages: CheckoutPage.create_order()
    Pages->>Playwright: 주문 생성
    
    Feature->>Steps: Then 주문 상태 확인
    Steps->>Pages: OrderPage.verify_status()
    Pages->>Playwright: 상태 확인
    
    Steps->>TR: Make Report (결과 기록)
    Playwright-.->|스크린샷|TR: 실패 시 첨부
    
    Test->>TR: Session Finish (Run 종료)
```

---

## 3. 전체 테스트 실행 플로우

```mermaid
graph TD
    Start[pytest 실행] --> LoadScenarios[test_features.py<br/>scenarios 로드]
    
    LoadScenarios --> SessionStart[pytest_sessionstart<br/>TestRail Run 생성]
    SessionStart --> TestRailInit[TestRail API<br/>Run 생성]
    
    LoadScenarios --> LoadFeatures[Feature Files 로드<br/>.feature]
    
    LoadFeatures --> BeforeScenario[pytest_bdd_before_scenario<br/>Feature별 브라우저 환경 생성]
    BeforeScenario --> CreateContext[Playwright Context 생성]
    CreateContext --> CreatePage[Page 생성]
    CreatePage --> CreateSession[BrowserSession 생성]
    
    LoadFeatures --> ExecuteScenario[시나리오 실행<br/>@C12345 태그 추출]
    
    ExecuteScenario --> StepMatch[Step Definition 매칭<br/>steps/*.py]
    StepMatch --> PageCall[Page Object 메서드 호출]
    PageCall --> PlaywrightAction[Playwright API 호출]
    PlaywrightAction --> PlaywrightState[PlaywrightSharedState<br/>Browser/Context/Page]
    
    ExecuteScenario --> LogReport[pytest_runtest_logreport<br/>로그 수집]
    
    ExecuteScenario --> MakeReport[pytest_runtest_makereport<br/>결과 기록]
    MakeReport --> ExtractCaseId[Case ID 추출<br/>@C12345 태그]
    MakeReport --> CaptureScreenshot[실패 시 스크린샷]
    MakeReport --> SendResult[TestRail API<br/>결과 전송]
    
    PlaywrightState -.->|스크린샷| CaptureScreenshot
    CaptureScreenshot --> SendResult
    
    ExecuteScenario --> NextScenario{다음 시나리오?}
    NextScenario -->|Yes| ExecuteScenario
    NextScenario -->|No| SessionFinish
    
    SessionFinish[pytest_sessionfinish<br/>TestRail Run 종료] --> TestRailClose[TestRail API<br/>Run 종료]
    TestRailClose --> End[테스트 완료]
    
    style Start fill:#e3f2fd
    style SessionStart fill:#e0f2f1
    style TestRailInit fill:#b2dfdb
    style BeforeScenario fill:#fff3e0
    style ExecuteScenario fill:#f5f5f5
    style MakeReport fill:#e0f2f1
    style SendResult fill:#b2dfdb
    style SessionFinish fill:#e0f2f1
    style End fill:#e3f2fd
```

---

## 4. 컴포넌트 간 의존성 다이어그램

```mermaid
graph TB
    %% ===== Style Definitions =====
    classDef l1 fill:#f1f5f9,stroke:#334155,stroke-width:1.5px
    classDef l2 fill:#e8f1f8,stroke:#1e40af,stroke-width:1.5px
    classDef l3 fill:#f0fdf4,stroke:#166534,stroke-width:1.5px
    classDef l4 fill:#fffbeb,stroke:#92400e,stroke-width:1.5px
    classDef ext fill:#f8fafc,stroke:#475569,stroke-dasharray:5 5
    classDef cfg fill:#ffffff,stroke:#94a3b8,stroke-dasharray:3 3

    %% ===== Layers =====
    subgraph L1["L1 · 비즈니스 계층"]
        F1(Feature Files<br/>Gherkin 시나리오)
    end

    subgraph L2["L2 · 행위 계층"]
        S1(Step Definitions<br/>@given @when @then)
    end

    subgraph L3["L3 · 객체 계층"]
        P1(Page Objects)
    end

    subgraph L4["L4 · 엔진 계층"]
        E1(Pytest Fixtures & Hooks)
        E2(Playwright Shared State)
        E1 --> E2
    end

    subgraph EXT["외부 시스템 연동"]
        TR1(TestRail Session Hook)
        TR2(TestRail API)
        TR1 --> TR2
    end

    %% ===== Flow =====
    L1 --> L2 --> L3 --> E2
    L1 -.->|케이스 ID 매핑| TR1
    E2 -.->|테스트 증적| TR1

    %% ===== Config =====
    Config(Config / Utils)
    Config -.-> S1
    Config -.-> P1
    Config -.-> E1

    %% ===== Class Mapping =====
    class L1,F1 l1
    class L2,S1 l2
    class L3,P1 l3
    class L4,E1,E2 l4
    class EXT,TR1,TR2 ext
    class Config cfg
```

---

## 사용 방법

### ⚠️ 중요 사항
**Mermaid Live Editor에는 순수한 Mermaid 코드만 입력해야 합니다!**
- 파일 전체를 복사하지 마세요
- 각 다이어그램의 ```mermaid 와 ``` 사이의 코드만 복사하세요
- 마크다운 형식(---, ##, ``` 등)은 복사하지 마세요

### 단계별 사용법

1. **Mermaid Live Editor 접속**: https://mermaid.live
2. **코드 블록 열기**: 위에서 원하는 다이어그램의 ```mermaid 시작 부분 찾기
3. **코드 복사**: ```mermaid부터 다음 ```까지의 코드만 복사
   - 예: ```mermaid 다음 줄부터 시작
   - ``` 전 줄까지 복사
4. **붙여넣기**: Mermaid Live Editor의 왼쪽 편집창에 붙여넣기
5. **확인**: 오른쪽에서 다이어그램이 올바르게 렌더링되는지 확인

각 다이어그램은 독립적으로 사용할 수 있습니다.

