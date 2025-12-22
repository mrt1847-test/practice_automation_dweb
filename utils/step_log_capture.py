"""
Step별 로그 캡처 유틸리티
각 step 실행 중 발생한 로그를 캡처하기 위한 헬퍼
"""
import logging
from io import StringIO
from contextlib import contextmanager


class StepLogCapture:
    """Step별 로그를 캡처하는 클래스"""
    
    def __init__(self):
        self.log_stream = StringIO()
        self.handler = None
        self.original_handlers = []
    
    def start(self):
        """로그 캡처 시작"""
        # StringIO 핸들러 생성
        self.handler = logging.StreamHandler(self.log_stream)
        self.handler.setLevel(logging.DEBUG)
        
        # 포맷터 설정
        formatter = logging.Formatter('%(asctime)s [%(levelname)-8s] %(name)s: %(message)s')
        self.handler.setFormatter(formatter)
        
        # 루트 로거에 핸들러 추가
        root_logger = logging.getLogger()
        self.original_handlers = root_logger.handlers[:]  # 원본 핸들러 백업
        root_logger.addHandler(self.handler)
        root_logger.setLevel(logging.DEBUG)
    
    def stop(self):
        """로그 캡처 중지"""
        if self.handler:
            root_logger = logging.getLogger()
            root_logger.removeHandler(self.handler)
            # 원본 핸들러 복원
            root_logger.handlers = self.original_handlers
    
    def get_logs(self) -> str:
        """캡처한 로그 가져오기"""
        return self.log_stream.getvalue()
    
    def clear(self):
        """로그 버퍼 초기화"""
        self.log_stream.seek(0)
        self.log_stream.truncate(0)


@contextmanager
def capture_step_logs():
    """
    Step 실행 중 로그를 캡처하는 컨텍스트 매니저
    
    Usage:
        with capture_step_logs() as logs:
            # step 실행 코드
            pass
        logs_text = logs.get_logs()
    """
    capture = StepLogCapture()
    capture.start()
    try:
        yield capture
    finally:
        capture.stop()

