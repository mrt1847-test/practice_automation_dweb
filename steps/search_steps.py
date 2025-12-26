"""
검색 관련 Step Definitions
상품 탐색
"""
from pytest_bdd import given, when, then, parsers
from playwright.sync_api import expect
from pages.home_page import HomePage
from pages.search_page import SearchPage
import logging

logger = logging.getLogger(__name__)


@when(parsers.parse('사용자가 "{keyword}"을 검색한다'))
def user_searches_product(page, keyword):
    """
    사용자가 상품을 검색 (Atomic POM 조합)
    시나리오 태그(@C12345)로 TestRail에 자동 기록됨
    """
    home_page = HomePage(page)
    home_page.fill_search_input(keyword)
    home_page.click_search_button()
    home_page.wait_for_search_results()
    logger.info(f"상품 검색 완료: {keyword}")


@given(parsers.parse('사용자가 "{keyword}"을 검색했다'))
def user_has_searched_product(page, keyword):
    """
    사용자가 이미 검색을 완료한 상태 (Atomic POM 조합)
    시나리오 태그(@C12345)로 TestRail에 자동 기록됨
    """
    home_page = HomePage(page)
    home_page.fill_search_input(keyword)
    home_page.click_search_button()
    home_page.wait_for_search_results()
    logger.info(f"상품 검색 완료: {keyword}")


@when("사용자가 첫 번째 상품을 선택한다")
def user_selects_first_product(page):
    """사용자가 첫 번째 상품을 선택 (Atomic POM 조합)"""
    search_page = SearchPage(page)
    search_page.wait_for_search_results_load()
    search_page.click_first_product()
    logger.info("첫 번째 상품 선택 완료")


@when(parsers.parse('사용자가 "{product_name}" 상품을 선택한다'))
def user_selects_product(page, product_name):
    """사용자가 특정 상품을 선택 (Atomic POM 조합)"""
    search_page = SearchPage(page)
    search_page.wait_for_search_results_load()
    search_page.click_product_by_name(product_name)
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
    # 기본 검색어 사용 (또는 설정에서 가져오기) - Atomic POM 조합
    home_page.fill_search_input("노트북")
    home_page.click_search_button()
    home_page.wait_for_search_results()
    
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


@given(parsers.parse('검색 결과 페이지에 "{module_title}" 모듈이 있다'))
def module_exists_in_search_results(page, module_title):
    """
    검색 결과 페이지에 특정 모듈이 존재하는지 확인하고 보장 (Given)
    
    Args:
        page: Playwright Page 객체
        module_title: 모듈 타이틀
    """
    search_page = SearchPage(page)
    
    # 모듈 존재 확인
    module = search_page.get_module_by_title(module_title)
    expect(module).to_be_visible()
    
    logger.info(f"{module_title} 모듈 존재 확인 완료")


@when(parsers.parse('사용자가 "{module_title}" 모듈 내 상품을 확인하고 클릭한다'))
def user_confirms_and_clicks_product_in_module(page, module_title, scenario):
    """
    모듈 내 상품 노출 확인하고 클릭 (Atomic POM 조합)
    
    Args:
        page: Playwright Page 객체
        module_title: 모듈 타이틀
        scenario: pytest-bdd scenario context (step 간 데이터 공유용)
    """
    search_page = SearchPage(page)
    
    # 모듈로 이동
    module = search_page.get_module_by_title(module_title)
    search_page.scroll_module_into_view(module)
    
    # 모듈 내 상품 찾기
    parent = search_page.get_module_parent(module)
    product = search_page.get_product_in_module(parent)
    search_page.scroll_product_into_view(product)
    
    # 상품 노출 확인
    search_page.assert_product_visible(product)
    
    # 상품 코드 가져오기
    goodscode = search_page.get_product_code(product)
    
    # 상품 클릭
    new_page = search_page.click_product_and_wait_new_page(product)
    
    # scenario context에 저장
    scenario.goodscode = goodscode
    scenario.product_url = new_page.url
    
    logger.info(f"{module_title} 모듈 내 상품 확인 및 클릭 완료: {goodscode}")


@then('상품 페이지로 이동되었다')
def product_page_is_opened(page, scenario):
    """
    상품 페이지 이동 확인 (검증)
    
    Args:
        page: Playwright Page 객체
        scenario: pytest-bdd scenario context
    """
    search_page = SearchPage(page)
    
    # scenario context에서 값 가져오기
    goodscode = getattr(scenario, 'goodscode', None)
    url = getattr(scenario, 'product_url', None)
    
    if not goodscode or not url:
        raise ValueError("goodscode 또는 URL이 설정되지 않았습니다.")
    
    # 검증
    search_page.verify_product_code_in_url(url, goodscode)
    
    logger.info(f"상품 페이지 이동 확인 완료: {goodscode}")


