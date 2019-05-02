from selenium import webdriver
from bs4 import BeautifulSoup
import datetime
import smtplib
from email.mime.text import MIMEText
import os
from os.path import join, dirname
from dotenv import load_dotenv


# 고정 변수

utc_time = datetime.datetime.utcnow()
time_gap = datetime.timedelta(hours=9)
kor_time = utc_time + time_gap
today = kor_time.strftime("%Y.%m.%d.")

if os.uname().sysname == 'Linux':
    os_name = 'linux'
else:
    os_name = 'mac'

if os_name == 'linux':
    dirver_loc = os.path.realpath(__file__)+'/../chromeDriver/linux/chromedriver'
else:
    dirver_loc = os.path.realpath(__file__)+'/../chromeDriver/mac/chromedriver'

naver_login_url = 'https://nid.naver.com/nidlogin.login'
joonggonara_url = 'https://cafe.naver.com/joonggonara.cafe?iframe_url=/ArticleList.nhn%3Fsearch.clubid=10050146%26search.boardtype=L%26viewType=pc'
keyword_list = [
    '소니 a5100','소니 a6000'
]
result_dic = {}
for keyword in keyword_list:
    result_dic[keyword] = {
        'title' : [],
        'writer' : [],
        'href' : [],
        'date' : []
    }
exception_flag = 0
exception_title_keyword_list = ['삽니다','사기','부산','대전','대구','사 기','사  기','ㅅ ㅏㄱ ㅣ','완료','경남','창원']
exception_writer_keyword_list = []

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
    iframe = driver.find_element_by_css_selector('iframe#cafe_main')
    driver.switch_to.frame(iframe)
    # //*[@id="listSizeSelectDiv"]/ul/li[7]/a
    show_element = driver.find_element_by_xpath("""//*[@id="listSizeSelectDiv"]/a""")
    show_element.click()
    show_50_element = driver.find_element_by_xpath("""//*[@id="listSizeSelectDiv"]/ul/li[7]/a""")
    show_50_element.click()

    req = driver.page_source
    html = BeautifulSoup(req, 'html.parser')
    title_list = []
    writer_list = []
    href_list = []
    date_list = []
    # driver.get_screenshot_as_file('naver_main_headless.png')
    for tag in html.select('div#content-area div#main-area table tbody tr'):
        if len(tag.select('div.inner_list > a.article')) < 1:
            continue

        title = tag.select('div.inner_list > a.article')[0].text.strip()
        number = tag.select('div.inner_number')[0].text.strip()
        writer = tag.select('td.p-nick > a.m-tcol-c')[0].text.strip()
        date = tag.select('td.td_date')[0].text.strip()
        if ':' in date:
            date = today

        # 제목 예외처리
        for exception_title_keyword in exception_title_keyword_list:
            if exception_title_keyword in title:
                exception_flag = 1
                break
        # 글쓴이 예외처리
        for exception_writer_keyword in exception_writer_keyword_list:
            if exception_writer_keyword == writer:
                exception_flag = 1
                break

        if exception_flag == 1:
            exception_flag = 0
            continue

        href = 'https://cafe.naver.com/joonggonara/'+number
        # print(title,"//",writer,"//",date)
        # print(href)

        if writer in writer_list:
            pass
        else:
            title_list.append(title)
            writer_list.append(writer)
            href_list.append(href)
            date_list.append(date)
    result_dic[keyword]['title'] = title_list
    result_dic[keyword]['writer'] = writer_list
    result_dic[keyword]['href'] = href_list
    result_dic[keyword]['date'] = date_list
    driver.switch_to.default_content()
driver.quit()
# print(result_dic)

# 파일로 기록


# 1주일 이전 파일 삭제



# 메일 발송
# 메일 본문 작성 먼저
mail_html = "<html><head></head><body>"+kor_time.strftime("%Y/%m/%d %H:%M:%S")+"<br>"  # YYYY/mm/dd HH:MM:SS 형태의 시간 출력
for keyword in keyword_list:
    mail_html += "<h1>"+keyword+" 크롤링 결과</h1>"
    for i,v in enumerate(result_dic[keyword]['title']):
        mail_html += "<p><a href='"+result_dic[keyword]['href'][i]+"'>"+v+" _ "+result_dic[keyword]['writer'][i]+"</a></p>"
        mail_html += "<p>"+result_dic[keyword]['date'][i]+"</p><br>"
    mail_html += "<br>" 
mail_html += "</body></html>"
# print(mail_html)

# Create .env file path.
dotenv_path = join(dirname(__file__), '.env')
# Load file from the path.
load_dotenv(dotenv_path)
# open SMTP
smtp = smtplib.SMTP('smtp.gmail.com', 587)
smtp.ehlo()      # say Hello
smtp.starttls()  # TLS 사용시 필요
smtp.login('doobw@likelion.org', os.getenv('PASSWORD'))
 
# main html
msg = MIMEText(mail_html,'html')
# title
msg['Subject'] = '중고나라 크롤링 결과 보고'
# from
msg['From'] = os.getenv("FROM")
# to
msg['To'] = os.getenv("TO")
# from / to / msg
smtp.sendmail(msg['From'], msg['To'].split(','), msg.as_string())
 
smtp.quit()


