# pytest_plugins는 파일 최상단에 위치해야 함 (다른 import보다 먼저)
pytest_plugins = [
    "pytest_bdd",
    "steps.home_steps",
    "steps.login_steps",
    "steps.search_steps",
    "steps.product_steps",
    "steps.cart_steps",
    "steps.checkout_steps",
    "steps.order_steps",
]

import shutil
from playwright.sync_api import sync_playwright, Browser, BrowserContext, Page
from src.gtas_python_core_v2.gtas_python_core_vault_v2 import Vault
import os
import pytest
import requests
from datetime import datetime
from pathlib import Path
import json
import time
import re
import logging

logger = logging.getLogger(__name__)

# 브라우저 fixture (세션 단위, 한 번만 실행)
@pytest.fixture(scope="session")
def browser():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, args=["--start-maximized"])  # True/False로 headless 제어
        yield browser
        browser.close()


# 컨텍스트 fixture (브라우저 환경)
@pytest.fixture(scope="module")
def context(browser: Browser):
    context = browser.new_context(no_viewport=True)

    # navigator.webdriver 우회
    context.add_init_script("""
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined
        });
    """)

    yield context
    context.close()


# BrowserSession 클래스
class BrowserSession:
    """
    브라우저 세션 관리 클래스 - 현재 active page 참조 관리
    상태 관리자 역할: page stack을 통해 탭 전환 추적
    """
    def __init__(self, page):
        """
        BrowserSession 초기화
        
        Args:
            page: fixture에서 생성한 기본 page (seed 역할)
        """
        self._page_stack = [page]  # page stack으로 전환 이력 관리
    
    @property
    def page(self):
        """
        현재 active page 반환 (가장 최근에 전환된 page)
        """
        return self._page_stack[-1]
    
    def switch_to(self, page):
        """
        새 페이지로 전환 (명시적 전환)
        
        Args:
            page: 전환할 Page 객체
        
        Returns:
            bool: 전환 성공 여부
        """
        if not page:
            logger.warning("BrowserSession: None 페이지로 전환 시도 실패")
            return False
        
        try:
            if page.is_closed():
                logger.warning("BrowserSession: 이미 닫힌 페이지로 전환 시도 실패")
                return False
            
            # 페이지 유효성 검증
            current_url = page.url
            if not current_url or current_url == "about:blank":
                logger.warning(f"BrowserSession: 유효하지 않은 URL의 페이지: {current_url}")
                # about:blank는 잠시 후 로드될 수 있으므로 경고만
            
            self._page_stack.append(page)
            logger.info(f"BrowserSession: 새 페이지로 전환 - URL: {current_url} (stack depth: {len(self._page_stack)})")
            return True
        except Exception as e:
            logger.error(f"BrowserSession: 페이지 전환 중 오류 발생: {e}")
            return False
    
    def restore(self):
        """
        이전 페이지로 복귀 (page stack에서 pop)
        
        Returns:
            bool: 복귀 성공 여부 (stack에 이전 페이지가 있는 경우)
        """
        if len(self._page_stack) > 1:
            previous_page = self._page_stack.pop()
            logger.info(f"BrowserSession: 이전 페이지로 복귀 - 현재 URL: {self.page.url} (stack depth: {len(self._page_stack)})")
            return True
        else:
            logger.warning("BrowserSession: 복귀할 이전 페이지가 없음")
            return False
    
    def get_page_stack(self):
        """
        디버깅용: 현재 page stack의 URL 리스트 반환
        
        Returns:
            list: page stack의 URL 리스트
        """
        return [p.url for p in self._page_stack]


# BrowserSession fixture
@pytest.fixture(scope="module")
def browser_session(page):
    """
    BrowserSession fixture - 현재 active page 참조 관리
    module scope로 유지하여 같은 feature 파일의 시나리오들이 같은 세션을 공유
    
    Args:
        page: fixture에서 생성한 기본 page (seed 역할)
    """
    return BrowserSession(page)


# 페이지 fixture
@pytest.fixture(scope="module")
def page(context: BrowserContext):
    page = context.new_page()
    page.set_default_timeout(10000)  # 기본 10초 타임아웃
    yield page
    page.close()


# BDD context fixture (시나리오 내 스텝 간 데이터 공유를 위한 전용 객체)
# pytest-bdd의 내부 scenario fixture에 의존하지 않고 독립적으로 동작
@pytest.fixture(scope="module")
def bdd_context():
    """
    시나리오 내 스텝 간 데이터 공유를 위한 전용 객체
    같은 feature 파일 내의 모든 시나리오가 같은 context를 공유 (module scope)
    이름 충돌이 없고, 시나리오 메타데이터와 비즈니스 데이터를 분리해서 관리
    """
    class Context:
        def __init__(self):
            self.store = {}
    
    return Context()


# STATE_PATH = "state.json"
# GMARKET_URL = "https://www.gmarket.co.kr"  # 모바일 페이지 기준 셀렉터 안정성


# def pytest_addoption(parser):
#     """pytest 커맨드 라인 옵션 추가"""
#     parser.addoption(
#         "--case-id",
#         action="store",
#         default=None,
#         help="TestRail case ID (일반 pytest 테스트용)"
#     )
# # ------------------------
# # :일: Playwright 세션 단위 fixture
# # ------------------------
# @pytest.fixture(scope="session")
# def pw():
#     """Playwright 세션 관리"""
#     with sync_playwright() as p:
#         yield p
# # ------------------------
# # :둘: 브라우저 fixture
# # ------------------------
# @pytest.fixture(scope="session")
# def browser(pw):
#     """세션 단위 브라우저"""
#     browser = pw.chromium.launch(headless=False)
#     yield browser
#     browser.close()
# # ------------------------
# # :셋: 로그인 상태 검증
# # ------------------------
# def is_state_valid(state_path: str) -> bool:
#     """state.json이 유효한지 확인 (쿠키 기반)"""
#     if not os.path.exists(state_path):
#         return False
#     try:
#         with open(state_path, "r", encoding="utf-8") as f:
#             data = json.load(f)
#         cookies = data.get("cookies", [])
#         now = time.time()
#         # 쿠키 하나라도 만료되지 않았으면 로그인 유지 가능
#         if any("expires" in c and c["expires"] and c["expires"] > now for c in cookies):
#             return True
#         return False
#     except Exception as e:
#         print(f"[WARN] state.json 검증 오류: {e}")
#         return False
# # ------------------------
# # :넷: 로그인 수행 + state.json 저장
# # ------------------------
# def create_login_state(pw):
#     """로그인 수행 후 state.json 저장"""
#     print("[INFO] 로그인 절차 시작")
#     browser = pw.chromium.launch(headless=False)  # 화면 확인용
#     context = browser.new_context()
#     page = context.new_page()
#     page.goto(GMARKET_URL)
#     # 로그인 페이지 이동 및 입력
#     page.locator("text=로그인").click()
#     page.locator("#typeMemberInputId").fill("t4adbuy01")
#     page.locator("#typeMemberInputPassword").fill("Gmkt1004!!")
#     page.locator("#btn_memberLogin").click()
#     # 로그인 완료 대기
#     page.wait_for_selector("text=로그아웃", timeout=15000)
#     # 로그인 상태 저장
#     context.storage_state(path=STATE_PATH)
#     browser.close()
#     print("[INFO] 로그인 완료 및 state.json 저장됨")
# # ------------------------
# # :다섯: 로그인 상태 fixture
# # ------------------------
# @pytest.fixture(scope="session")
# def ensure_login_state(pw):
#     """
#     state.json 존재 여부 및 유효성 확인.
#     없거나 만료 시 자동 로그인 수행
#     """
#     if not os.path.exists(STATE_PATH):
#         print("[INFO] state.json 없음 → 로그인 시도")
#         create_login_state(pw)
#     elif not is_state_valid(STATE_PATH):
#         print("[INFO] state.json 만료됨 → 재로그인 시도")
#         create_login_state(pw)
#     else:
#         print("[INFO] 로그인 세션 유효 → 기존 state.json 사용")
#     return STATE_PATH
# # ------------------------
# # :여섯: page fixture
# # ------------------------
# @pytest.fixture(scope="module")
# def page(browser, ensure_login_state):
#     """
#     로그인 상태가 보장된 page fixture
#     같은 feature 파일 내의 시나리오들이 같은 page를 공유
#     """
#     context = browser.new_context(storage_state=ensure_login_state)
#     page = context.new_page()
#     page.set_default_timeout(30000)  # 기본 타임아웃 30초
#     yield page
#     context.close()


# pytest-bdd 통합: BDD 시나리오에서 case_id 추출을 위한 fixture
@pytest.fixture
def case_id(request):
    """
    BDD 시나리오의 태그에서 case_id를 추출
    feature 파일에서 @C12345 형식의 태그를 사용하면 자동으로 추출됨
    """
    # pytest-bdd 시나리오의 태그에서 case_id 추출
    # request.keywords에서 마커 확인
    for marker in request.node.iter_markers():
        marker_name = marker.name
        # @C12345 형식의 태그 찾기
        if marker_name.startswith("C") and len(marker_name) > 1 and marker_name[1:].isdigit():
            return marker_name
    
    # nodeid에서도 확인
    nodeid = request.node.nodeid
    match = re.search(r'\[C(\d+)\]', nodeid)
    if match:
        return f"C{match.group(1)}"
    
    # 일반 pytest 테스트의 경우 커맨드 라인 옵션에서 가져오기
    return request.config.getoption("--case-id", default=None)



with open('config.json') as config_file:
    config = json.load(config_file)

# 환경변수 기반 설정
TESTRAIL_BASE_URL = config['tr_url']
TESTRAIL_PROJECT_ID = config['project_id']
TESTRAIL_SUITE_ID = config['suite_id']
TESTRAIL_SECTION_ID = config['section_id']  # ✅ 섹션 이름으로 지정
TESTRAIL_USER = (Vault("gmarket").get_Kv_credential("authentication/testrail/automation")).get("username")
TESTRAIL_TOKEN = (Vault("gmarket").get_Kv_credential("authentication/testrail/automation")).get("password")
TESTRAIL_MILESTONE_ID = config['milestone_id']
testrail_run_id = None
case_id_map = {}  # {섹션 이름: [케이스ID 리스트]}
test_logs = {}  # {nodeid: 로그 문자열} - 테스트별 로그 저장
current_test_nodeid = None  # 현재 실행 중인 테스트의 nodeid
active_browser_sessions = {}  # {feature_file: {nodeid: browser_session}} - feature 파일별로 browser_session 저장


def testrail_get(endpoint):
    url = f"{TESTRAIL_BASE_URL}/index.php?/api/v2/{endpoint}"
    r = requests.get(url, auth=(TESTRAIL_USER, TESTRAIL_TOKEN))
    r.raise_for_status()
    return r.json()


def testrail_post(endpoint, payload=None, files=None):
    url = f"{TESTRAIL_BASE_URL}/index.php?/api/v2/{endpoint}"
    if files:
        r = requests.post(url, auth=(TESTRAIL_USER, TESTRAIL_TOKEN), files=files)
    else:
        r = requests.post(url, auth=(TESTRAIL_USER, TESTRAIL_TOKEN), json=payload)
    r.raise_for_status()
    return r.json()




def get_all_subsection_ids(parent_section_id, all_sections):
    """
    지정된 섹션 ID와 모든 하위 섹션 ID를 재귀적으로 찾기
    
    Args:
        parent_section_id: 부모 섹션 ID (int 또는 str)
        all_sections: 모든 섹션 리스트 (TestRail API에서 가져온 전체 섹션)
    
    Returns:
        list: 부모 섹션 ID와 모든 하위 섹션 ID 리스트
    """
    # 타입 통일 (정수로 변환)
    if isinstance(parent_section_id, str):
        try:
            parent_section_id = int(parent_section_id)
        except ValueError:
            print(f"[WARNING] parent_section_id를 정수로 변환 실패: {parent_section_id}")
            return [parent_section_id]
    
    section_ids = [parent_section_id]
    
    # parent_id가 parent_section_id인 모든 하위 섹션 찾기
    for section in all_sections:
        section_parent_id = section.get("parent_id")
        
        # parent_id가 None이면 최상위 섹션이므로 스킵
        if section_parent_id is None:
            continue
        
        # 타입 통일 (정수로 변환)
        if isinstance(section_parent_id, str):
            try:
                section_parent_id = int(section_parent_id)
            except ValueError:
                continue
        
        # parent_id가 일치하는 경우
        if section_parent_id == parent_section_id:
            child_section_id = section["id"]
            # 타입 통일
            if isinstance(child_section_id, str):
                try:
                    child_section_id = int(child_section_id)
                except ValueError:
                    continue
            
            section_ids.append(child_section_id)
            # 재귀적으로 하위 섹션의 하위 섹션도 찾기
            section_ids.extend(get_all_subsection_ids(child_section_id, all_sections))
    
    return section_ids


@pytest.hookimpl(tryfirst=True)
def pytest_sessionstart(session):
    """
    테스트 실행 시작 시:
    1. section_id 기반으로 해당 섹션과 모든 하위 섹션의 케이스 ID 가져오기
    2. 그 케이스들로 Run 생성
    """
    global testrail_run_id, case_id_map
    
    if testrail_run_id is not None:
        print(f"[TestRail] 이미 Run(ID={testrail_run_id})이 존재합니다. 새 Run 생성 생략")
        return
    
    if not TESTRAIL_SECTION_ID:
        raise RuntimeError("[TestRail] TESTRAIL_SECTION_ID가 정의되지 않았습니다.")
    
    # TESTRAIL_SECTION_ID를 정수로 변환
    try:
        section_id_int = int(TESTRAIL_SECTION_ID)
    except (ValueError, TypeError):
        raise RuntimeError(f"[TestRail] TESTRAIL_SECTION_ID '{TESTRAIL_SECTION_ID}'를 정수로 변환할 수 없습니다.")
    
    # 1. 모든 섹션 가져오기
    print(f"[TestRail] 모든 섹션 가져오기 중...")
    all_sections = testrail_get(
        f"get_sections/{TESTRAIL_PROJECT_ID}&suite_id={TESTRAIL_SUITE_ID}"
    )
    
    # 디버깅: 섹션 구조 확인
    print(f"[TestRail] 총 {len(all_sections)}개 섹션 발견")
    print(f"[TestRail] 찾고자 하는 섹션 ID: {section_id_int} (타입: {type(section_id_int).__name__})")
    
    # 지정된 섹션이 존재하는지 확인
    section_exists = any(s.get("id") == section_id_int for s in all_sections)
    if not section_exists:
        print(f"[WARNING] 섹션 ID {section_id_int}가 존재하지 않습니다.")
        print(f"[DEBUG] 사용 가능한 섹션 ID 샘플 (최대 10개):")
        for s in all_sections[:10]:
            print(f"  - ID: {s.get('id')}, Name: {s.get('name')}, Parent ID: {s.get('parent_id')}")
    
    # 2. 지정된 섹션과 모든 하위 섹션 ID 찾기
    all_section_ids = get_all_subsection_ids(section_id_int, all_sections)
    print(f"[TestRail] 섹션 ID {section_id_int}와 하위 섹션 {len(all_section_ids) - 1}개 발견: {all_section_ids}")
    
    # 3. 각 섹션의 케이스 가져오기
    all_case_ids = []
    for section_id in all_section_ids:
        try:
            cases = testrail_get(
                f"get_cases/{TESTRAIL_PROJECT_ID}&suite_id={TESTRAIL_SUITE_ID}&section_id={section_id}"
            )
            section_case_ids = [c["id"] for c in cases]
            all_case_ids.extend(section_case_ids)
            case_id_map[section_id] = section_case_ids
            if section_case_ids:
                print(f"[TestRail] 섹션 {section_id}: {len(section_case_ids)}개 케이스 발견")
        except Exception as e:
            print(f"[WARNING] 섹션 {section_id}의 케이스 가져오기 실패: {e}")
    
    # 중복 제거 (같은 케이스가 여러 섹션에 있을 수 있음)
    all_case_ids = list(set(all_case_ids))
    
    if not all_case_ids:
        raise RuntimeError(f"[TestRail] section_id '{section_id_int}'와 하위 섹션에 케이스가 없습니다.")
    
    print(f"[TestRail] 총 {len(all_case_ids)}개 케이스 수집 완료")
    
    # 4. Run 생성
    run_name = f"AD Regression test dweb {datetime.now():%Y-%m-%d %H:%M:%S}"
    payload = {
        "suite_id": TESTRAIL_SUITE_ID,
        "name": run_name,
        "include_all": False,
        "case_ids": all_case_ids,
        "milestone_id": TESTRAIL_MILESTONE_ID
    }
    run = testrail_post(f"add_run/{TESTRAIL_PROJECT_ID}", payload)
    testrail_run_id = run["id"]
    print(f"[TestRail] section_id '{section_id_int}' (하위 섹션 포함) Run 생성 완료 (ID={testrail_run_id})")


# 커스텀 로그 핸들러 - 테스트 실행 중 로그를 수집
class TestLogHandler(logging.Handler):
    """테스트 실행 중 로그를 수집하는 커스텀 핸들러"""
    def __init__(self):
        super().__init__()
        self.logs = []
    
    def emit(self, record):
        """로그 레코드를 수집"""
        if record.levelno >= logging.INFO:  # INFO 이상만 수집
            log_message = self.format(record)
            self.logs.append(log_message)
    
    def clear(self):
        """로그 초기화"""
        self.logs = []
    
    def get_logs(self):
        """수집된 로그 반환"""
        return "\n".join(self.logs)

# 전역 로그 핸들러
test_log_handler = TestLogHandler()
test_log_handler.setLevel(logging.INFO)
test_log_handler.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))

# 루트 로거에 핸들러 추가
root_logger = logging.getLogger()
root_logger.addHandler(test_log_handler)


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_setup(item):
    """테스트 시작 시 로그 핸들러 초기화 및 browser_session 저장 (feature 파일별로 분리)"""
    global current_test_nodeid
    current_test_nodeid = item.nodeid
    test_log_handler.clear()
    
    # browser_session fixture가 있으면 feature 파일별로 저장
    try:
        if hasattr(item, '_request'):
            if "browser_session" in item._request.fixturenames:
                browser_session = item._request.getfixturevalue("browser_session")
                if browser_session:
                    # feature 파일 이름 추출 (nodeid에서 첫 번째 부분)
                    # 예: "test_features.py::test_g_마켓_접속후_로그인" -> "test_features.py"
                    # 또는 "features/purchase_flow.feature::test_g_마켓_접속후_로그인" -> "features/purchase_flow.feature"
                    feature_file = item.nodeid.split("::")[0]
                    
                    # feature 파일별 딕셔너리 초기화
                    if feature_file not in active_browser_sessions:
                        active_browser_sessions[feature_file] = {}
                    
                    # 해당 feature 파일의 nodeid로 저장
                    active_browser_sessions[feature_file][item.nodeid] = browser_session
                    print(f"[DEBUG] browser_session 저장: {feature_file} -> {item.nodeid}")
    except Exception as e:
        print(f"[DEBUG] browser_session 저장 실패: {e}")
    
    outcome = yield


@pytest.hookimpl(hookwrapper=True, tryfirst=True)
def pytest_runtest_logreport(report):
    """
    각 테스트의 로그를 수집하여 test_logs에 저장
    pytest_runtest_makereport보다 먼저 실행되도록 tryfirst=True 설정
    """
    outcome = yield
    # setup, call, teardown 모든 단계에서 로그 수집
    if report.when == "call":  # 실행 단계만
        nodeid = report.nodeid
        if report.outcome in ("passed", "failed", "skipped"):
            # 수집된 로그 가져오기
            logs = test_log_handler.get_logs()
            if logs and logs.strip():
                test_logs[nodeid] = logs
                print(f"[DEBUG] 테스트 {nodeid} 로그 수집 완료: {len(logs.split(chr(10)))}줄")
            else:
                print(f"[DEBUG] 테스트 {nodeid} 로그 없음 (빈 로그 또는 수집 실패)")


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    각 테스트 결과를 TestRail에 기록 + 실패 시 스크린샷 첨부
    INTERNALERROR 방지를 위해 모든 외부 호출은 try/except로 보호
    BDD 시나리오와 일반 pytest 테스트 모두 지원
    """
    outcome = yield
    result = outcome.get_result()

    try:
        # BDD 시나리오의 경우 태그에서 case_id 추출
        case_id = None

        # 1. funcargs에서 case_id 파라미터 확인 (가장 우선순위)
        # Scenario Outline의 Examples 테이블에서 case_id 컬럼이 있으면 우선 사용
        if "case_id" in item.funcargs:
            case_id = item.funcargs.get("case_id")
            if case_id:
                print(f"[TestRail] Examples 테이블에서 case_id 추출: {case_id}")

        # 2. BDD 시나리오의 태그에서 직접 추출 (pytest-bdd)
        # pytest-bdd는 feature 파일의 태그(@C12345)를 pytest 마커로 변환
        if case_id is None:
            # item.iter_markers()를 사용하여 모든 마커 확인
            for marker in item.iter_markers():
                marker_name = marker.name
                # @C12345 형식의 태그 찾기 (C로 시작하고 뒤에 숫자만 있는 경우)
                if marker_name.startswith("C") and len(marker_name) > 1 and marker_name[1:].isdigit():
                    case_id = marker_name
                    print(f"[TestRail] 태그에서 case_id 추출: {case_id}")
                    break

        # 3. item.nodeid에서도 확인 (백업 방법)
        # pytest-bdd는 때때로 nodeid에 태그를 포함시킬 수 있음
        if case_id is None:
            nodeid = item.nodeid
            # nodeid에서 [C12345] 형식 찾기
            match = re.search(r'\[C(\d+)\]', nodeid)
            if match:
                case_id = f"C{match.group(1)}"
                print(f"[TestRail] nodeid에서 case_id 추출: {case_id}")

        # case_id를 찾지 못했거나 testrail_run_id가 없으면 기록하지 않음
        if case_id is None:
            print(f"[TestRail] case_id를 찾을 수 없음. nodeid: {item.nodeid}")
            return

        if testrail_run_id is None:
            print("[TestRail] testrail_run_id가 없습니다. 기록 생략")
            return

        # Cxxxx → 숫자만 추출
        if isinstance(case_id, str) and case_id.startswith("C"):
            case_id = case_id[1:]
        case_id = int(case_id)  # API는 int만 허용

        screenshot_path = None
        if result.when == "call":  # 실행 단계만 기록
            if result.failed:
                status_id = 5  # Failed
                comment = f"테스트 실패: {result.longrepr}"

                # 스크린샷 시도
                try:
                    page = None
                    
                    # 1. 저장된 browser_session에서 가져오기 (가장 안정적, feature 파일별로 분리)
                    feature_file = item.nodeid.split("::")[0]
                    if feature_file in active_browser_sessions:
                        feature_sessions = active_browser_sessions[feature_file]
                        # 정확한 nodeid로 먼저 찾기
                        if item.nodeid in feature_sessions:
                            browser_session = feature_sessions[item.nodeid]
                            if browser_session and hasattr(browser_session, 'page'):
                                page = browser_session.page
                                print(f"[DEBUG] browser_session에서 page 가져옴 (정확한 nodeid)")
                        else:
                            # 정확한 nodeid가 없으면 같은 feature 파일의 첫 번째 session 사용
                            if feature_sessions:
                                browser_session = list(feature_sessions.values())[0]
                                if browser_session and hasattr(browser_session, 'page'):
                                    page = browser_session.page
                                    print(f"[DEBUG] browser_session에서 page 가져옴 (같은 feature 파일의 첫 번째 session)")
                    
                    # 2. item.funcargs에서 직접 가져오기 시도
                    if not page and hasattr(item, 'funcargs') and item.funcargs:
                        if "browser_session" in item.funcargs:
                            browser_session = item.funcargs.get("browser_session")
                            if browser_session and hasattr(browser_session, 'page'):
                                page = browser_session.page
                                print(f"[DEBUG] funcargs에서 browser_session.page 가져옴")
                        if not page and "page" in item.funcargs:
                            page = item.funcargs.get("page")
                            print(f"[DEBUG] funcargs에서 page 가져옴")
                    
                    # 3. item._request를 통해 fixture 가져오기 시도
                    if not page and hasattr(item, '_request'):
                        try:
                            if "browser_session" in item._request.fixturenames:
                                browser_session = item._request.getfixturevalue("browser_session")
                                if browser_session and hasattr(browser_session, 'page'):
                                    page = browser_session.page
                                    print(f"[DEBUG] _request에서 browser_session.page 가져옴")
                        except Exception as e:
                            print(f"[DEBUG] browser_session fixture 가져오기 실패: {e}")
                        
                        if not page:
                            try:
                                if "page" in item._request.fixturenames:
                                    page = item._request.getfixturevalue("page")
                                    print(f"[DEBUG] _request에서 page 가져옴")
                            except Exception as e:
                                print(f"[DEBUG] page fixture 가져오기 실패: {e}")
                    
                    # 4. context에서 활성 페이지 찾기 시도
                    if not page and hasattr(item, '_request'):
                        try:
                            if "context" in item._request.fixturenames:
                                context = item._request.getfixturevalue("context")
                                if context and context.pages:
                                    # 가장 최근에 열린 페이지 사용
                                    page = context.pages[-1]
                                    print(f"[DEBUG] context에서 page 가져옴")
                        except Exception as e:
                            print(f"[DEBUG] context에서 page 찾기 실패: {e}")
                    
                    if page and not page.is_closed():
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        screenshot_path = f"screenshots/{case_id}_{timestamp}.png"
                        os.makedirs(os.path.dirname(screenshot_path), exist_ok=True)
                        page.screenshot(path=screenshot_path, timeout=2000)
                        print(f"[TestRail] 스크린샷 저장 완료: {screenshot_path}")
                    else:
                        print(f"[WARNING] 스크린샷 실패: page 객체를 찾을 수 없음")
                        print(f"[DEBUG] active_browser_sessions feature 파일: {list(active_browser_sessions.keys())}")
                        if feature_file in active_browser_sessions:
                            print(f"[DEBUG] {feature_file}의 nodeid: {list(active_browser_sessions[feature_file].keys())}")
                        print(f"[DEBUG] funcargs 키: {list(item.funcargs.keys()) if hasattr(item, 'funcargs') and item.funcargs else 'N/A'}")
                        print(f"[DEBUG] fixturenames: {list(item._request.fixturenames) if hasattr(item, '_request') else 'N/A'}")
                except Exception as e:
                    print(f"[WARNING] 스크린샷 실패: {e}")
                    import traceback
                    print(f"[DEBUG] 스크린샷 실패 상세: {traceback.format_exc()}")

            elif result.skipped:
                status_id = 2  # Blocked
                comment = "테스트 스킵"
            else:
                status_id = 1  # Passed
                comment = "테스트 성공"

            # 실행 시간 기록
            duration_sec = getattr(result, "duration", 0)
            if duration_sec and duration_sec > 0.1:
                elapsed = f"{duration_sec:.1f}s"
            else:
                elapsed = None

            # 수집된 로그 추가
            # pytest_runtest_logreport에서 수집한 로그 또는 직접 핸들러에서 가져오기
            # pass/fail/skip 모든 경우에 로그 포함
            log_content = None
            
            # 1. test_logs에서 먼저 확인 (pytest_runtest_logreport에서 수집된 경우)
            if item.nodeid in test_logs:
                log_content = test_logs[item.nodeid]
                # 사용 후 삭제 (메모리 절약)
                del test_logs[item.nodeid]
            else:
                # 2. nodeid 부분 매칭 시도 (pytest-bdd는 nodeid 형식이 다를 수 있음)
                for stored_nodeid, stored_logs in list(test_logs.items()):
                    if item.nodeid in stored_nodeid or stored_nodeid in item.nodeid:
                        log_content = stored_logs
                        # 매칭된 항목도 삭제
                        del test_logs[stored_nodeid]
                        break
                
                # 3. 여전히 없으면 직접 핸들러에서 가져오기 (실행 순서 문제 대비)
                if not log_content:
                    logs = test_log_handler.get_logs()
                    if logs and logs.strip():
                        log_content = logs
                        print(f"[DEBUG] 테스트 {item.nodeid} 로그를 핸들러에서 직접 가져옴")
            
            if log_content and log_content.strip():  # 로그가 있고 비어있지 않은 경우만 추가
                comment += f"\n\n--- 실행 로그 ---\n{log_content}"
                print(f"[DEBUG] 테스트 {item.nodeid} 로그 추가 완료")
            else:
                # 로그가 없는 경우에도 디버깅 정보 출력
                print(f"[DEBUG] 테스트 {item.nodeid}의 로그가 없음. test_logs 키: {list(test_logs.keys())}")

            # TestRail 기록
            payload = {
                "status_id": status_id,
                "comment": comment,
            }
            if elapsed:
                payload["elapsed"] = elapsed

            result_id = None
            try:
                result_obj = testrail_post(
                    f"add_result_for_case/{testrail_run_id}/{case_id}", payload
                )
                result_id = result_obj.get("id")
            except Exception as e:
                print(f"[WARNING] TestRail 기록 실패: {e}")

            # 스크린샷 첨부
            if screenshot_path and result_id:
                try:
                    with open(screenshot_path, "rb") as f:
                        testrail_post(
                            f"add_attachment_to_result/{result_id}",
                            files={"attachment": f},
                        )
                except Exception as e:
                    print(f"[WARNING] TestRail 스크린샷 업로드 실패: {e}")

            print(f"[TestRail] case_id {case_id} 결과 기록 완료 (status_id: {status_id})")

    except Exception as e:
        # 어떤 이유로든 pytest 자체 중단 방지
        print(f"[ERROR] pytest_runtest_makereport 처리 중 예외 발생 (무시됨): {e}")

@pytest.hookimpl(trylast=True)
def pytest_sessionfinish(session, exitstatus):
    """
    전체 테스트 종료 후 Run 닫기
    """
    global testrail_run_id
    if testrail_run_id:
        testrail_post(f"close_run/{testrail_run_id}", {})
        print(f"[TestRail] Run {testrail_run_id} 종료 완료")

    screenshots_dir = "screenshots"
    if os.path.exists(screenshots_dir):
        shutil.rmtree(screenshots_dir)  # 폴더 통째로 삭제
        print(f"[CLEANUP] '{screenshots_dir}' 폴더 삭제 완료")
