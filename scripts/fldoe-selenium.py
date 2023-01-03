from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from bs4 import BeautifulSoup
import json
import os
driver = webdriver.Chrome()

# Home page url
url = "https://flscns.fldoe.org/Default.aspx"
driver.get(url)

# Go to find an institution course
driver.find_element("xpath", '//*[@id="content"]/nav/div[1]/div/ul/li[2]/a').click()
driver.find_element("xpath", '/html/body/form/div[3]/table/tbody/tr[3]/td/div/nav/div[1]/div/ul/li[2]/ul/li[2]/a').click()

# Load all disciplines in one page
driver.find_element("xpath", '/html/body/form/div[3]/table/tbody/tr[3]/td/div/div[3]/div/div[2]/div[2]/div/div[1]/div/div/select').click()
driver.find_element("xpath", '/html/body/form/div[3]/table/tbody/tr[3]/td/div/div[3]/div/div[2]/div[2]/div/div[1]/div/div/select/option[5]').click()

# Click search and load table with discipline links
driver.find_element("xpath", '/html/body/form/div[3]/table/tbody/tr[3]/td/div/div[3]/div/div[2]/div[2]/div/div[2]/div[1]/div/a[1]').click()
discipline_links = driver.find_elements("xpath", '//*[@class="btn-link"]')

# Functions

### Click on a discipline link, load all courses and get their info
def get_discipline_courses(discipline_link):
    discipline_link.click()
    course_links = driver.find_elements("xpath", '//*[@class="btn-link"]')
    [get_course_info(course_link) for course_link in course_links]

### Click on course link and retrieve table with description in json format
def get_course_info(course_link):
    course_link.click()
    form = driver.find_element("xpath", "/html/body/form/div[3]/table/tbody/tr[3]/td/div/div[3]/div/div[3]/div[2]/div/div[2]/div")
    dict = {}
    dict = get_kv(form)
    kv_to_json(dict)
    driver.execute.script("window.history go(-1)")

### Get key value pairs to construct course json file
def get_kv(form):
    html = form.get_attribute("innerHTML")
    soup = BeautifulSoup(html, 'html.parser')   
    divs = soup.find_all('div', {"class":"form-group form-group-sm"})
    dict = {}
    for div in divs:
        try:
            key = div.find('label').get_text()
            value = div.find("span").get_text()
            dict[key] = value
        except:
            print(f"Nothing to extract")
    
    return dict

def kv_to_json(dict):
    dir_name = dict["Institution"].split()[0].lower()
    dir = f"data/fldoe/{dir_name}"
    if not os.path.exists(dir):
        os.mkdir(dir)
    file_name = dict["Course ID"]
    with open(f'{dir}/{file_name}.json', 'w') as fp:
        json.dump(dict, fp)
