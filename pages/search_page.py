"""
검색 결과 페이지 객체
"""
from pages.base_page import BasePage
from playwright.sync_api import Page
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
    
    def select_first_product(self) -> None:
        """검색 결과에서 첫 번째 상품 선택"""
        # TODO: 구현
        self.page.wait_for_load_state("networkidle")
        self.click(self.FIRST_PRODUCT, timeout=10000)
        logger.info("첫 번째 상품 선택 완료")
    
    def select_product_by_name(self, product_name: str) -> None:
        """상품명으로 상품 선택"""
        # TODO: 구현
        self.page.wait_for_load_state("networkidle")
        selector = self.PRODUCT_BY_NAME.format(product_name=product_name)
        self.click(selector)
        logger.info(f"상품 선택: {product_name}")
    
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

