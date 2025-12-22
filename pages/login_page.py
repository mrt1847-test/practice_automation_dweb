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
    USERNAME_INPUT = "#typeMemberInputId"
    PASSWORD_INPUT = "#typeMemberInputPassword"
    LOGIN_SUBMIT_BUTTON = "#btn_memberLogin"
    LOGOUT_BUTTON = "text=로그아웃"  # 로그인 성공 후 표시되는 요소
    
    def __init__(self, page: Page):
        """
        LoginPage 초기화
        
        Args:
            page: Playwright Page 객체
        """
        super().__init__(page)
    
    def login(self, username: str, password: str) -> None:
        """
        로그인 수행
        
        Args:
            username: 사용자 ID
            password: 비밀번호
        """
        logger.info(f"로그인 시도: {username}")
        self.fill(self.USERNAME_INPUT, username)
        self.fill(self.PASSWORD_INPUT, password)
        self.click(self.LOGIN_SUBMIT_BUTTON)
        
        # 로그인 완료 대기 (로그아웃 버튼이 나타날 때까지)
        self.wait_for_selector(self.LOGOUT_BUTTON, timeout=15000)
        logger.info("로그인 완료")
    
    def is_login_successful(self) -> bool:
        """
        로그인 성공 여부 확인
        
        Returns:
            로그인 성공하면 True, 아니면 False
        """
        return self.is_visible(self.LOGOUT_BUTTON, timeout=5000)

