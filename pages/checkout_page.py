"""
주문서서 페이지 객체
"""
from pages.base_page import BasePage
from playwright.sync_api import Page
from typing import Optional
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

    def select_payment_method(self, payment_type: str, timeout: Optional[int] = None) -> None:
        """결제 유형 선택
        
        Args:
            payment_type: 선택할 결제 유형 (텍스트)
                - 스마일페이
                - 일반결제
            timeout: 타임아웃 (기본값: self.timeout)
        """
        timeout = timeout or self.timeout
        logger.debug(f"결제 유형 선택: {payment_type}")
        
        # 요소 찾기
        element = self.get_by_text(payment_type)
        
        # 요소가 나타날 때까지 대기
        element.wait_for(state="attached", timeout=timeout)
        logger.debug(f"결제 유형 요소 발견: {payment_type}")
        
        # 요소가 화면에 보이도록 스크롤
        element.scroll_into_view_if_needed(timeout=timeout)
        logger.debug(f"결제 유형 요소 스크롤 완료: {payment_type}")
        
        # 요소가 보일 때까지 대기
        element.wait_for(state="visible", timeout=timeout)
        logger.debug(f"결제 유형 요소 표시 확인: {payment_type}")
        
        # 클릭
        element.click(timeout=timeout)
        logger.info(f"결제 유형 선택 완료: {payment_type}")
    
    def select_normal_payment_method(self, payment_method: str, timeout: Optional[int] = None) -> None:
        """결제 방법 선택
        
        Args:
            payment_method: 선택할 결제 방법 (텍스트)
                - 신용/체크카드
                - 해외발급 신용카드
                - 무통장 입금
                - 휴대폰 소액결제
            timeout: 타임아웃 (기본값: self.timeout)
        """
        timeout = timeout or self.timeout
        logger.debug(f"결제 방법 선택: {payment_method}")
        
        # 요소 찾기
        element = self.get_by_text(payment_method)
        
        # 요소가 나타날 때까지 대기
        element.wait_for(state="attached", timeout=timeout)
        logger.debug(f"결제 방법 요소 발견: {payment_method}")
        
        # 요소가 화면에 보이도록 스크롤
        element.scroll_into_view_if_needed(timeout=timeout)
        logger.debug(f"결제 방법 요소 스크롤 완료: {payment_method}")
        
        # 요소가 보일 때까지 대기
        element.wait_for(state="visible", timeout=timeout)
        logger.debug(f"결제 방법 요소 표시 확인: {payment_method}")
        
        # 클릭
        element.click(timeout=timeout)
        logger.info(f"결제 방법 선택 완료: {payment_method}")
    
    def select_bank_type(self, bank_type: str, timeout: Optional[int] = None) -> None:
        """은행 종류 선택
        
        Args:
            bank_type: 선택할 은행 종류 (텍스트)
            timeout: 타임아웃 (기본값: self.timeout)
        """
        timeout = timeout or self.timeout
        logger.debug(f"은행 종류 선택: {bank_type}")
        
        # 요소 찾기
        element = self.get_by_text(bank_type)
        
        # 요소가 나타날 때까지 대기
        element.wait_for(state="attached", timeout=timeout)
        logger.debug(f"은행 종류 요소 발견: {bank_type}")
        
        # 요소가 화면에 보이도록 스크롤
        element.scroll_into_view_if_needed(timeout=timeout)
        logger.debug(f"은행 종류 요소 스크롤 완료: {bank_type}")
        
        # 요소가 보일 때까지 대기
        element.wait_for(state="visible", timeout=timeout)
        logger.debug(f"은행 종류 요소 표시 확인: {bank_type}")
        
        # 클릭
        element.click(timeout=timeout)
        logger.info(f"은행 종류 선택 완료: {bank_type}")

    def click_order_button(self, timeout: Optional[int] = None) -> None:
        """
        결제하기 버튼 클릭
        
        Args:
            timeout: 타임아웃 (기본값: self.timeout)
        """
        timeout = timeout or self.timeout
        logger.debug("결제하기 버튼 클릭")
        
        # 요소 찾기
        element = self.get_by_text("결제하기")
        
        # 요소가 나타날 때까지 대기
        element.wait_for(state="attached", timeout=timeout)
        logger.debug("결제하기 버튼 발견")
        
        # 요소가 화면에 보이도록 스크롤
        element.scroll_into_view_if_needed(timeout=timeout)
        logger.debug("결제하기 버튼 스크롤 완료")
        
        # 요소가 보일 때까지 대기
        element.wait_for(state="visible", timeout=timeout)
        logger.debug("결제하기 버튼 표시 확인")
        
        # 클릭
        element.click(timeout=timeout)
        logger.info("결제하기 버튼 클릭 완료")
    