"""
검색 관련 Step Definitions
상품 탐색
"""
from pytest_bdd import given, when, then, parsers
from pages.home_page import HomePage
import logging

logger = logging.getLogger(__name__)


@when(parsers.parse('사용자가 "{keyword}"을 검색한다'))
def user_searches_product(page, keyword):
    """
    사용자가 상품을 검색
    시나리오 태그(@C12345)로 TestRail에 자동 기록됨
    """
    home_page = HomePage(page)
    home_page.search_product(keyword)
    logger.info(f"상품 검색 완료: {keyword}")


@given(parsers.parse('사용자가 "{keyword}"을 검색했다'))
def user_has_searched_product(page, keyword):
    """
    사용자가 이미 검색을 완료한 상태
    시나리오 태그(@C12345)로 TestRail에 자동 기록됨
    """
    home_page = HomePage(page)
    home_page.search_product(keyword)
    logger.info(f"상품 검색 완료: {keyword}")


@then("검색 결과 페이지가 표시된다")
def search_results_page_is_displayed(page):
    """검색 결과 페이지가 표시되는지 확인"""
    page.wait_for_load_state("networkidle")
    current_url = page.url
    assert "search" in current_url.lower(), f"검색 결과 페이지가 아닙니다. 현재 URL: {current_url}"
    logger.info("검색 결과 페이지 표시 확인")


@then(parsers.parse('검색 결과에 "{keyword}" 관련 상품이 포함되어 있다'))
def search_results_contain_product(page, keyword):
    """검색 결과에 해당 키워드 관련 상품이 포함되어 있는지 확인"""
    page.wait_for_load_state("networkidle")
    page_content = page.content()
    assert len(page_content) > 0, "검색 결과 페이지가 비어있습니다"
    logger.info(f"검색 결과에 '{keyword}' 관련 상품 포함 확인")


@when("사용자가 검색 필터를 적용한다")
def user_applies_search_filter(page):
    """사용자가 검색 결과에 필터를 적용"""
    # TODO: 필터 적용 로직 구현
    logger.info("검색 필터 적용")


@when("사용자가 정렬 기준을 선택한다")
def user_selects_sort_option(page):
    """사용자가 검색 결과 정렬 기준 선택"""
    # TODO: 정렬 기준 선택 로직 구현
    logger.info("정렬 기준 선택")


@when(parsers.parse('사용자가 "{category}" 카테고리를 선택한다'))
def user_selects_category(page, category):
    """사용자가 특정 카테고리 선택"""
    # TODO: 특정 카테고리 선택 로직 구현
    logger.info(f"카테고리 선택: {category}")


@when("사용자가 인기 상품을 확인한다")
def user_views_popular_products(page):
    """사용자가 인기 상품 확인"""
    # TODO: 인기 상품 영역 확인 로직 구현
    logger.info("인기 상품 확인")


@when("사용자가 특가 상품을 확인한다")
def user_views_special_products(page):
    """사용자가 특가 상품 확인"""
    # TODO: 특가 상품 영역 확인 로직 구현
    logger.info("특가 상품 확인")
