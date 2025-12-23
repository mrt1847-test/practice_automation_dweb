"""
검색 관련 Step Definitions
상품 탐색
"""
from pytest_bdd import given, when, then, parsers
from pages.home_page import HomePage
from pages.search_page import SearchPage
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


@when("사용자가 첫 번째 상품을 선택한다")
def user_selects_first_product(page):
    """사용자가 첫 번째 상품을 선택"""
    search_page = SearchPage(page)
    search_page.select_first_product()
    logger.info("첫 번째 상품 선택 완료")


@when(parsers.parse('사용자가 "{product_name}" 상품을 선택한다'))
def user_selects_product(page, product_name):
    """사용자가 특정 상품을 선택"""
    search_page = SearchPage(page)
    search_page.select_product_by_name(product_name)
    logger.info(f"상품 선택: {product_name}")


@then("검색 결과 페이지가 표시된다")
def search_results_page_is_displayed(page):
    """검색 결과 페이지가 표시되는지 확인 (증명)"""
    search_page = SearchPage(page)
    assert search_page.is_search_results_displayed(), "검색 결과 페이지가 표시되지 않았습니다"
    logger.info("검색 결과 페이지 표시 확인")


@given("검색 결과 페이지가 표시된다")
def search_results_page_is_displayed_given(page):
    """검색 결과 페이지 상태 보장 (확인 + 필요시 생성)"""
    search_page = SearchPage(page)
    
    # 상태 확인
    if search_page.is_search_results_displayed():
        logger.info("이미 검색 결과 페이지에 있음")
        return
    
    # 상태가 아니면 강제로 생성
    logger.info("검색 결과 페이지가 아님. 검색 수행")
    home_page = HomePage(page)
    # 기본 검색어 사용 (또는 설정에서 가져오기)
    home_page.search_product("노트북")
    
    # 생성 후 확인
    assert search_page.is_search_results_displayed(), "검색 결과 페이지 생성 실패"
    logger.info("검색 결과 페이지 상태 보장 완료")


@then(parsers.parse('검색 결과에 "{keyword}" 관련 상품이 포함되어 있다'))
def search_results_contain_product(page, keyword):
    """검색 결과에 해당 키워드 관련 상품이 포함되어 있는지 확인"""
    search_page = SearchPage(page)
    assert search_page.contains_keyword(keyword), f"검색 결과에 '{keyword}' 관련 상품이 포함되어 있지 않습니다"
    logger.info(f"검색 결과에 '{keyword}' 관련 상품 포함 확인")


@when("사용자가 검색 필터를 적용한다")
def user_applies_search_filter(page):
    """사용자가 검색 결과에 필터를 적용"""
    search_page = SearchPage(page)
    search_page.apply_filter()
    logger.info("검색 필터 적용")


@when("사용자가 정렬 기준을 선택한다")
def user_selects_sort_option(page):
    """사용자가 검색 결과 정렬 기준 선택"""
    search_page = SearchPage(page)
    search_page.select_sort_option()
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
