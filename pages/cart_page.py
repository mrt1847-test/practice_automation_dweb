"""
장바구니 페이지 객체
"""
from pages.base_page import BasePage
from playwright.sync_api import Page
from utils.urls import CART_URL
import logging

logger = logging.getLogger(__name__)


class CartPage(BasePage):
    """장바구니 페이지"""
    
    # 선택자 정의 (TODO: 실제 선택자로 교체)
    CART_ICON = '[title = "장바구니"]'
    CART_PREVIEW = ""  # TODO: 장바구니 미리보기 선택자
    PRODUCT_LIST = ".item_desc"  # TODO: 상품 목록 선택자
    PRODUCT_NAME = ""  # TODO: 상품명 선택자
    PRODUCT_QUANTITY = ""  # TODO: 상품 수량 선택자
    TOTAL_PRICE = ""  # TODO: 총 금액 선택자
    REMOVE_BUTTON = ""  # TODO: 제거 버튼 선택자
    CLEAR_CART_BUTTON = ""  # TODO: 장바구니 비우기 버튼 선택자
    PURCHASE_BUTTON = "button:has-text('구매하기')"  # 구매하기 버튼
    
    def __init__(self, page: Page):
        """
        CartPage 초기화
        
        Args:
            page: Playwright Page 객체
        """
        super().__init__(page)
        self.cart_url = CART_URL
    
    def navigate(self) -> None:
        """장바구니 페이지로 이동"""
        logger.info("장바구니 페이지로 이동")
        self.goto(self.cart_url)
    
    def click_cart_icon(self) -> None:
        """장바구니 아이콘 클릭"""
        self.click(self.CART_ICON)
        logger.info("장바구니 아이콘 클릭")
    
    def wait_for_cart_page_load(self) -> None:
        """장바구니 페이지 로드 대기"""
        logger.debug("장바구니 페이지 로드 대기")
        self.page.wait_for_load_state("networkidle")
    
    def is_cart_page_displayed(self) -> bool:
        """장바구니 페이지가 표시되었는지 확인"""
        # TODO: 구현
        return True
    
    def is_cart_preview_displayed(self) -> bool:
        """장바구니 미리보기가 표시되었는지 확인"""
        # TODO: 구현
        return self.is_visible(self.CART_PREVIEW)
    
    def has_products(self) -> bool:
        """장바구니에 상품이 있는지 확인"""
        # TODO: 구현
        products = self.page.locator(self.PRODUCT_LIST).count()
        return products > 0
    
    def is_empty(self) -> bool:
        """장바구니가 비어있는지 확인"""
        # TODO: 구현
        return not self.has_products()
    
    def get_product_quantity(self, product_name: str) -> str:
        """특정 상품의 수량 가져오기"""
        # TODO: 구현
        return ""
    
    def contains_product_with_quantity(self, product_name: str, quantity: str) -> bool:
        """장바구니에 특정 상품이 특정 수량으로 담겨있는지 확인"""
        # TODO: 구현
        actual_quantity = self.get_product_quantity(product_name)
        return actual_quantity == quantity
    
    def is_total_price_displayed(self) -> bool:
        """장바구니 총 금액이 표시되었는지 확인"""
        # TODO: 구현
        return self.is_visible(self.TOTAL_PRICE)
    
    def change_product_quantity(self, product_name: str, quantity: str) -> None:
        """장바구니 내 상품 수량 변경"""

        self.page.get_by_text(product_name).locator("xpath=ancestor::dd").locator("input.item_qty_count").fill(quantity)

        # TODO: 구현
        logger.info(f"장바구니 상품 수량 변경: {product_name} → {quantity}개")
    
    def remove_product(self, product_name: str) -> None:
        """장바구니에서 특정 상품 제거"""
        # 상품명 텍스트로 시작해서 부모 dd 태그를 찾고, 그 안의 삭제 버튼 선택
        self.page.get_by_text(product_name).locator("xpath=ancestor::dd").locator("button.btn_del").click()

        logger.info(f"장바구니에서 상품 제거: {product_name}")
    
    def clear_cart(self) -> None:
        """장바구니 전체 비우기"""
        
        self.locator('label[for="item_all_select"]').click()
        self.click(".btn_del")
        
        logger.info("장바구니 비우기")
    
    def wait_for_page_load(self) -> None:
        """페이지 로드 대기"""
        logger.debug("페이지 로드 대기")
        self.page.wait_for_load_state("networkidle")
    
    def click_purchase_button(self, timeout: int = 10000) -> None:
        """
        구매하기 버튼 클릭
        
        Args:
            timeout: 타임아웃 (기본값: 10000ms)
        """
        logger.debug("구매하기 버튼 클릭")
        self.click(self.PURCHASE_BUTTON, timeout=timeout)

