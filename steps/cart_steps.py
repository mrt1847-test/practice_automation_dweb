"""
장바구니 관련 Step Definitions
장바구니
"""
from pytest_bdd import given, when, then, parsers
from pages.product_page import ProductPage
from pages.cart_page import CartPage
import logging

logger = logging.getLogger(__name__)


@when("사용자가 장바구니에 추가한다")
def user_adds_to_cart(page):
    """
    사용자가 현재 상품을 장바구니에 추가
    시나리오 태그(@C12345)로 TestRail에 자동 기록됨
    """
    product_page = ProductPage(page)
    product_page.add_to_cart()
    logger.info("장바구니에 상품 추가 완료")


@given("사용자가 장바구니에 상품을 담았다")
def user_has_added_to_cart(page):
    """
    사용자가 이미 장바구니에 상품을 담은 상태
    시나리오 태그(@C12345)로 TestRail에 자동 기록됨
    """
    product_page = ProductPage(page)
    product_page.add_to_cart()
    logger.info("장바구니에 상품 추가 완료")


@when("사용자가 장바구니를 확인한다")
def user_views_cart(page):
    """사용자가 장바구니 페이지로 이동"""
    cart_page = CartPage(page)
    cart_page.navigate()
    logger.info("장바구니 확인")


@when("사용자가 장바구니 아이콘을 클릭한다")
def user_clicks_cart_icon(page):
    """사용자가 장바구니 아이콘 클릭"""
    cart_page = CartPage(page)
    cart_page.click_cart_icon()
    logger.info("장바구니 아이콘 클릭")


@then("장바구니 페이지가 표시된다")
def cart_page_is_displayed(page):
    """장바구니 페이지가 표시되는지 확인"""
    cart_page = CartPage(page)
    assert cart_page.is_cart_page_displayed(), "장바구니 페이지가 표시되지 않았습니다"
    logger.info("장바구니 페이지 표시 확인")


@then("장바구니 미리보기가 표시된다")
def cart_preview_is_displayed(page):
    """장바구니 미리보기(드롭다운)가 표시되는지 확인"""
    cart_page = CartPage(page)
    assert cart_page.is_cart_preview_displayed(), "장바구니 미리보기가 표시되지 않았습니다"
    logger.info("장바구니 미리보기 표시 확인")


@then("장바구니에 상품이 담겨있다")
def cart_contains_products(page):
    """장바구니에 상품이 있는지 확인 (증명)"""
    cart_page = CartPage(page)
    assert cart_page.has_products(), "장바구니에 상품이 없습니다"
    logger.info("장바구니에 상품 있음 확인")


@given("장바구니에 상품이 담겨있다")
def cart_contains_products_given(page):
    """장바구니에 상품이 담겨있는 상태 보장 (확인 + 필요시 생성)"""
    from pages.product_page import ProductPage
    from pages.search_page import SearchPage
    from pages.home_page import HomePage
    
    cart_page = CartPage(page)
    
    # 상태 확인
    if cart_page.has_products():
        logger.info("이미 장바구니에 상품이 있음")
        return
    
    # 상태가 아니면 강제로 생성
    logger.info("장바구니가 비어있음. 상품 추가 수행")
    
    # 상품 상세 페이지로 이동 (없으면 생성)
    product_page = ProductPage(page)
    if not product_page.is_product_detail_displayed():
        # 상품 상세 페이지도 없으면 상품 선택부터 수행
        logger.info("상품 상세 페이지가 아님. 상품 선택 수행")
        search_page = SearchPage(page)
        if not search_page.is_search_results_displayed():
            # 검색 결과 페이지도 아니면 검색부터 수행
            logger.info("검색 결과 페이지도 아님. 검색 수행")
            home_page = HomePage(page)
            home_page.search_product("노트북")
        search_page.select_first_product()
    
    # 장바구니에 추가
    product_page.add_to_cart()
    
    # 생성 후 확인
    assert cart_page.has_products(), "장바구니에 상품 추가 실패"
    logger.info("장바구니 상태 보장 완료")


@then("장바구니가 비어있다")
def cart_is_empty(page):
    """장바구니가 비어있는지 확인"""
    cart_page = CartPage(page)
    assert cart_page.is_empty(), "장바구니가 비어있지 않습니다"
    logger.info("장바구니 비어있음 확인")


@then(parsers.parse('장바구니에 "{product_name}" 상품이 "{quantity}"개 담겨있다'))
def cart_contains_product_with_quantity(page, product_name, quantity):
    """장바구니에 특정 상품이 특정 수량으로 담겨있는지 확인"""
    cart_page = CartPage(page)
    assert cart_page.contains_product_with_quantity(product_name, quantity), \
        f"장바구니에 '{product_name}' 상품이 {quantity}개 담겨있지 않습니다"
    logger.info(f"장바구니 상품 확인: {product_name} {quantity}개")


@then("장바구니에 담긴 상품의 총 금액이 표시된다")
def cart_total_price_is_displayed(page):
    """장바구니에 담긴 상품의 총 금액이 표시되는지 확인"""
    cart_page = CartPage(page)
    assert cart_page.is_total_price_displayed(), "장바구니 총 금액이 표시되지 않았습니다"
    logger.info("장바구니 총 금액 표시 확인")


@when(parsers.parse('사용자가 "{product_name}" 상품의 수량을 "{quantity}"개로 변경한다'))
def user_changes_cart_quantity(page, product_name, quantity):
    """사용자가 장바구니 내 상품 수량 변경"""
    cart_page = CartPage(page)
    cart_page.change_product_quantity(product_name, quantity)
    logger.info(f"장바구니 상품 수량 변경: {product_name} → {quantity}개")


@when(parsers.parse('사용자가 "{product_name}" 상품을 장바구니에서 제거한다'))
def user_removes_from_cart(page, product_name):
    """사용자가 장바구니에서 특정 상품 제거"""
    cart_page = CartPage(page)
    cart_page.remove_product(product_name)
    logger.info(f"장바구니에서 상품 제거: {product_name}")


@when("사용자가 장바구니를 비운다")
def user_clears_cart(page):
    """사용자가 장바구니의 모든 상품 제거"""
    cart_page = CartPage(page)
    cart_page.clear_cart()
    logger.info("장바구니 비우기")
