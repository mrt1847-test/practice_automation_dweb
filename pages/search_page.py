"""
검색 결과 페이지 객체
"""
from pages.base_page import BasePage
from playwright.sync_api import Page, Locator, expect
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class SearchPage(BasePage):
    """검색 결과 페이지"""
    
    # 선택자 정의 (TODO: 실제 선택자로 교체)
    FIRST_PRODUCT = "a.item:first-child"
    PRODUCT_BY_NAME = "a.item:has-text('{product_name}')"
    FILTER_BUTTON = ""  # TODO: 필터 버튼 선택자
    SORT_DROPDOWN = ""  # TODO: 정렬 드롭다운 선택자
    
    def __init__(self, page: Page):
        """
        SearchPage 초기화
        
        Args:
            page: Playwright Page 객체
        """
        super().__init__(page)
    
    def wait_for_search_results_load(self) -> None:
        """검색 결과 페이지 로드 대기"""
        logger.debug("검색 결과 페이지 로드 대기")
        self.page.wait_for_load_state("networkidle")
    
    def click_first_product(self, timeout: int = 10000) -> None:
        """
        첫 번째 상품 클릭
        
        Args:
            timeout: 타임아웃 (기본값: 10000ms)
        """
        logger.debug("첫 번째 상품 클릭")
        self.click(self.FIRST_PRODUCT, timeout=timeout)
    
    def click_product_by_name(self, product_name: str) -> None:
        """
        상품명으로 상품 클릭
        
        Args:
            product_name: 상품명
        """
        logger.debug(f"상품 클릭: {product_name}")
        selector = self.PRODUCT_BY_NAME.format(product_name=product_name)
        self.click(selector)
    
    def is_search_results_displayed(self) -> bool:
        """검색 결과 페이지가 표시되었는지 확인"""
        # TODO: 구현
        self.page.wait_for_load_state("networkidle")
        return "search" in self.page.url.lower()
    
    def contains_keyword(self, keyword: str) -> bool:
        """검색 결과에 키워드 관련 상품이 포함되어 있는지 확인"""
        # TODO: 구현
        self.page.wait_for_load_state("networkidle")
        page_content = self.page.content()
        return len(page_content) > 0
    
    def apply_filter(self) -> None:
        """검색 필터 적용"""
        # TODO: 구현
        logger.info("검색 필터 적용")
    
    def select_sort_option(self) -> None:
        """정렬 기준 선택"""
        # TODO: 구현
        logger.info("정렬 기준 선택")
    
    # ============================================
    # 모듈 및 상품 관련 메서드 (Atomic POM)
    # ============================================
    
    def get_module_by_title(self, module_title: str) -> Locator:
        """
        모듈 타이틀로 모듈 요소 찾기
        
        Args:
            module_title: 모듈 타이틀 텍스트
            
        Returns:
            Locator 객체
        """
        logger.debug(f"모듈 찾기: {module_title}")
        return self.page.get_by_text(module_title, exact=True)
    
    def scroll_module_into_view(self, module_locator: Locator) -> None:
        """
        모듈을 뷰포트로 스크롤
        
        Args:
            module_locator: 모듈 Locator 객체
        """
        logger.debug("모듈 스크롤")
        module_locator.scroll_into_view_if_needed()
    
    def get_module_parent(self, module_locator: Locator) -> Locator:
        """
        모듈의 부모 요소 찾기
        
        Args:
            module_locator: 모듈 Locator 객체
            
        Returns:
            부모 Locator 객체
        """
        logger.debug("모듈 부모 요소 찾기")
        return module_locator.locator("xpath=../..")
    
    def get_product_in_module(self, parent_locator: Locator) -> Locator:
        """
        모듈 내 상품 요소 찾기
        
        Args:
            parent_locator: 모듈 부모 Locator 객체
            
        Returns:
            상품 Locator 객체
        """
        logger.debug("모듈 내 상품 요소 찾기")
        return parent_locator.locator("div.box__item-container > div.box__image > a")
    
    def scroll_product_into_view(self, product_locator: Locator) -> None:
        """
        상품 요소를 뷰포트로 스크롤
        
        Args:
            product_locator: 상품 Locator 객체
        """
        logger.debug("상품 요소 스크롤")
        product_locator.scroll_into_view_if_needed()
    
    def assert_product_visible(self, product_locator: Locator) -> None:
        """
        상품이 보이는지 확인 (Assert)
        
        Args:
            product_locator: 상품 Locator 객체
        """
        logger.debug("상품 가시성 확인")
        expect(product_locator).to_be_visible()
    
    def get_product_code(self, product_locator: Locator) -> Optional[str]:
        """
        상품 코드 가져오기
        
        Args:
            product_locator: 상품 Locator 객체
            
        Returns:
            상품 코드 (data-montelena-goodscode 속성 값)
        """
        logger.debug("상품 코드 가져오기")
        return product_locator.get_attribute("data-montelena-goodscode")
    
    def get_product_by_code(self, goodscode: str) -> Locator:
        """
        상품 번호로 상품 요소 찾기
        
        Args:
            goodscode: 상품 번호
            
        Returns:
            상품 Locator 객체
        """
        logger.debug(f"상품 번호로 상품 찾기: {goodscode}")
        return self.page.locator(f'a[data-montelena-goodscode="{goodscode}"]').nth(0)
    
    def wait_for_new_page(self):
        """
        새 페이지가 열릴 때까지 대기하는 컨텍스트 매니저
        
        Returns:
            새 페이지 정보를 담은 컨텍스트 매니저
        """
        logger.debug("새 페이지 대기")
        return self.page.context.expect_page()
    
    def click_product_and_wait_new_page(self, product_locator: Locator) -> Page:
        """
        상품 클릭하고 새 페이지 대기
        
        Args:
            product_locator: 상품 Locator 객체
            
        Returns:
            새 Page 객체
        """
        logger.debug("상품 클릭 및 새 페이지 대기")
        with self.page.context.expect_page() as new_page_info:
            product_locator.click()
        new_page = new_page_info.value
        new_page.wait_for_load_state("networkidle")
        return new_page
    
    def verify_product_code_in_url(self, url: str, goodscode: str) -> None:
        """
        URL에 상품 번호가 포함되어 있는지 확인 (Assert)
        
        Args:
            url: 확인할 URL
            goodscode: 상품 번호
        """
        logger.debug(f"URL에 상품 번호 포함 확인: {goodscode}")
        assert goodscode in url, f"상품 번호 {goodscode}가 URL에 포함되어야 합니다"

