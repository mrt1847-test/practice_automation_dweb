"""
TestRail Step 기록 유틸리티
Step definition에서 TestRail에 결과를 기록하기 위한 함수
"""
import sys
import os
from datetime import datetime
from typing import Optional

# conftest의 전역 변수 접근을 위한 함수
def get_testrail_run_id():
    """conftest의 testrail_run_id 가져오기"""
    import conftest
    return conftest.testrail_run_id


def testrail_post(endpoint, payload=None, files=None):
    """conftest의 testrail_post 함수 사용"""
    import conftest
    return conftest.testrail_post(endpoint, payload, files)


def record_testrail_step(case_id_tag: str, step_name: str, status: str, error: str = None, 
                         page=None, duration_sec: float = None, logs: str = None):
    """
    TestRail에 step 단위 결과 기록 (스크린샷, 실행 시간, 로그 포함)
    
    Args:
        case_id_tag: TestRail case ID 태그 (예: "C12345" 또는 "C12345-1")
        step_name: Step 이름 또는 함수명
        status: "passed" 또는 "failed"
        error: 오류 메시지 (실패 시)
        page: Playwright Page 객체 (스크린샷용, 실패 시만 사용)
        duration_sec: 실행 시간 (초)
        logs: Step 실행 중 생성된 로그 문자열
    """
    testrail_run_id = get_testrail_run_id()
    if not testrail_run_id:
        return
    
    try:
        # C12345 또는 C12345-1 → 12345 추출
        # C12345-1 같은 경우 앞부분만 사용 (C12345)
        case_id_str = case_id_tag.split("-")[0]  # "C12345-1" → "C12345"
        if case_id_str.startswith("C"):
            case_id_num = int(case_id_str[1:])  # "C12345" → 12345
        else:
            # C가 없는 경우 숫자로 변환 시도
            case_id_num = int(case_id_str) if case_id_str.isdigit() else int(case_id_str)
        
        status_id = 1 if status == "passed" else 5
        comment = f"Step: {step_name}"
        if error:
            comment += f"\n오류: {error}"
        if logs:
            comment += f"\n\n--- 실행 로그 ---\n{logs}"
        
        # 실행 시간 기록 (있는 경우)
        elapsed = None
        if duration_sec and duration_sec > 0.1:
            elapsed = f"{duration_sec:.1f}s"
        
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
                f"add_result_for_case/{testrail_run_id}/{case_id_num}", payload
            )
            result_id = result_obj.get("id")
        except Exception as e:
            print(f"[WARNING] TestRail 기록 실패: {e}")
            return
        
        # 실패 시 스크린샷 첨부
        screenshot_path = None
        if status == "failed" and page:
            try:
                if not page.is_closed():
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    screenshot_path = f"screenshots/{case_id_num}_{timestamp}.png"
                    os.makedirs(os.path.dirname(screenshot_path), exist_ok=True)
                    page.screenshot(path=screenshot_path, timeout=2000)
            except Exception as e:
                print(f"[WARNING] 스크린샷 실패: {e}")
        
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
        
        print(f"[TestRail] Step '{step_name}' → case_id {case_id_num} 기록 완료 (status: {status})")
    except Exception as e:
        print(f"[WARNING] Step TestRail 기록 실패: {e}")

