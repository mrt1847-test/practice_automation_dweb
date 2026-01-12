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
import time

logger = logging.getLogger(__name__)


@when("사용자가 장바구니 구매하기 버튼을 클릭한다")
def user_clicks_purchase_button(browser_session):
    """
    사용자가 구매하기 버튼 클릭 (POM 패턴 사용)
    
    Args:
        browser_session: BrowserSession 객체 (page 참조 관리)
    """
    cart_page = CartPage(browser_session.page)
    cart_page.wait_for_page_load()
    cart_page.click_purchase_button()
    logger.info("구매하기 버튼 클릭 완료")


@when("사용자가 바로구매 버튼을 클릭한다")
def user_clicks_buy_now_button(browser_session):
    """
    사용자가 바로구매 버튼 클릭
    
    Args:
        browser_session: BrowserSession 객체 (page 참조 관리)
    """
    product_page = ProductPage(browser_session.page)
    product_page.wait_for_page_load()
    product_page.click_buy_now_button()
    logger.info("바로구매 버튼 클릭 완료")


@when("사용자가 장바구니에서 선택된 상품을 주문한다")
def user_orders_selected_items_from_cart(browser_session):
    """
    사용자가 장바구니에서 선택된 상품 주문
    
    Args:
        browser_session: BrowserSession 객체 (page 참조 관리)
    """
    # TODO: 장바구니에서 선택 주문 로직 구현
    logger.info("장바구니에서 선택 주문")


@when("사용자가 장바구니에서 전체 상품을 주문한다")
def user_orders_all_items_from_cart(browser_session):
    """
    사용자가 장바구니의 모든 상품 주문
    
    Args:
        browser_session: BrowserSession 객체 (page 참조 관리)
    """
    # TODO: 장바구니 전체 주문 로직 구현
    logger.info("장바구니 전체 주문")


@then("구매 페이지가 표시된다")
def purchase_page_is_displayed(browser_session):
    """
    구매/주문 페이지가 표시되는지 확인 (증명)
    
    Args:
        browser_session: BrowserSession 객체 (page 참조 관리)
    """
    checkout_page = CheckoutPage(browser_session.page)
    browser_session.page.wait_for_load_state("networkidle")
    assert checkout_page.is_checkout_page_displayed(), "구매 페이지가 표시되지 않았습니다"
    logger.info("구매 페이지 표시 확인")


@given("구매 페이지가 표시된다")
def purchase_page_is_displayed_given(browser_session):
    """
    구매 페이지 상태 보장 (확인 + 필요시 생성)
    
    Args:
        browser_session: BrowserSession 객체 (page 참조 관리)
    """
    checkout_page = CheckoutPage(browser_session.page)
    browser_session.page.wait_for_load_state("networkidle")
    
    # 상태 확인
    if checkout_page.is_checkout_page_displayed():
        logger.info("이미 구매 페이지에 있음")
        return
    
    # 상태가 아니면 강제로 생성
    logger.info("구매 페이지가 아님. 구매하기 버튼 클릭 수행")
    
    # 장바구니에 상품이 있는지 확인
    cart_page = CartPage(browser_session.page)
    if not cart_page.has_products():
        # 장바구니가 비어있으면 상품 추가부터 수행
        logger.info("장바구니가 비어있음. 상품 추가 수행")
        product_page = ProductPage(browser_session.page)
        if not product_page.is_product_detail_displayed():
            # 상품 상세 페이지도 없으면 상품 선택부터 수행
            logger.info("상품 상세 페이지가 아님. 상품 선택 수행")
            search_page = SearchPage(browser_session.page)
            if not search_page.is_search_results_displayed():
                # 검색 결과 페이지도 아니면 검색부터 수행
                logger.info("검색 결과 페이지도 아님. 검색 수행")
                home_page = HomePage(browser_session.page)
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
    cart_page = CartPage(browser_session.page)
    cart_page.wait_for_page_load()
    cart_page.click_purchase_button()
    
    # 생성 후 확인
    browser_session.page.wait_for_load_state("networkidle")
    assert checkout_page.is_checkout_page_displayed(), "구매 페이지 생성 실패"
    logger.info("구매 페이지 상태 보장 완료")


@when("사용자가 배송지 정보를 입력한다")
def user_enters_shipping_info(browser_session):
    """
    사용자가 배송지 정보 입력
    
    Args:
        browser_session: BrowserSession 객체 (page 참조 관리)
    """
    # TODO: 배송지 정보 입력 로직 구현
    logger.info("배송지 정보 입력")


@when("사용자가 기존 배송지를 선택한다")
def user_selects_existing_shipping_address(browser_session):
    """
    사용자가 저장된 배송지 선택
    
    Args:
        browser_session: BrowserSession 객체 (page 참조 관리)
    """
    # TODO: 기존 배송지 선택 로직 구현
    logger.info("기존 배송지 선택")


@when(parsers.parse('사용자가 "{address_name}" 배송지를 선택한다'))
def user_selects_specific_shipping_address(browser_session, address_name):
    """
    사용자가 특정 배송지 선택
    
    Args:
        browser_session: BrowserSession 객체 (page 참조 관리)
        address_name: 배송지명
    """
    # TODO: 특정 배송지 선택 로직 구현
    logger.info(f"배송지 선택: {address_name}")


@when("사용자가 결제 방법을 선택한다")
def user_selects_payment_method(browser_session):
    """
    사용자가 결제 방법 선택
    
    Args:
        browser_session: BrowserSession 객체 (page 참조 관리)
    """
    # TODO: 결제 방법 선택 로직 구현
    logger.info("결제 방법 선택")


@when(parsers.parse('사용자가 "{payment_method}"의 "{payment_type}" 을 선택한다'))
def user_pays_with_method(browser_session, payment_method, payment_type):
    """
    사용자가 특정 결제 방법으로 결제
    
    Args:
        browser_session: BrowserSession 객체 (page 참조 관리)
        payment_method: 결제 방법
        pament_type: 결제 타입 (은행명 등)
    """
    checkout_page = CheckoutPage(browser_session.page)
    browser_session.page.wait_for_load_state("networkidle")
    
    # 스마일페이 선택
    if payment_method == "스마일페이":
        checkout_page.select_payment_method("스마일페이")
    # 일반결제 하위 결제 방법 선택 (신용/체크카드, 해외발급 신용카드, 무통장 입금, 휴대폰 소액결제)
    elif payment_method == "일반 결제":
        # 먼저 일반결제 선택
        checkout_page.select_payment_method("일반 결제")
        # 그 다음 하위 결제 방법 선택
        checkout_page.select_normal_payment_method(payment_type)

    
    logger.info(f"결제 방법 선택: {payment_method}")


@when("사용자가 주문을 완료한다")
def user_completes_order(browser_session):
    """
    사용자가 주문 완료 버튼 클릭
    
    Args:
        browser_session: BrowserSession 객체 (page 참조 관리)
    """
    checkout_page = CheckoutPage(browser_session.page)
    browser_session.page.wait_for_load_state("networkidle")
    checkout_page.click_order_button()
    logger.info("주문 완료")


@then("주문이 완료되었다")
def order_is_completed(browser_session):
    """
    주문이 성공적으로 완료되었는지 확인
    
    Args:
        browser_session: BrowserSession 객체 (page 참조 관리)
    """
    browser_session.page.wait_for_load_state("networkidle")
    # TODO: 주문 완료 페이지 확인 로직 구현
    logger.info("주문 완료 확인")


@given("주문서 페이지 진입상태")
def checkout_page_state(browser_session):
    """
    주문서 페이지 상태 보장 (확인 + 필요시 생성)
    
    Args:
        browser_session: BrowserSession 객체 (page 참조 관리)
    """
    # browser_session.page 사용 (새 탭이 열렸다면 자동으로 새 탭을 가리킴)
    actual_page = browser_session.page
    
    checkout_page = CheckoutPage(actual_page)
    actual_page.wait_for_load_state("networkidle")
    
    # 상태 확인
    if checkout_page.is_checkout_page_displayed():
        logger.info("이미 주문서 페이지에 있음")
        return
    
    # 상태가 아니면 강제로 생성
    logger.info("주문서 페이지가 아님. 구매하기 버튼 클릭 수행")
    
    # 장바구니에 상품이 있는지 확인
    cart_page = CartPage(actual_page)
    if not cart_page.has_products():
        # 장바구니가 비어있으면 상품 추가부터 수행
        logger.info("장바구니가 비어있음. 상품 추가 수행")
        product_page = ProductPage(actual_page)
        if not product_page.is_product_detail_displayed():
            # 상품 상세 페이지가 아니면 에러
            logger.warning("상품 상세 페이지가 아님. 현재 페이지에서 장바구니 추가 불가")
            raise ValueError("상품 상세 페이지가 아닌 상태에서 주문서 페이지 진입 불가")
        # 장바구니에 추가 (Atomic POM 조합)
        product_page.wait_for_page_load()
        product_page.click_add_to_cart_button()
    
    # 구매하기 버튼 클릭 (POM 패턴 사용)
    cart_page = CartPage(actual_page)
    cart_page.wait_for_page_load()
    cart_page.click_purchase_button()
    
    # 생성 후 확인
    actual_page.wait_for_load_state("networkidle")
    assert checkout_page.is_checkout_page_displayed(), "주문서 페이지 생성 실패"
    logger.info("주문서 페이지 상태 보장 완료")


@then("주문서 페이지로 이동한다")
def checkout_page_is_displayed(browser_session):
    """
    주문서 페이지로 이동했는지 확인
    
    Args:
        browser_session: BrowserSession 객체 (page 참조 관리)
    """
    # browser_session.page 사용 (새 탭이 열렸다면 자동으로 새 탭을 가리킴)
    actual_page = browser_session.page
    
    checkout_page = CheckoutPage(actual_page)
    actual_page.wait_for_load_state("networkidle")
    assert checkout_page.is_checkout_page_displayed(), "주문서 페이지로 이동하지 않았습니다"
    logger.info("주문서 페이지 이동 확인")


@when(parsers.parse('사용자가 "{bank_name}" 무통장입금으로 주문을 생성한다'))
def user_creates_order_with_bank_transfer(browser_session, bank_name):
    """
    사용자가 무통장입금으로 주문 생성
    
    Args:
        browser_session: BrowserSession 객체 (page 참조 관리)
        bank_name: 은행명
    """
    # browser_session.page 사용 (새 탭이 열렸다면 자동으로 새 탭을 가리킴)
    actual_page = browser_session.page
    
    checkout_page = CheckoutPage(actual_page)
    actual_page.wait_for_load_state("networkidle")
    
    # 은행 종류 선택
    checkout_page.select_bank_type(bank_name)
    # 주문 완료
    checkout_page.click_order_button()
    logger.info(f"무통장입금 주문 생성: {bank_name}")


@then("주문은 입금 대기 상태로 생성된다")
def order_is_created_with_pending_payment(browser_session):
    """
    주문이 입금 대기 상태로 생성되었는지 확인
    
    Args:
        browser_session: BrowserSession 객체 (page 참조 관리)
    """
    # browser_session.page 사용 (새 탭이 열렸다면 자동으로 새 탭을 가리킴)
    actual_page = browser_session.page
    
    actual_page.wait_for_load_state("networkidle")
    # TODO: 주문 완료 페이지에서 입금 대기 상태 확인 로직 구현
    checkout_page = CheckoutPage(browser_session.page)
    
    # actual_page.on("dialog",checkout_page.handle_dialog)

    logger.info("입금 대기 상태 주문 생성 확인")


@when("사용자가 비회원 주문정보를 입력한다")
def user_fill_nonmember_info(browser_session):
    """
    사용자가 비회원 주문정보 입력
    
    Args:
        browser_session: BrowserSession 객체 (page 참조 관리)
    """

    checkout_page = CheckoutPage(browser_session.page)
    browser_session.page.wait_for_load_state("networkidle")

    #주문 정보 입력
    checkout_page.fill_nonmember_info("김찬휘","01094294226","cksgnl777naver.com","gksksla12")
    
    #주문자 정보 동일 체크
    checkout_page.check_equalName()

    logger.info("주문정보 입력 완료")

@then("비회원 주문정보가 정상적으로 입력 되었다")
def check_nonmember_info(browser_session):
    # TODO 비회원 주문정보 정상 입력 확인 로직 구현
    checkout_page = CheckoutPage(browser_session.page)
    browser_session.page.wait_for_load_state("networkidle")
    checkout_page.get_error_messages()
    
    logger.info("비회원 주문정로 정상입력 확인")

@when(parsers.parse('사용자가 주소 "{address}"와 상세주소 "{detailAddress}"를 입력한다'))
def user_fill_address_info(browser_session, address, detailAddress):
    """
    사용자가 주소 입력

    Args:
        browser_session: BrowserSession 객체 (page 참조 관리)    
    """
    checkout_page = CheckoutPage(browser_session.page)
    browser_session.page.wait_for_load_state("networkidle")
    checkout_page.click_find_address()
    checkout_page.fill_address(address)
    checkout_page.fill_detail_address(detailAddress)
    logger.info("주소 입력 완료")

@then("주소가 정상적으로 입력 되었다")
def check_nonmember_info(broser_session):
    # TODO 주소 정상 입력 확인 로직 구현
    logger.info("주소 정상입력 확인")

@when(parsers.parse('사용자가 비회원으로 "{bank_name}" 무통장입금 주문을 생성한다'))
def user_fill_bank_account(browser_session, bank_name):
    
    checkout_page = CheckoutPage(browser_session.page)
    browser_session.page.wait_for_load_state("networkidle")

    # 은행 종류 선택
    checkout_page.select_bank_type(bank_name)

    # 계좌 정보 입력
    checkout_page.fill_bank_account("01094294226","김찬휘")
    
    # 서비스 약관 전체 동의
    checkout_page.check_agreInfoAll()
    
    # 주문 완료
    checkout_page.click_order_button()
    logger.info("주문 생성 완료")


    
