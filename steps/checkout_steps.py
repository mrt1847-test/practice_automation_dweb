"""
주문/결제 관련 Step Definitions
주문 / 결제
"""
from pytest_bdd import given, when, then, parsers
from pages.cart_page import CartPage
from pages.product_page import ProductPage
from pages.checkout_page import CheckoutPage
from pages.search_page import SearchPage
from pages.home_page import HomePage
import logging

logger = logging.getLogger(__name__)


@when("사용자가 구매하기 버튼을 클릭한다")
def user_clicks_purchase_button(page):
    """
    사용자가 구매하기 버튼 클릭 (POM 패턴 사용)
    시나리오 태그(@C12345)로 TestRail에 자동 기록됨
    """
    cart_page = CartPage(page)
    cart_page.wait_for_page_load()
    cart_page.click_purchase_button()
    logger.info("구매하기 버튼 클릭 완료")


@when("사용자가 바로구매 버튼을 클릭한다")
def user_clicks_buy_now_button(page):
    """사용자가 바로구매 버튼 클릭"""
    product_page = ProductPage(page)
    product_page.wait_for_page_load()
    product_page.click_buy_now_button()
    logger.info("바로구매 버튼 클릭 완료")


@when("사용자가 장바구니에서 선택된 상품을 주문한다")
def user_orders_selected_items_from_cart(page):
    """사용자가 장바구니에서 선택된 상품 주문"""
    # TODO: 장바구니에서 선택 주문 로직 구현
    logger.info("장바구니에서 선택 주문")


@when("사용자가 장바구니에서 전체 상품을 주문한다")
def user_orders_all_items_from_cart(page):
    """사용자가 장바구니의 모든 상품 주문"""
    # TODO: 장바구니 전체 주문 로직 구현
    logger.info("장바구니 전체 주문")


@then("구매 페이지가 표시된다")
def purchase_page_is_displayed(page):
    """구매/주문 페이지가 표시되는지 확인 (증명)"""
    checkout_page = CheckoutPage(page)
    page.wait_for_load_state("networkidle")
    assert checkout_page.is_checkout_page_displayed(), "구매 페이지가 표시되지 않았습니다"
    logger.info("구매 페이지 표시 확인")


@given("구매 페이지가 표시된다")
def purchase_page_is_displayed_given(page):
    """구매 페이지 상태 보장 (확인 + 필요시 생성)"""
    checkout_page = CheckoutPage(page)
    page.wait_for_load_state("networkidle")
    
    # 상태 확인
    if checkout_page.is_checkout_page_displayed():
        logger.info("이미 구매 페이지에 있음")
        return
    
    # 상태가 아니면 강제로 생성
    logger.info("구매 페이지가 아님. 구매하기 버튼 클릭 수행")
    
    # 장바구니에 상품이 있는지 확인
    cart_page = CartPage(page)
    if not cart_page.has_products():
        # 장바구니가 비어있으면 상품 추가부터 수행
        logger.info("장바구니가 비어있음. 상품 추가 수행")
        product_page = ProductPage(page)
        if not product_page.is_product_detail_displayed():
            # 상품 상세 페이지도 없으면 상품 선택부터 수행
            logger.info("상품 상세 페이지가 아님. 상품 선택 수행")
            search_page = SearchPage(page)
            if not search_page.is_search_results_displayed():
                # 검색 결과 페이지도 아니면 검색부터 수행
                logger.info("검색 결과 페이지도 아님. 검색 수행")
                home_page = HomePage(page)
                home_page.fill_search_input("노트북")
                home_page.click_search_button()
                home_page.wait_for_search_results()
            # 상품 선택 (Atomic POM 조합)
            search_page.wait_for_search_results_load()
            search_page.click_first_product()
        # 장바구니에 추가 (Atomic POM 조합)
        product_page.wait_for_page_load()
        product_page.click_add_to_cart_button()
    
    # 구매하기 버튼 클릭 (POM 패턴 사용)
    cart_page = CartPage(page)
    cart_page.wait_for_page_load()
    cart_page.click_purchase_button()
    
    # 생성 후 확인
    page.wait_for_load_state("networkidle")
    assert checkout_page.is_checkout_page_displayed(), "구매 페이지 생성 실패"
    logger.info("구매 페이지 상태 보장 완료")


@when("사용자가 배송지 정보를 입력한다")
def user_enters_shipping_info(page):
    """사용자가 배송지 정보 입력"""
    # TODO: 배송지 정보 입력 로직 구현
    logger.info("배송지 정보 입력")


@when("사용자가 기존 배송지를 선택한다")
def user_selects_existing_shipping_address(page):
    """사용자가 저장된 배송지 선택"""
    # TODO: 기존 배송지 선택 로직 구현
    logger.info("기존 배송지 선택")


@when(parsers.parse('사용자가 "{address_name}" 배송지를 선택한다'))
def user_selects_specific_shipping_address(page, address_name):
    """사용자가 특정 배송지 선택"""
    # TODO: 특정 배송지 선택 로직 구현
    logger.info(f"배송지 선택: {address_name}")


@when("사용자가 결제 방법을 선택한다")
def user_selects_payment_method(page):
    """사용자가 결제 방법 선택"""
    # TODO: 결제 방법 선택 로직 구현
    logger.info("결제 방법 선택")


@when(parsers.parse('사용자가 "{payment_method}"로 결제한다'))
def user_pays_with_method(page, payment_method):
    """사용자가 특정 결제 방법으로 결제"""
    checkout_page = CheckoutPage(page)
    page.wait_for_load_state("networkidle")
    
    # 스마일페이 선택
    if payment_method == "스마일페이":
        checkout_page.select_payment_method("스마일페이")
    # 일반결제 하위 결제 방법 선택 (신용/체크카드, 해외발급 신용카드, 무통장 입금, 휴대폰 소액결제)
    elif payment_method in ["신용/체크카드", "해외발급 신용카드", "무통장 입금", "휴대폰 소액결제"]:
        # 먼저 일반결제 선택
        checkout_page.select_payment_method("일반결제")
        # 그 다음 하위 결제 방법 선택
        checkout_page.select_normal_payment_method(payment_method)
    
    logger.info(f"결제 방법 선택: {payment_method}")


@when("사용자가 주문을 완료한다")
def user_completes_order(page):
    """사용자가 주문 완료 버튼 클릭"""
    checkout_page = CheckoutPage(page)
    page.wait_for_load_state("networkidle")
    checkout_page.click_order_button()
    logger.info("주문 완료")


@then("주문이 완료되었다")
def order_is_completed(page):
    """주문이 성공적으로 완료되었는지 확인"""
    page.wait_for_load_state("networkidle")
    # TODO: 주문 완료 페이지 확인 로직 구현
    logger.info("주문 완료 확인")
