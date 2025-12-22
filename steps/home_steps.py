"""
홈페이지 관련 Step Definitions
진입 / 초기 상태
"""
from pytest_bdd import given, when, then, parsers
from pages.home_page import HomePage
import logging

logger = logging.getLogger(__name__)


@given("사용자가 G마켓 홈페이지에 접속한다")
def user_navigates_to_homepage(page):
    """
    사용자가 G마켓 홈페이지에 접속
    시나리오 태그(@C12345)로 TestRail에 자동 기록됨
    """
    home_page = HomePage(page)
    home_page.navigate()
    logger.info("홈페이지 접속 완료")


@then("홈페이지가 표시된다")
def homepage_is_displayed(page):
    """홈페이지가 올바르게 표시되는지 확인"""
    # TODO: 홈페이지 특정 요소 확인 로직 구현
    logger.info("홈페이지 표시 확인")


@given("브라우저가 실행되었다")
def browser_is_launched(page):
    """브라우저가 실행된 상태 (자동으로 fixture에서 처리됨)"""
    logger.info("브라우저 실행 확인")


@then("페이지가 로드되었다")
def page_is_loaded(page):
    """페이지가 완전히 로드되었는지 확인"""
    page.wait_for_load_state("networkidle")
    logger.info("페이지 로드 완료 확인")
