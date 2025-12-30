# test_features.py
from pytest_bdd import scenarios
import pytest
import steps.home_steps
import steps.login_steps
import steps.search_steps
import steps.product_steps
import steps.cart_steps
import steps.checkout_steps
import steps.order_steps
# 폴더 전체 대신 문제가 의심되는 파일을 직접 지정해서 에러 추적
scenarios("features/purchase_flow.feature")