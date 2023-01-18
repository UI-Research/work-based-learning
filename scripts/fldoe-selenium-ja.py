from bs4 import BeautifulSoup
import json
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
# from selenium.webdriver.firefox.service import Service
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait
import time
# from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.chrome import ChromeDriverManager

def click_button(identifier, by=By.XPATH, timeout=15):   
    '''
    This function waits until a button is clickable and then clicks on it.

    Inputs:
        identifier (string): The Id, XPath, or other way of identifying the element to be clicked on
        by (By object): How to identify the identifier (Options include By.XPATH, By.ID, By.Name and others).
            Make sure 'by' and 'identifier' correspond to one other as they are used as a tuple pair below.
        timeout (int): How long to wait for the object to be clickable

    Returns:
        None (just clicks on button)
    '''

    element_clickable = EC.element_to_be_clickable((by, identifier))
    element = WebDriverWait(driver, timeout=timeout).until(element_clickable)
    driver.execute_script("arguments[0].click();", element)

def select_dropdown(identifier, by=By.XPATH, value=None, index=None):
    '''
    This function clicks on the correct dropdown option in a dropdown object.
    It first waits until the element becomes selectable before locating the proper drop down menu. Then it selects the proper option.
    If the page doesn't load within 15 seconds, it will return a timeout message.

    Inputs:
        id (string): This is the HTML 'value' of the dropdown menu to be selected, 
            found through inspecting the web page.
        value (string): The value to select from the dropdown menu.
        index (int): If index is not None, function assumes we want to select an option by its index instead of by specific value. 
            In this case, should specify that value = None.
    
    Returns:
        None (just selects on the right item in the dropdown menu)
    '''
    element_clickable = EC.element_to_be_clickable((by, identifier))
    element = WebDriverWait(driver, timeout=15).until(element_clickable)
    if index is None:
        Select(element).select_by_value(value)
    else:
        Select(element).select_by_index(index)
    print('selected!')

### Get key value pairs to construct course json file
def get_kv(form):
    '''
    [MANU TO FILL IN]
    '''
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
            pass
            # print(f"Nothing to extract")
    
    return dict

def kv_to_json(dict):
    '''
    [MANU TO FILL IN]
    '''
    dir_name = dict["Institution"].split()[0].lower()
    dir = f"data/fldoe/{dir_name}"
    if not os.path.exists(dir):
        os.mkdir(dir)
    file_name = dict["Course ID"]
    with open(f'{dir}/{file_name}.json', 'w') as fp:
        json.dump(dict, fp)


def get_course_info(course_link, go_back=1):
    '''
    This function clicks on a course link and retrieves a table with the course description in JSON format.

    Inputs:
        course_link (HTML object): Course link found using Selenium's find_elements functionality
        go_back (int): The number of pages to traverse backward, currently no values other than 1 are used.

    Returns:
        None (just writes out the JSON data for the course)
    '''
    # Click on course
    course_id = course_link.get_attribute('id')
    click_button(course_id, by=By.ID)
    # Wait until HTML panel housing the course information is loaded on the page
    try:
        course_panel_loaded = EC.presence_of_element_located((By.XPATH, '//*[@id="ContentPlaceHolder1_pnlTabCollectionDiscipline"]/div/div[2]'))
        WebDriverWait(driver, timeout=15).until(course_panel_loaded)
    except:
        print('Couldn\'t find element')
    form = driver.find_element('xpath', '//*[@id="ContentPlaceHolder1_pnlTabCollectionDiscipline"]/div/div[2]') #/div")
    dict = {}
    dict = get_kv(form)
    kv_to_json(dict)
    driver.execute_script(f"window.history.go(-{go_back})")


def get_discipline_courses(discipline_link, discipline_number, skip_to_end=False, start_page=1, start_course=0):
    '''
    This function clicks on a discipline link, loads all of the courses, and calls get_course_info()

    Inputs:
        discipline_link (HTML object): The discipline link, found using Selenium's find_elements functionality
        discipline_number (int): Which discipline we are currently iterating through, only used in print statement for readability
    TEST Inputs (used for development):
        skip_to_end (bool): If True, will skip to final page of a given discipline, otherwise starts at the beginning.
            Useful for testing to make sure there is a smooth transition of the scraper between disciplines.
        start_page and start_course (int): Not currently used, also just for testing edge cases and transitions between courses/disciplines.

    Returns:
        None
    '''
    # Click on the discipline link
    discipline_id = discipline_link.get_attribute('id')
    click_button(discipline_id, by=By.ID)
    # Check to make sure we've navigated to the course page
    # on_course_page = EC.
    # Grab all the course links
    select_dropdown(identifier='//*[@id="ContentPlaceHolder1_ddlPageSize"]', value='500')
    
    # Get number of pages of courses
    try:
        page_numbers_present = EC.presence_of_element_located((By.XPATH, '//*[@id="ContentPlaceHolder1_gvCoursesGridview"]/tbody/tr[502]/td/table/tbody/tr/td[1]/span'))
        WebDriverWait(driver, timeout=10).until(page_numbers_present)
        n_pages = int(driver.find_elements(By.TAG_NAME, 'tbody')[-2].size['width']//32)
    except:
        n_pages = 1
    print(f'{n_pages} page(s) of courses')
    
    # Block is only relevant for development, not in final version.
    # But still need to initialize "current_page" if this is commented out
    current_page = n_pages if skip_to_end else start_page
    if current_page != 1:
        click_button(identifier=f'//*[@id="ContentPlaceHolder1_gvCoursesGridview"]/tbody/tr[502]/td/table/tbody/tr/td[{current_page}]/a')
        time.sleep(5)

    # Iterate over all pages of courses within the discipline
    more_pages = True
    while more_pages:
        # Within a page, determine how many courses there are
        course_links_clickable = EC.element_to_be_clickable((By.CLASS_NAME, 'btn-link'))
        WebDriverWait(driver, timeout=15).until(course_links_clickable)
        n_course_links = len(driver.find_elements("xpath", '//*[@class="btn-link"]'))
        print(f'{n_course_links} courses on this page')
        # Iterate over all the courses on that page, calling get_course_info() for each one
        for j in range(n_course_links):
            # Take break every 15 links to give page chance to reload
            if j % 15 == 14:
                print('Sleeping for 30 seconds')
                time.sleep(30)
            # if block only needed if you don't want to start with the first course on a page
            if skip_to_end and j < n_course_links - 1:
                continue
            course_links_clickable = EC.element_to_be_clickable((By.CLASS_NAME, 'btn-link'))
            WebDriverWait(driver, timeout=15).until(course_links_clickable)
            print(f'Discipline {discipline_number}, Page {current_page}, Course {j}')
            course_links = driver.find_elements("xpath", '//*[@class="btn-link"]')
            course_link = course_links[j]
            go_back = 1
            get_course_info(course_link, go_back=go_back)
        current_page += 1

        # After getting all courses on a page, try to go to the next page. 
        # If there isn't one, click on "Reset Filters" button in preparation for transition to the next discipline and exit the while loop
        try:
            click_button(identifier=f'//*[@id="ContentPlaceHolder1_gvCoursesGridview"]/tbody/tr[502]/td/table/tbody/tr/td[{current_page}]/a', timeout=10)
            print(f'Proceeding to page {current_page}')
            print('Sleeping for 60 seconds')
            time.sleep(60)
            

        except:
            print(f'There is no page {current_page}, resetting filters')
            more_pages = False
            click_button(identifier='//*[@id="ContentPlaceHolder1_cmdResetFilters"]')
            print('Sleeping for 60 seconds')
            time.sleep(60)
            


if __name__ == '__main__':
    # Can tweak this parameter based on how many disciplines have been successfully scraped
    START_DISCIPLINE = 14

    # Home page url
    url = "https://flscns.fldoe.org/Default.aspx"
    service = Service(executable_path=ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)
    driver.get(url)

    # Go to find an institution course  
    click_button(identifier='//*[@id="content"]/nav/div[1]/div/ul/li[2]/a')
    click_button(identifier='//*[@id="dropdownmenu1"]/li[2]/a')
    # Load all disciplines in one page
    select_dropdown(identifier='//*[@id="ContentPlaceHolder1_ddlPageSize"]', value='500')
    # Click search and load table with discipline links
    click_button(identifier='//*[@id="ContentPlaceHolder1_btnSearch"]')
    # Wait until links are loaded in order to find them
    element_clickable = EC.element_to_be_clickable((By.CLASS_NAME, 'btn-link'))
    element = WebDriverWait(driver, timeout=15).until(element_clickable)

    # Get number of course disciplines on the site
    n_discipline_links = len(driver.find_elements("xpath", '//*[@class="btn-link"]')) 
    for i in range(n_discipline_links):
        if i < START_DISCIPLINE: # Will skip if already have that data scraped
            continue
        print(f'*****SCRAPING DISCIPLINE {i}*****')
        # After the first iteration, will have to re-click on the Search button each time we transition to next discipline
        if i > START_DISCIPLINE:
            click_button(identifier='//*[@id="ContentPlaceHolder1_btnSearch"]')
            element_clickable = EC.element_to_be_clickable((By.CLASS_NAME, 'btn-link'))
            element = WebDriverWait(driver, timeout=15).until(element_clickable)
        discipline_link = driver.find_elements("xpath", '//*[@class="btn-link"]')[i]
        if i == START_DISCIPLINE:
            get_discipline_courses(discipline_link, discipline_number=i, start_page=2)
        else:
            get_discipline_courses(discipline_link, discipline_number=i)
        # Only used for development:
        # if i < 2: # Can tweak this number based on how many disciplines' courses are finished downloading
        #     get_discipline_courses(discipline_link, discipline_number=i, skip_to_end=True)
        # else:
        #     get_discipline_courses(discipline_link, discipline_number=i)
    driver.quit()


    # Pages that aren't working: Discipline 14, Page 2