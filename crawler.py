import os
from selenium import webdriver


# 고정 변수

if os.uname().sysname == 'Linux':
    os_name = 'linux'
else:
    os_name = 'mac'

if os_name == 'linux':
    dirver_loc = './chromeDriver/linux/chromedriver'
else:
    dirver_loc = './chromeDriver/mac/chromedriver'

naver_login_url = 'https://nid.naver.com/nidlogin.login'
joonggonara_url = 'https://cafe.naver.com/joonggonara.cafe?iframe_url=/ArticleList.nhn%3Fsearch.clubid=10050146%26search.boardtype=L%26viewType=pc'
keyword_list = [
    '소니 a5100',
]

# Headless chrome 사용법에 대해서는 아래 URL을 참고한다.
# https://beomi.github.io/gb-crawling/posts/2017-09-28-HowToMakeWebCrawler-Headless-Chrome.html

options = webdriver.ChromeOptions()
options.add_argument('headless')
options.add_argument('window-size=1920x1080')
options.add_argument("disable-gpu")

driver = webdriver.Chrome(dirver_loc, options=options)

# driver.get('http://naver.com')
# driver.implicitly_wait(3)
# driver.get_screenshot_as_file('naver_main_headless.png')

# 네이버 로그인
# 생략

# 중고나라 접속 및 검색어 크롤링
driver.get(joonggonara_url)
driver.implicitly_wait(3)
# driver.get_screenshot_as_file('naver_main_headless.png')

search_input = driver.find_element_by_css_selector('input#topLayerQueryInput')
for keyword in keyword_list:
    search_input.send_keys(keyword)
    search_button = driver.find_element_by_css_selector("form[name='frmBoardSearch'] > button")
    search_button.click()
    driver.implicitly_wait(3)
    # driver.get_screenshot_as_file('naver_main_headless.png')


# 메일 발송

driver.quit()