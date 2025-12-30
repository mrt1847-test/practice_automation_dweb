"""
G마켓 로그인 페이지 객체
"""
from pages.base_page import BasePage
from playwright.sync_api import Page
import logging

logger = logging.getLogger(__name__)


class LoginPage(BasePage):
    """G마켓 로그인 페이지"""
    
    # 선택자 정의
    
    def __init__(self, page: Page):
        """
        LoginPage 초기화
        
        Args:
            page: Playwright Page 객체
        """
        super().__init__(page)
    
    def fill_username(self, username: str) -> None:
        """
        사용자명 입력
        
        Args:
            username: 사용자 ID
        """
        logger.debug(f"사용자명 입력: {username}")
        self.fill("#typeMemberInputId", username)
    
    def fill_password(self, password: str) -> None:
        """
        비밀번호 입력
        
        Args:
            password: 비밀번호
        """
        logger.debug("비밀번호 입력")
        self.fill("#typeMemberInputPassword", password)
    
    def click_login_button(self) -> None:
        """로그인 버튼 클릭"""
        logger.debug("로그인 버튼 클릭")
        self.click("#btn_memberLogin")
    
    def wait_for_login_complete(self, timeout: int = 15000) -> None:
        """
        로그인 완료 대기
        
        Args:
            timeout: 타임아웃 (기본값: 15000ms)
        """
        logger.debug("로그인 완료 대기")
        self.wait_for_selector("text='로그아웃'", timeout=timeout)
    
    def is_login_successful(self) -> bool:
        """
        로그인 성공 여부 확인
        
        Returns:
            로그인 성공하면 True, 아니면 False
        """
        return self.is_visible("text='로그아웃'", timeout=5000)

