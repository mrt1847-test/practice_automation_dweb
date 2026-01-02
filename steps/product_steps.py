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
def product_detail_page_is_displayed_given(browser_session, context):
    """
    상품 상세 페이지 상태 보장 (확인 + 필요시 생성)
    
    우선순위:
    1. 현재 browser_session.page가 이미 상품 상세 페이지인지 확인
    2. 검색 결과 페이지에서 상품 클릭하여 생성
    
    Args:
        browser_session: BrowserSession 객체 (page 참조 관리, module scope로 같은 feature 파일의 시나리오들이 공유)
        context: Playwright BrowserContext 객체
    """
    # 1. 현재 browser_session.page가 이미 상품 상세 페이지인지 확인
    product_page = ProductPage(browser_session.page)
    if product_page.is_product_detail_displayed():
        logger.info("현재 페이지가 이미 상품 상세 페이지임")
        return
    
    # 2. 검색 결과 페이지에서 상품 클릭하여 생성
    logger.info("상품 상세 페이지 생성 시작")
    
    # 검색 결과 페이지 찾기 (context의 모든 페이지 확인)
    search_page_obj = None
    search_page_base = None
    for page in context.pages:
        search_page = SearchPage(page)
        if search_page.is_search_results_displayed():
            search_page_obj = search_page
            search_page_base = page
            break
    
    # 검색 결과 페이지를 찾지 못했으면 현재 페이지 사용
    if not search_page_obj:
        search_page_base = browser_session.page
        search_page_obj = SearchPage(search_page_base)
        
        # 검색 결과 페이지가 아니면 검색 수행
        if not search_page_obj.is_search_results_displayed():
            logger.info("검색 결과 페이지가 아님. 검색 수행")
            home_page = HomePage(search_page_base)
            home_page.search_product("노트북")
            # 검색 후 다시 SearchPage 생성
            search_page_obj = SearchPage(search_page_base)
    
    # 상품 선택 (Atomic POM 조합)
    search_page_obj.wait_for_search_results_load()
    new_page = search_page_obj.click_first_product()
    
    # 새 탭이 열렸다면 명시적 페이지 전환
    if new_page:
        browser_session.switch_to(new_page)
        # 새 탭이 완전히 로드될 때까지 대기 (domcontentloaded는 이미 click_product_and_wait_new_page에서 대기함)
        # 추가로 페이지가 제어 가능한 상태인지 확인
        try:
            # 페이지가 닫히지 않았는지 확인
            if new_page.is_closed():
                raise Exception("새 탭이 이미 닫혀있습니다")
            
            # URL이 유효한지 확인 (about:blank가 아닌지)
            current_url = new_page.url
            if not current_url or current_url == "about:blank":
                logger.warning(f"새 탭의 URL이 유효하지 않음: {current_url}")
                # 잠시 대기 후 다시 확인
                new_page.wait_for_timeout(1000)
                current_url = new_page.url
                if not current_url or current_url == "about:blank":
                    raise Exception(f"새 탭의 URL이 여전히 유효하지 않음: {current_url}")
            
            logger.debug(f"새 탭 전환 완료 - URL: {current_url}")
        except Exception as e:
            logger.error(f"새 탭 전환 후 확인 실패: {e}")
            raise
        
        product_page = ProductPage(browser_session.page)
    else:
        # 같은 페이지에서 이동한 경우
        # search_page_base가 이미 상품 상세 페이지로 이동했을 수 있음
        if search_page_base != browser_session.page:
            browser_session.switch_to(search_page_base)
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
    try:
        product_page.select_group_product(1)
    except:
        logger.debug(f"그룹상품 선택 실패")
        pass
    product_page.click_buy_now_button()
    logger.info("구매하기 클릭 완료")
