"""
상품 관련 Step Definitions
상품 선택 / 상세
"""
from pytest_bdd import given, when, then, parsers
from pages.product_page import ProductPage
from pages.search_page import SearchPage
from pages.home_page import HomePage
import logging

logger = logging.getLogger(__name__)


@then("상품 상세 페이지가 표시된다")
def product_detail_page_is_displayed(browser_session):
    """
    상품 상세 페이지가 표시되는지 확인 (증명)
    
    Args:
        browser_session: BrowserSession 객체 (page 참조 관리)
    """
    product_page = ProductPage(browser_session.page)
    assert product_page.is_product_detail_displayed(), "상품 상세 페이지가 표시되지 않았습니다"
    logger.info("상품 상세 페이지 표시 확인")


@given("상품 상세 페이지가 표시된다")
def product_detail_page_is_displayed_given(browser_session, bdd_context, context):
    """
    상품 상세 페이지 상태 보장 (확인 + 필요시 생성)
    
    Args:
        browser_session: BrowserSession 객체 (page 참조 관리)
        bdd_context: BDD context (step 간 데이터 공유용)
        context: Playwright BrowserContext 객체
    """
    product_page = ProductPage(browser_session.page)
    
    # 상태 확인
    if product_page.is_product_detail_displayed():
        logger.info("이미 상품 상세 페이지에 있음")
        return
    
    # 상태가 아니면 강제로 생성
    logger.info("상품 상세 페이지가 아님. 상품 선택 수행")
    # 기본 page 사용 (검색 결과 페이지는 기본 page에 있을 가능성이 높음)
    # browser_session의 기본 page를 가져오기 위해 context에서 첫 번째 page 사용
    default_page = context.pages[0] if context.pages else browser_session.page
    search_page = SearchPage(default_page)
    
    # 먼저 검색 결과 페이지인지 확인
    if not search_page.is_search_results_displayed():
        # 검색 결과 페이지도 아니면 검색부터 수행
        logger.info("검색 결과 페이지도 아님. 검색 수행")
        home_page = HomePage(default_page)
        home_page.search_product("노트북")
    
    # 상품 선택 (Atomic POM 조합)
    search_page.wait_for_search_results_load()
    new_page = search_page.click_first_product()
    
    # 새 탭이 열렸다면 명시적 페이지 전환
    if new_page:
        browser_session.switch_to(new_page)
        bdd_context.store['product_page'] = new_page
        product_page = ProductPage(browser_session.page)
    else:
        # 새 탭이 열리지 않았으면 같은 페이지에서 이동했을 수 있음
        # default_page가 이미 상품 상세 페이지로 이동했을 수 있으므로
        # default_page를 사용하고 browser_session에도 반영
        # 같은 페이지에서 이동한 경우에도 browser_session 업데이트
        # (URL이 변경되었을 수 있으므로)
        if default_page != browser_session.page:
            browser_session.switch_to(default_page)
            bdd_context.store['product_page'] = default_page
        
        product_page = ProductPage(browser_session.page)
    
    # 생성 후 확인
    assert product_page.is_product_detail_displayed(), "상품 상세 페이지 생성 실패"
    logger.info("상품 상세 페이지 상태 보장 완료")


@then(parsers.parse('상품명에 "{product_name}"이 포함되어 있다'))
def product_name_contains(browser_session, product_name):
    """
    상품 상세 페이지의 상품명 확인
    
    Args:
        browser_session: BrowserSession 객체 (page 참조 관리)
        product_name: 확인할 상품명
    """
    product_page = ProductPage(browser_session.page)
    assert product_page.contains_product_name(product_name), f"상품명에 '{product_name}'이 포함되어 있지 않습니다"
    logger.info(f"상품명 확인: {product_name}")


@when("사용자가 상품 옵션을 선택한다")
def user_selects_product_option(browser_session):
    """
    사용자가 상품 옵션(색상, 사이즈 등) 선택
    
    Args:
        browser_session: BrowserSession 객체 (page 참조 관리)
    """
    product_page = ProductPage(browser_session.page)
    product_page.select_option()
    logger.info("상품 옵션 선택")


@when(parsers.parse('사용자가 "{option_name}" 옵션을 선택한다'))
def user_selects_specific_option(browser_session, option_name):
    """
    사용자가 특정 옵션 선택
    
    Args:
        browser_session: BrowserSession 객체 (page 참조 관리)
        option_name: 옵션명
    """
    product_page = ProductPage(browser_session.page)
    product_page.select_specific_option(option_name)
    logger.info(f"옵션 선택: {option_name}")


@when("사용자가 수량을 변경한다")
def user_changes_quantity(browser_session):
    """
    사용자가 상품 수량 변경
    
    Args:
        browser_session: BrowserSession 객체 (page 참조 관리)
    """
    product_page = ProductPage(browser_session.page)
    product_page.change_quantity()
    logger.info("수량 변경")


@when(parsers.parse('사용자가 수량을 "{quantity}"개로 변경한다'))
def user_changes_quantity_to(browser_session, quantity):
    """
    사용자가 상품 수량을 특정 개수로 변경
    
    Args:
        browser_session: BrowserSession 객체 (page 참조 관리)
        quantity: 수량
    """
    product_page = ProductPage(browser_session.page)
    product_page.change_quantity_to(quantity)
    logger.info(f"수량 변경: {quantity}개")


@then(parsers.parse('상품 가격이 "{price}"로 표시된다'))
def product_price_is_displayed(browser_session, price):
    """
    상품 가격이 올바르게 표시되는지 확인
    
    Args:
        browser_session: BrowserSession 객체 (page 참조 관리)
        price: 예상 가격
    """
    product_page = ProductPage(browser_session.page)
    assert product_page.is_price_displayed(price), f"상품 가격이 '{price}'로 표시되지 않았습니다"
    logger.info(f"상품 가격 확인: {price}")

@when("사용자가 구매하기 버튼을 클릭한다")
def user_clicks_buy_now_button(browser_session):
    """
    사용자가 구매하기 버튼을 클릭한다
    
    Args:
        browser_session: BrowserSession 객체 (page 참조 관리)
    """
    product_page = ProductPage(browser_session.page)
    product_page.click_buy_now_button()
    logger.info("구매하기 클릭 완료")
