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
def product_detail_page_is_displayed(page, bdd_context):
    """상품 상세 페이지가 표시되는지 확인 (증명)"""
    # bdd_context에 새 탭이 저장되어 있으면 그것을 사용
    product_page_obj = bdd_context.store.get('product_page')
    if product_page_obj:
        logger.info("bdd_context에서 새 탭(상품 상세 페이지) 사용하여 확인")
        actual_page = product_page_obj
    else:
        logger.info("기존 page 사용하여 확인")
        actual_page = page
    
    product_page = ProductPage(actual_page)
    assert product_page.is_product_detail_displayed(), "상품 상세 페이지가 표시되지 않았습니다"
    logger.info("상품 상세 페이지 표시 확인")


@given("상품 상세 페이지가 표시된다")
def product_detail_page_is_displayed_given(page, bdd_context, context):
    """상품 상세 페이지 상태 보장 (확인 + 필요시 생성)"""
    # bdd_context에 새 탭이 저장되어 있으면 그것을 사용
    product_page_obj = bdd_context.store.get('product_page')
    if product_page_obj:
        logger.info("bdd_context에서 새 탭(상품 상세 페이지) 사용")
        # 새 탭이 이미 열려있으므로 확인만 수행
        product_page = ProductPage(product_page_obj)
        if product_page.is_product_detail_displayed():
            logger.info("새 탭의 상품 상세 페이지 확인됨")
            return
        else:
            logger.warning("새 탭이 있지만 상품 상세 페이지가 아님. 기존 page 사용")
    
    # bdd_context에 product_url이 있으면 context에서 해당 URL의 페이지 찾기
    product_url = bdd_context.store.get('product_url')
    if product_url:
        logger.info(f"product_url로 새 탭 찾기 시도: {product_url}")
        # context의 모든 페이지에서 product_url과 일치하는 페이지 찾기
        found_page = None
        for p in context.pages:
            if p.url == product_url or product_url in p.url:
                logger.info(f"새 탭 찾음: {p.url}")
                # 찾은 페이지를 bdd_context에 저장 (다음 step에서 사용)
                bdd_context.store['product_page'] = p
                found_page = p
                break
        
        if found_page:
            product_page = ProductPage(found_page)
            if product_page.is_product_detail_displayed():
                logger.info("찾은 새 탭의 상품 상세 페이지 확인됨")
                return
            else:
                logger.warning("찾은 새 탭이 상품 상세 페이지가 아님")
        else:
            logger.warning(f"product_url({product_url})과 일치하는 페이지를 찾을 수 없음")
            logger.warning(f"context.pages 개수: {len(context.pages)}")
            for i, p in enumerate(context.pages):
                logger.warning(f"  페이지 {i}: {p.url}")
    
    # 새 탭이 없거나 상품 상세 페이지가 아니면 기존 로직 사용
    product_page = ProductPage(page)
    
    # 상태 확인
    if product_page.is_product_detail_displayed():
        logger.info("이미 상품 상세 페이지에 있음")
        return
    
    # 상태가 아니면 강제로 생성
    logger.info("상품 상세 페이지가 아님. 상품 선택 수행")
    search_page = SearchPage(page)
    
    # 먼저 검색 결과 페이지인지 확인
    if not search_page.is_search_results_displayed():
        # 검색 결과 페이지도 아니면 검색부터 수행
        logger.info("검색 결과 페이지도 아님. 검색 수행")
        home_page = HomePage(page)
        home_page.search_product("노트북")
    
    # 상품 선택 (Atomic POM 조합)
    search_page.wait_for_search_results_load()
    search_page.click_first_product()
    
    # 생성 후 확인
    assert product_page.is_product_detail_displayed(), "상품 상세 페이지 생성 실패"
    logger.info("상품 상세 페이지 상태 보장 완료")


@then(parsers.parse('상품명에 "{product_name}"이 포함되어 있다'))
def product_name_contains(page, product_name):
    """상품 상세 페이지의 상품명 확인"""
    product_page = ProductPage(page)
    assert product_page.contains_product_name(product_name), f"상품명에 '{product_name}'이 포함되어 있지 않습니다"
    logger.info(f"상품명 확인: {product_name}")


@when("사용자가 상품 옵션을 선택한다")
def user_selects_product_option(page):
    """사용자가 상품 옵션(색상, 사이즈 등) 선택"""
    product_page = ProductPage(page)
    product_page.select_option()
    logger.info("상품 옵션 선택")


@when(parsers.parse('사용자가 "{option_name}" 옵션을 선택한다'))
def user_selects_specific_option(page, option_name):
    """사용자가 특정 옵션 선택"""
    product_page = ProductPage(page)
    product_page.select_specific_option(option_name)
    logger.info(f"옵션 선택: {option_name}")


@when("사용자가 수량을 변경한다")
def user_changes_quantity(page):
    """사용자가 상품 수량 변경"""
    product_page = ProductPage(page)
    product_page.change_quantity()
    logger.info("수량 변경")


@when(parsers.parse('사용자가 수량을 "{quantity}"개로 변경한다'))
def user_changes_quantity_to(page, quantity):
    """사용자가 상품 수량을 특정 개수로 변경"""
    product_page = ProductPage(page)
    product_page.change_quantity_to(quantity)
    logger.info(f"수량 변경: {quantity}개")


@then(parsers.parse('상품 가격이 "{price}"로 표시된다'))
def product_price_is_displayed(page, price):
    """상품 가격이 올바르게 표시되는지 확인"""
    product_page = ProductPage(page)
    assert product_page.is_price_displayed(price), f"상품 가격이 '{price}'로 표시되지 않았습니다"
    logger.info(f"상품 가격 확인: {price}")

@when("사용자가 구매하기 버튼을 클릭한다")
def user_clicks_buy_now_button(page, bdd_context, context):
    """사용자가 구매하기 버튼을 클릭한다"""
    # 디버깅: bdd_context 상태 확인
    logger.debug(f"bdd_context.store에 저장된 키: {list(bdd_context.store.keys())}")
    logger.debug(f"product_url: {bdd_context.store.get('product_url')}")
    
    # bdd_context에 새 탭이 저장되어 있으면 그것을 사용 (새 탭이 상품 상세 페이지)
    product_page_obj = bdd_context.store.get('product_page')
    logger.debug(f"product_page_obj 타입: {type(product_page_obj)}")
    logger.debug(f"product_page_obj 값: {product_page_obj}")
    
    if product_page_obj:
        logger.info(f"bdd_context에서 새 탭(상품 상세 페이지) 사용하여 구매하기 클릭 - URL: {product_page_obj.url}")
        actual_page = product_page_obj
    else:
        # bdd_context에 product_url이 있으면 context에서 해당 URL의 페이지 찾기
        product_url = bdd_context.store.get('product_url')
        if product_url:
            logger.info(f"product_url로 새 탭 찾기 시도: {product_url}")
            # context의 모든 페이지에서 product_url과 일치하는 페이지 찾기
            found_page = None
            for p in context.pages:
                if p.url == product_url or product_url in p.url:
                    logger.info(f"새 탭 찾음: {p.url}")
                    # 찾은 페이지를 bdd_context에 저장 (다음 step에서 사용)
                    bdd_context.store['product_page'] = p
                    found_page = p
                    break
            
            if found_page:
                actual_page = found_page
            else:
                logger.warning(f"product_url({product_url})과 일치하는 페이지를 찾을 수 없음. 기존 page 사용")
                logger.warning(f"기존 page URL: {page.url}")
                logger.warning(f"context.pages 개수: {len(context.pages)}")
                for i, p in enumerate(context.pages):
                    logger.warning(f"  페이지 {i}: {p.url}")
                actual_page = page
        else:
            logger.warning("bdd_context에 product_page와 product_url이 모두 없음. 기존 page 사용하여 구매하기 클릭")
            logger.warning(f"기존 page URL: {page.url}")
            actual_page = page
    
    product_page = ProductPage(actual_page)
    product_page.click_buy_now_button()
    logger.info("구매하기 클릭 완료")

@then("주문서 페이지로 이동한다")
def product_price_is_displayed(page, price):
    """주문서 페이지로 이동 확인인"""
    product_page = ProductPage(page)
    assert product_page.is_price_displayed(price), f"상품 가격이 '{price}'로 표시되지 않았습니다"
    logger.info(f"상품 가격 확인: {price}")