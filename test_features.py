# test_features.py
from pytest_bdd import scenarios

# 폴더 전체 대신 문제가 의심되는 파일을 직접 지정해서 에러 추적
scenarios("features")