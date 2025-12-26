"""
주문서서 페이지 객체
"""
from pages.base_page import BasePage
from playwright.sync_api import Page
import logging

logger = logging.getLogger(__name__)


class CheckoutPage(BasePage):
    """주문서 페이지"""
    
    # 선택자 정의
    
    def __init__(self, page: Page):
        """
        CheckoutPage 초기화
        
        Args:
            page: Playwright Page 객체
        """
        super().__init__(page)

    def is_checkout_page_displayed(self) -> bool:
        """주문서 페이지가 표시되었는지 확인"""
        return self.is_visible("h2.text__main-title")

    def select_payment_method(self, payment_type: str) -> None:
        """결제 유형 선택
        
        Args:
            payment_type: 선택할 결제 유형 (텍스트)
                - 스마일페이
                - 일반결제
        """
        self.get_by_text_and_click(payment_type)
    
    def select_normal_payment_method(self, payment_method: str) -> None:
        """결제 방법 선택
        
        Args:
            payment_method: 선택할 결제 방법 (텍스트)
                - 신용/체크카드
                - 해외발급 신용카드
                - 무통장 입금
                - 휴대폰 소액결제
        """
        self.get_by_text_and_click(payment_method)
    
    def select_bank_type(self, bank_type: str) -> None:
        """은행 종류 선택
        
        Args:
            bank_type: 선택할 은행 종류 (텍스트)
        """
        self.get_by_text_and_click(bank_type)
    