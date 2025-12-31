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


def pytest_report_teststatus(report, config):
    # 이름에 'wait_'가 들어간 테스트는 리포트 출력에서 숨김
    if any(keyword in report.nodeid for keyword in ["wait_", "fetch"]):
        return report.outcome, None, ""
    return None


# JSON 파일이 들어 있는 폴더 지정
JSON_DIR = Path(__file__).parent / "json"  # json 폴더 내의 JSON 파일 전부 대상


def get_json_files():
    """폴더 내 모든 .json 파일 경로 리스트 반환"""
    return sorted(JSON_DIR.glob("*.json"))


def clear_json_cases(json_data):
    """
    JSON 데이터에서 최상위 키(case1, case2 등)는 유지하고,
    값은 모두 빈 dict로 초기화
    """
    cleared_list = []  # 초기화된 JSON 데이터를 담을 리스트

    for case_group in json_data:  # 각 JSON 객체 순회
        cleared_group = {}  # 초기화된 case 묶음
        for case_name in case_group.keys():  # case1, case2 등 키 순회
            cleared_group[case_name] = {}  # 내부 데이터 비우기
        cleared_list.append(cleared_group)  # 변환된 데이터 추가

    return cleared_list


@pytest.fixture(scope="session", autouse=True)
def clear_all_json_files():
    files = list(get_json_files())
    for f in files:
        print(" -", f)
    print(f"총 {len(files)}개 파일 발견")

    for file_path in files:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if not content:
                    # 빈 파일인 경우 빈 리스트로 초기화
                    data = []
                else:
                    data = json.loads(content)
        except json.JSONDecodeError:
            # JSON 파싱 실패 시 빈 리스트로 초기화
            data = []
        
        cleared = clear_json_cases(data)
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(cleared, f, ensure_ascii=False, indent=2)

    print(f"✅ JSON 초기화 완료: {len(files)}개 파일 처리됨")


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




@pytest.hookimpl(tryfirst=True)
def pytest_sessionstart(session):
    """
    테스트 실행 시작 시:
    1. section_id 기반으로 해당 섹션의 케이스 ID 가져오기
    2. 그 케이스들로 Run 생성
    """
    global testrail_run_id, case_id_map
    # 1. section_id 직접 사용
    if testrail_run_id is not None:
        print(f"[TestRail] 이미 Run(ID={testrail_run_id})이 존재합니다. 새 Run 생성 생략")
        return
    if not TESTRAIL_SECTION_ID:
        raise RuntimeError("[TestRail] TESTRAIL_SECTION_ID가 정의되지 않았습니다.")
    # 2. 섹션 내 케이스 가져오기
    cases = testrail_get(
        f"get_cases/{TESTRAIL_PROJECT_ID}&suite_id={TESTRAIL_SUITE_ID}&section_id={TESTRAIL_SECTION_ID}"
    )
    case_ids = [c["id"] for c in cases]
    case_id_map[TESTRAIL_SECTION_ID] = case_ids
    if not case_ids:
        raise RuntimeError(f"[TestRail] section_id '{TESTRAIL_SECTION_ID}'에 케이스가 없습니다.")
    # 3. Run 생성
    run_name = f"AD Regression test dweb {datetime.now():%Y-%m-%d %H:%M:%S}"
    payload = {
        "suite_id": TESTRAIL_SUITE_ID,
        "name": run_name,
        "include_all": False,
        "case_ids": case_ids,
        "milestone_id": TESTRAIL_MILESTONE_ID
    }
    run = testrail_post(f"add_run/{TESTRAIL_PROJECT_ID}", payload)
    testrail_run_id = run["id"]
    print(f"[TestRail] section_id '{TESTRAIL_SECTION_ID}' Run 생성 완료 (ID={testrail_run_id})")


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
                    page = item.funcargs.get("page")
                    if page and not page.is_closed():
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        screenshot_path = f"screenshots/{case_id}_{timestamp}.png"
                        os.makedirs(os.path.dirname(screenshot_path), exist_ok=True)
                        page.screenshot(path=screenshot_path, timeout=2000)
                except Exception as e:
                    print(f"[WARNING] 스크린샷 실패: {e}")

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

            # stdout 로그 추가
            stdout = getattr(item, "_stdout_capture", None)
            if stdout:
                comment += f"\n\n--- stdout 로그 ---\n{stdout.strip()}"

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
