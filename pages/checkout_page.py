"""
주문서서 페이지 객체
"""
from pages.base_page import BasePage
from playwright.sync_api import Page
from typing import Optional, List
import logging
import cv2
import numpy as np
import easyocr

logger = logging.getLogger(__name__)


class CheckoutPage(BasePage):
    """주문서 페이지"""
    
    # 선택자 정의
    
    def __init__(self, page: Page):
        """
        CheckoutPage 초기화
        
        Args:
            page: Playwright Page 객체
        """
        super().__init__(page)

    def is_checkout_page_displayed(self) -> bool:
        """주문서 페이지가 표시되었는지 확인"""
        return self.is_visible("h2.text__main-title")

    def select_payment_method(self, payment_type: str, timeout: Optional[int] = None) -> None:
        """결제 유형 선택
        
        Args:
            payment_type: 선택할 결제 유형 (텍스트)
                - 스마일페이
                - 일반결제
            timeout: 타임아웃 (기본값: self.timeout)
        """
        timeout = timeout or self.timeout
        logger.debug(f"결제 유형 선택: {payment_type}")
        
        # 요소 찾기
        element = self.get_by_text(payment_type)
        
        # 요소가 나타날 때까지 대기
        element.wait_for(state="attached", timeout=timeout)
        logger.debug(f"결제 유형 요소 발견: {payment_type}")
        
        # 요소가 화면에 보이도록 스크롤
        element.scroll_into_view_if_needed(timeout=timeout)
        logger.debug(f"결제 유형 요소 스크롤 완료: {payment_type}")
        
        # 요소가 보일 때까지 대기
        element.wait_for(state="visible", timeout=timeout)
        logger.debug(f"결제 유형 요소 표시 확인: {payment_type}")
        
        # 클릭
        element.click(timeout=timeout)
        logger.info(f"결제 유형 선택 완료: {payment_type}")
    
    def select_normal_payment_method(self, payment_method: str, timeout: Optional[int] = None) -> None:
        """결제 방법 선택
        
        Args:
            payment_method: 선택할 결제 방법 (텍스트)
                - 신용/체크카드
                - 해외발급 신용카드
                - 무통장 입금
                - 휴대폰 소액결제
            timeout: 타임아웃 (기본값: self.timeout)
        """
        timeout = timeout or self.timeout
        logger.debug(f"결제 방법 선택: {payment_method}")
        
        # 요소 찾기
        element = self.get_by_text(payment_method)
        
        # 요소가 나타날 때까지 대기
        element.wait_for(state="attached", timeout=timeout)
        logger.debug(f"결제 방법 요소 발견: {payment_method}")
        
        # 요소가 화면에 보이도록 스크롤
        element.scroll_into_view_if_needed(timeout=timeout)
        logger.debug(f"결제 방법 요소 스크롤 완료: {payment_method}")
        
        # 요소가 보일 때까지 대기
        element.wait_for(state="visible", timeout=timeout)
        logger.debug(f"결제 방법 요소 표시 확인: {payment_method}")
        
        # 클릭
        element.click(timeout=timeout)
        logger.info(f"결제 방법 선택 완료: {payment_method}")
    
    def select_bank_type(self, bank_type: str, timeout: Optional[int] = None) -> None:
        """은행 종류 선택
        
        Args:
            bank_type: 선택할 은행 종류 (텍스트)
            timeout: 타임아웃 (기본값: self.timeout)
        """
        timeout = timeout or self.timeout
        logger.debug(f"은행 종류 선택: {bank_type}")
        
        # 요소 찾기
        element = self.get_by_role("button",name = bank_type)
        
        # 요소가 나타날 때까지 대기
        element.wait_for(state="attached", timeout=timeout)
        logger.debug(f"은행 종류 요소 발견: {bank_type}")
        
        # 요소가 화면에 보이도록 스크롤
        element.scroll_into_view_if_needed(timeout=timeout)
        logger.debug(f"은행 종류 요소 스크롤 완료: {bank_type}")
        
        # 요소가 보일 때까지 대기
        element.wait_for(state="visible", timeout=timeout)
        logger.debug(f"은행 종류 요소 표시 확인: {bank_type}")
        
        # 클릭
        element.click(timeout=timeout)
        logger.info(f"은행 종류 선택 완료: {bank_type}")

    def click_order_button(self, timeout: Optional[int] = None) -> None:
        """
        결제하기 버튼 클릭
        
        Args:
            timeout: 타임아웃 (기본값: self.timeout)
        """
        timeout = timeout or self.timeout
        logger.debug("결제하기 버튼 클릭")
        
        # 요소 찾기

        element = self.get_by_role("button",name = "결제하기")
        # element = self.get_by_text("결제하기")
        
        # 요소가 나타날 때까지 대기
        element.wait_for(state="attached", timeout=timeout)
        logger.debug("결제하기 버튼 발견")
        
        # 요소가 화면에 보이도록 스크롤
        element.scroll_into_view_if_needed(timeout=timeout)
        logger.debug("결제하기 버튼 스크롤 완료")
        
        # 요소가 보일 때까지 대기
        element.wait_for(state="visible", timeout=timeout)
        logger.debug("결제하기 버튼 표시 확인")
        
        # 클릭
        element.click(timeout=timeout)
        logger.info("결제하기 버튼 클릭 완료")
    
    def _get_smilepay_iframe(self):
        """
        스마일페이 iframe을 찾아서 반환
        
        Returns:
            iframe의 content_frame
        """
        # iframe 찾기
        iframes = self.page.locator("iframe").all()
        if not iframes:
            raise Exception("스마일페이 iframe을 찾을 수 없습니다.")
        
        # 첫 번째 iframe으로 전환
        iframe = iframes[0]
        iframe_frame = iframe.content_frame()
        if not iframe_frame:
            raise Exception("스마일페이 iframe content를 가져올 수 없습니다.")
        
        return iframe_frame
    
    def _analyze_smilepay_keypad_numbers(self, timeout: Optional[int] = None) -> List[str]:
        """
        스마일페이 비밀번호 입력 패드의 숫자 버튼들을 OCR로 분석하여 각 버튼의 숫자를 인식
        
        Args:
            timeout: 타임아웃 (기본값: self.timeout)
        
        Returns:
            숫자 버튼들의 인식된 숫자 리스트 (0-9, 백스페이스 등 11개)
        """
        timeout = timeout or self.timeout
        logger.info("스마일페이 비밀번호 입력 패드 숫자 분석 시작")
        
        # EasyOCR 리더 초기화 (한국어, 영어 지원)
        reader = easyocr.Reader(['en', 'ko'], gpu=False)
        
        # iframe 가져오기
        iframe_frame = self._get_smilepay_iframe()
        
        # 숫자 버튼 선택자 (KeyboardsNumbers__Grid__Item 클래스)
        number_buttons = iframe_frame.locator(".KeyboardsNumbers__Grid__Item").all()
        
        if len(number_buttons) != 11:
            logger.warning(f"예상된 11개의 버튼이 아닙니다. 발견된 버튼 수: {len(number_buttons)}")
        
        sm_num = []
        
        for i, button in enumerate(number_buttons):
            try:
                # 버튼이 보일 때까지 대기
                button.wait_for(state="visible", timeout=timeout)
                
                # 버튼 스크린샷을 bytes로 가져오기 (파일 저장 없이)
                screenshot_bytes = button.screenshot(timeout=timeout)
                
                # bytes를 numpy 배열로 변환
                nparr = np.frombuffer(screenshot_bytes, np.uint8)
                img = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)
                
                if img is None:
                    logger.warning(f"이미지를 디코딩할 수 없습니다: 버튼 {i+1}")
                    sm_num.append(" ")
                    continue
                
                # 이미지 리사이즈 및 전처리
                img = cv2.resize(img, None, fx=1.5, fy=2.7, interpolation=cv2.INTER_CUBIC)
                img = cv2.medianBlur(img, 3)
                _, img = cv2.threshold(img, 128, 255, cv2.THRESH_BINARY)
                img = cv2.convertScaleAbs(img, alpha=2, beta=0)  # 대비 강화
                
                # OCR로 숫자 인식 (numpy 배열 직접 전달, 여러 threshold로 시도하여 가장 많이 인식된 값 선택)
                num_k = []
                for threshold_multiplier in range(1, 6):
                    text_threshold = 0.15 * threshold_multiplier
                    try:
                        recognized_text = reader.readtext(
                            img,  # numpy 배열 직접 전달
                            text_threshold=text_threshold,
                            allowlist='0123456789',
                            detail=0
                        )
                        if recognized_text:
                            # 리스트를 평탄화하고 숫자만 추출
                            for text in recognized_text:
                                if text and text.strip():
                                    num_k.append(text.strip())
                    except Exception as e:
                        logger.debug(f"OCR 시도 {threshold_multiplier} 실패: {e}")
                
                # 가장 많이 인식된 숫자 선택
                if num_k:
                    # 빈도수 계산
                    count_n = [num_k.count(num) for num in num_k]
                    if count_n:
                        max_index = count_n.index(max(count_n))
                        read_text = num_k[max_index] if max_index < len(num_k) else " "
                    else:
                        read_text = " "
                else:
                    read_text = " "
                
                logger.debug(f"버튼 {i+1} 인식 결과: {read_text}")
                sm_num.append(read_text)
                
            except Exception as e:
                logger.warning(f"버튼 {i+1} 분석 실패: {e}")
                sm_num.append(" ")
        
        logger.info(f"숫자 패드 분석 완료: {sm_num}")
        return sm_num
    
    def enter_smilepay_password(self, password: str, timeout: Optional[int] = None) -> None:
        """
        스마일페이 비밀번호 입력 패드에서 비밀번호를 입력
        
        Args:
            password: 입력할 비밀번호 (문자열)
            timeout: 타임아웃 (기본값: self.timeout)
        """
        timeout = timeout or self.timeout
        logger.info(f"스마일페이 비밀번호 입력 시작: {password}")
        
        # iframe 가져오기
        iframe_frame = self._get_smilepay_iframe()
        
        # 숫자 패드 분석
        sm_num = self._analyze_smilepay_keypad_numbers(timeout=timeout)
        
        # 비밀번호 각 자리 입력
        for digit in password:
            try:
                # 인식된 숫자 배열에서 해당 숫자의 위치 찾기
                if digit not in sm_num:
                    raise ValueError(f"비밀번호 숫자 '{digit}'를 숫자 패드에서 찾을 수 없습니다. 인식된 숫자: {sm_num}")
                
                # 같은 숫자가 여러 개 있을 수 있으므로 첫 번째 인덱스 사용
                button_index = sm_num.index(digit)
                
                # 해당 버튼 클릭
                number_buttons = iframe_frame.locator(".KeyboardsNumbers__Grid__Item").all()
                if button_index < len(number_buttons):
                    button = number_buttons[button_index]
                    button.wait_for(state="visible", timeout=timeout)
                    button.click(timeout=timeout)
                    logger.debug(f"숫자 '{digit}' 클릭 완료 (버튼 인덱스: {button_index})")
                else:
                    raise ValueError(f"버튼 인덱스 {button_index}가 유효하지 않습니다.")
                
            except Exception as e:
                logger.error(f"숫자 '{digit}' 입력 실패: {e}")
                raise
        
        logger.info("스마일페이 비밀번호 입력 완료")

    def fill_nonmember_info(self, buyername: str, phonenumber: str, email: str, password: str) -> None:
        """
        비회원 정보 입력
        
        Args:
            buyername: 구매자명
            phonenumber: 전화번호
            email: 구매자 이메일
            password: 구매자 비밀번호
        """
        
        self.fill("#xo_id_buyer_name", buyername)
        logger.debug(f"구매자명 입력: {buyername}")
        
        self.fill("#xo_id_buyer_phone_number", phonenumber)
        logger.debug(f"전화번호 입력: {phonenumber}")
        
        self.fill("#xo_id_buyer_email", email)
        logger.debug(f"이메일 입력: {email}")
        
        self.fill("#xo_id_non_member_password", password)
        logger.debug(f"비밀번호 입력: {password}")
        
        self.fill("#xo_id_non_member_password_confirm", password)
        logger.debug(f"비밀번호 확인 입력: {password}")

        logger.info("구매자 정보 입력 완료")
            
    def check_agreInfoAll(self) -> None:
        """전체동의 체크"""
        
        self.locator('label[for="agreeInfoAllTop"]').click()
        logger.info("전체동의 체크 완료")
        
    def check_equalName(self) -> None:
        """주문자 정보와 동일 체크"""
        
        self.locator('label[for="equal-name2"]').click()
        logger.info("주문자 정보와 동일 체크 완료")
        
    
    def _get_address_iframe(self):
        """
        주소찾기 iframe을 찾아서 반환
        
        Returns:
            iframe의 content_frame
        """
        # iframe 찾기
        iframes = self.page.locator("iframe").all()
        if not iframes:
            raise Exception("주소찾기 iframe을 찾을 수 없습니다.")
        
        # 첫 번째 iframe으로 전환
        iframe = iframes[0]
        iframe_frame = iframe.content_frame()
        if not iframe_frame:
            raise Exception("주소찾기 iframe content를 가져올 수 없습니다.")
        
        return iframe_frame


    def click_find_address(self) -> None:
        """
        비회원 주소찾기 버튼 클릭
        
        """
        
        self.click(".button__address-search")
        logger.info("주소찾기 버튼 클릭 완료")


    def fill_address(self, address: str) -> None:
        """
        주소 찾기
        
        Args:
            address: 주소
        """
        iframes = self.page.frame_locator('[title = "주소찾기"]')

        iframes.locator(".input_search").fill(address)
        logger.debug(f"주소: {address}")
        
        iframes.locator(".ico_search").click()
        logger.debug("찾기 버튼")
        
        iframes.locator("#text_address_1_0").click()
        logger.debug("첫번째 주소")
        
        iframes.locator(".btn_set").click()        
        logger.info("주소 선택 클릭 완료")


    
    def fill_detail_address(self, address: str, timeout: Optional[int] = None) -> None:
        """
        주소 찾기
        
        Args:
            address: 상세주소
        """
        timeout = timeout or self.timeout
        logger.debug(f"입력주소: {address}")        


        self.fill('[title = "상세주소 입력"]', address)
        logger.debug(f"주소: {address}") 

        logger.info("상세주소 입력 완료")
        
        
    def fill_bank_account(self, number: str, name: str) -> None:
        """
        은행 계좌번호 입력
        
        Args:
            number: 계좌번호
            name: 예금주명
        """
        self.fill("#xo_id_refund_account_number", number)
        logger.debug(f"계좌번호: {number}")
            
        self.fill("#xo_id_refund_account_owner_name", name)
        logger.debug(f"이름: {name}")
        
        with self.page.expect_event("dialog") as dialog_info:
            self.click("#xo_id_refund_account_confirm_button")
    
        dialog = dialog_info.value
        dialog.accept()

        logger.info("계좌확인 클릭 완료")

    def get_error_messages(self) -> None:
        # 해당 클래스의 모든 텍스트를 리스트로 가져옴
        error_messages = self.locator(".text__error-message").all_inner_texts()
        # 에러 메시지 리스트가 비어있어야(False) 테스트 통과
        # 만약 메시지가 있다면(True) AssertionError 발생
        assert not error_messages, f"구매자 입력 정보 오류: {'//'.join(error_messages)}"
   