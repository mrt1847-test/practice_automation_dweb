
import pydata_google_auth
import gspread
import json
import os
import platform

SCOPES = ['https://www.googleapis.com/auth/drive', 'https://www.googleapis.com/auth/spreadsheets']
credentials = pydata_google_auth.get_user_credentials(SCOPES, auth_local_webserver=True)
credentials.access_token = credentials.token
gc = gspread.authorize(credentials)

spreadsheet_url = "https://docs.google.com/spreadsheets/d/1Hmrpoz1EVACFY5lHW7r4v8bEtRRFu8eay7grCojRr3E/edit?gid=0#gid=0"
sh = gc.open_by_url(spreadsheet_url)
worksheet = sh.worksheet("mweb")
os_version = platform.platform()
if 'Windows' in os_version:  # windows인 경우
  param_json_path = os.path.dirname(__file__) + '\\json\\'
  current_json = param_json_path + os.path.splitext(os.path.basename(__file__))[0] + '.json'
elif 'mac' in os_version:
  param_json_path = os.path.dirname(__file__) + '/json/'
  current_json = param_json_path + os.path.splitext(os.path.basename(__file__))[0] + '.json'

with open(current_json, 'r', encoding='utf-8') as file:
  json_data = json.load(file)

def input_pass(sheet_num):
  if json_data[0]["tc{0}".format(sheet_num)]["use_type"] == 2:
    worksheet.update([["pass"]], f"D{sheet_num+2}")
    worksheet.format(f"D{sheet_num+2}", {"textFormat": {"foregroundColor": {"red": 0.0, "green": 0.5, "blue": 0.0}, "bold": True}})
    worksheet.update([[" "]], f"E{sheet_num+2}")
  else:
    worksheet.update([["untest"]], f"D{sheet_num+2}")
    worksheet.format(f"D{sheet_num+2}",
                     {"textFormat": {"foregroundColor": {"red": 0.5, "green": 0.5, "blue": 0.5}, "bold": True}})
    worksheet.update([[" "]], f"E{sheet_num+2}")
def input_fail(sheet_num, error_reason):
  worksheet.update([["fail"]], f"D{sheet_num+2}")
  worksheet.format(f"D{sheet_num+2}", {"textFormat": {"foregroundColor": {"red": 1.0, "green": 0.0, "blue": 0.0}, "bold": True}})
  worksheet.update([[str(error_reason)]], f"E{sheet_num+2}")

# 앱에서 자동화 테스트 수행
# 명령어 python -m pytest --cache-clear .\test.py -s
def test1(driver):
  from src.home import HomePage
  from src.etc import EtcFunction
  home_page = HomePage(driver)
  etc_func= EtcFunction(driver)
  try:
    home_page.input_move_login_screen(2)
    # home_page.ss_1_2_1_4(json_data[0]['tc4']['use_type'])
    # etc_func.input_login_account_type(2)
    value = etc_func.smile_pay_num(2)
    input_pass(1)
    worksheet.update([[value]], "E3")
  except Exception as e:
    input_fail(1, e)
  try:
    home_page.input_move_login_screen(json_data[0]["tc2"]["use_type"])
    input_pass(2)
  except Exception as e:
    input_fail(2, e)
