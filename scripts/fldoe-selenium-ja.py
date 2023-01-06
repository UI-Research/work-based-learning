from bs4 import BeautifulSoup
import json
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait
from webdriver_manager.firefox import GeckoDriverManager

def click_button(identifier, by=By.XPATH):    
    element_clickable = EC.element_to_be_clickable((by, identifier))
    element = WebDriverWait(driver, timeout=15).until(element_clickable)
    driver.execute_script("arguments[0].click();", element)

def select_dropdown(identifier, by=By.XPATH, value=None, index=None):
    element_clickable = EC.element_to_be_clickable((by, identifier))
    element = WebDriverWait(driver, timeout=15).until(element_clickable)
    if index is None:
        Select(element).select_by_value(value)
    else:
        Select(element).select_by_index(index)



# Functions

### Click on a discipline link, load all courses and get their info
def get_discipline_courses(discipline_link):
    # Click on the discipline link
    discipline_id = discipline_link.get_attribute('id')
    discipline_link_clickable = EC.element_to_be_clickable((By.ID, discipline_id))
    WebDriverWait(driver, timeout=15).until(discipline_link_clickable)
    discipline_link.click()
    # Grab all the course links
    select_dropdown(identifier='//*[@id="ContentPlaceHolder1_ddlPageSize"]', value='500')
    course_links_clickable = EC.element_to_be_clickable((By.CLASS_NAME, 'btn-link'))
    WebDriverWait(driver, timeout=15).until(course_links_clickable)

    n_course_links = len(driver.find_elements("xpath", '//*[@class="btn-link"]'))
    
    for j in range(n_course_links):
        if j < 499:
            continue
        course_links_clickable = EC.element_to_be_clickable((By.CLASS_NAME, 'btn-link'))
        WebDriverWait(driver, timeout=15).until(course_links_clickable)
        print(f'     Course {j}')
        course_links = driver.find_elements("xpath", '//*[@class="btn-link"]')
        course_link = course_links[j]
        print(len(course_links))
        # print(course_link)
        go_back = 1 if j < n_course_links - 1 else 2 # Need to tweak this to handle multiple pages of courses
        get_course_info(course_link, go_back=go_back)

### Click on course link and retrieve table with description in json format
def get_course_info(course_link, go_back=1):
    print('Entered here')
    # Click on course
    course_id = course_link.get_attribute('id')
    course_link_clickable = EC.element_to_be_clickable((By.ID, course_id))
    WebDriverWait(driver, timeout=15).until(course_link_clickable)
    course_link.click()

    form = driver.find_element("xpath", "/html/body/form/div[3]/table/tbody/tr[3]/td/div/div[3]/div/div[3]/div[2]/div/div[2]/div")
    dict = {}
    dict = get_kv(form)
    kv_to_json(dict)
    print('Going back')
    driver.execute_script(f"window.history.go(-{go_back})")
    print('Went back')

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

if __name__ == '__main__':
    # Home page url
    url = "https://flscns.fldoe.org/Default.aspx"
    service = Service(executable_path=GeckoDriverManager().install())
    driver = webdriver.Firefox(service=service)

    driver.get(url)

    # Go to find an institution course
    click_button(identifier='//*[@id="content"]/nav/div[1]/div/ul/li[2]/a')
    click_button(identifier='//*[@id="dropdownmenu1"]/li[2]/a')
    # Load all disciplines in one page
    select_dropdown(identifier='//*[@id="ContentPlaceHolder1_ddlPageSize"]', value='200')
    # # Click search and load table with discipline links
    click_button(identifier='//*[@id="ContentPlaceHolder1_btnSearch"]')
    # Wait until links are loaded to find them
    element_clickable = EC.element_to_be_clickable((By.CLASS_NAME, 'btn-link'))
    element = WebDriverWait(driver, timeout=15).until(element_clickable)

    
    n_discipline_links = len(driver.find_elements("xpath", '//*[@class="btn-link"]')) # number of course disciplines on the site
    for i in range(n_discipline_links):
        print(f'Discipline {i}')
        discipline_link_clickable = EC.element_to_be_clickable((By.CLASS_NAME, 'btn-link'))
        WebDriverWait(driver, timeout=15).until(discipline_link_clickable)
        discipline_link = driver.find_elements("xpath", '//*[@class="btn-link"]')[i]
        get_discipline_courses(discipline_link)
    driver.quit()