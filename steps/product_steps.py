"""
상품 관련 Step Definitions
상품 선택 / 상세
"""
from pytest_bdd import given, when, then, parsers
import logging

logger = logging.getLogger(__name__)


@given("사용자가 첫 번째 상품을 선택했다")
def user_has_selected_product(page):
    """
    사용자가 이전에 상품을 선택했음을 의미 (실제로 선택 수행)
    시나리오 태그(@C12345)로 TestRail에 자동 기록됨
    """
    # 검색 결과에서 첫 번째 상품 클릭
    page.wait_for_load_state("networkidle")
    page.click("a.item:first-child", timeout=10000)
    logger.info("상품 선택 완료")


@when(parsers.parse('사용자가 "{product_name}" 상품을 선택한다'))
def user_selects_product(page, product_name):
    """사용자가 특정 상품을 선택"""
    # TODO: 상품명으로 상품 선택 로직 구현
    page.wait_for_load_state("networkidle")
    logger.info(f"상품 선택: {product_name}")


@then("상품 상세 페이지가 표시된다")
def product_detail_page_is_displayed(page):
    """상품 상세 페이지가 표시되는지 확인"""
    page.wait_for_load_state("networkidle")
    # TODO: 상품 상세 페이지 특정 요소 확인
    logger.info("상품 상세 페이지 표시 확인")


@then(parsers.parse('상품명에 "{product_name}"이 포함되어 있다'))
def product_name_contains(page, product_name):
    """상품 상세 페이지의 상품명 확인"""
    # TODO: 상품명 확인 로직 구현
    logger.info(f"상품명 확인: {product_name}")


@when("사용자가 상품 옵션을 선택한다")
def user_selects_product_option(page):
    """사용자가 상품 옵션(색상, 사이즈 등) 선택"""
    # TODO: 상품 옵션 선택 로직 구현
    logger.info("상품 옵션 선택")


@when(parsers.parse('사용자가 "{option_name}" 옵션을 선택한다'))
def user_selects_specific_option(page, option_name):
    """사용자가 특정 옵션 선택"""
    # TODO: 특정 옵션 선택 로직 구현
    logger.info(f"옵션 선택: {option_name}")


@when("사용자가 수량을 변경한다")
def user_changes_quantity(page):
    """사용자가 상품 수량 변경"""
    # TODO: 수량 변경 로직 구현
    logger.info("수량 변경")


@when(parsers.parse('사용자가 수량을 "{quantity}"개로 변경한다'))
def user_changes_quantity_to(page, quantity):
    """사용자가 상품 수량을 특정 개수로 변경"""
    # TODO: 수량 변경 로직 구현
    logger.info(f"수량 변경: {quantity}개")


@then(parsers.parse('상품 가격이 "{price}"로 표시된다'))
def product_price_is_displayed(page, price):
    """상품 가격이 올바르게 표시되는지 확인"""
    # TODO: 상품 가격 확인 로직 구현
    logger.info(f"상품 가격 확인: {price}")
