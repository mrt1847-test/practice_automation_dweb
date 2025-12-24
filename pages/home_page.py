"""
G마켓 홈 페이지 객체
"""
from pages.base_page import BasePage
from playwright.sync_api import Page
import logging

logger = logging.getLogger(__name__)


class HomePage(BasePage):
    """G마켓 홈 페이지"""
    
    # 선택자 정의
    SEARCH_INPUT = "input[placeholder*='검색']"
    SEARCH_BUTTON = "button[type='submit']"
    LOGIN_BUTTON = "로그인"
    LOGOUT_BUTTON = "text=로그아웃"
    
    def __init__(self, page: Page):
        """
        HomePage 초기화
        
        Args:
            page: Playwright Page 객체
        """
        super().__init__(page)
        self.base_url = "https://www.gmarket.co.kr"
    
    def navigate(self) -> None:
        """홈 페이지로 이동"""
        logger.info("홈 페이지로 이동")
        self.goto(self.base_url)
    
    def fill_search_input(self, keyword: str) -> None:
        """
        검색어 입력
        
        Args:
            keyword: 검색할 상품명
        """
        logger.debug(f"검색어 입력: {keyword}")
        self.fill("#form__search-keyword", keyword)
    
    def click_search_button(self) -> None:
        """검색 버튼 클릭"""
        logger.debug("검색 버튼 클릭")
        self.click("button.button__search.general-clk-spm-d > img.image")
    
    def wait_for_search_results(self) -> None:
        """검색 결과 페이지 로드 대기"""
        logger.debug("검색 결과 로드 대기")
        self.page.wait_for_load_state("networkidle")
    
    def click_login(self) -> None:
        """로그인 버튼 클릭"""
        logger.info("로그인 버튼 클릭")
        self.get_by_text_and_click("로그인")
    
    def is_logged_in(self) -> bool:
        """
        로그인 상태 확인
        
        Returns:
            로그인되어 있으면 True, 아니면 False
        """
        return self.is_visible(self.LOGOUT_BUTTON, timeout=5000)
    
    def click_logout(self) -> None:
        """로그아웃 버튼 클릭"""
        logger.info("로그아웃 버튼 클릭")
        self.click(self.LOGOUT_BUTTON)

