import sys, os, calendar, datetime, time
from tabulate import tabulate
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from confluence.calendar import ConfluenceCalendar

load_dotenv()

IWOM_USER=os.getenv('IWOM_USER')
IWOM_PASS=os.getenv('IWOM_PASS')
BASE_URL=os.getenv('BASE_URL')


months = {
    'enero': '01',
    'febrero': '02',
    'marzo': '03',
    'abril': '04',
    'mayo': '05',
    'junio': '06',
    'julio': '07',
    'agosto': '08',
    'septiembre': '09',
    'octubre': '10',
    'noviembre': '11',
    'diciembre': '12'
}


def document_initialised(browser):
    return browser.execute_script("return initialised")


def do_login(browser):
    full_url = BASE_URL + 'iwom_web5/Login.aspx'
    browser.get(full_url)
    assert 'Portal Aplicaciones' in browser.title
    
    user_textbox = browser.find_element(By.ID, 'LoginApps_UserName')
    user_textbox.send_keys(IWOM_USER)
    pass_textbox = browser.find_element(By.ID, 'LoginApps_Password')
    pass_textbox.send_keys(IWOM_PASS + Keys.RETURN)
    
    browser.find_element(By.ID, 'MainContent_lblNOMBRE_APP3').click()
    
    browser.switch_to.window(browser.window_handles[1])
    
    # Wait for logout icon == login ok
    WebDriverWait(browser, 30).until(EC.presence_of_element_located((By.ID, 'ctl00_Image3')))
    
    
def get_type(browser):
    available = browser.find_element(By.ID, 'ctl00_Sustituto_Ch_disponible')
    if not available.is_selected():
        select = Select(browser.find_element(By.ID, 'ctl00_Sustituto_D_absentismo'))
        selected_option = select.first_selected_option
        return selected_option.text
    return "workday"
    
def add_leave(browser, type='01 - Vacaciones'):
    available = browser.find_element(By.ID, 'ctl00_Sustituto_Ch_disponible')
    if available.is_selected():
        available.click()
    
    type = Select(browser.find_element(By.ID, 'ctl00_Sustituto_D_absentismo')) # Type of absenteeism
    type.select_by_visible_text('01 - Vacaciones')
    
    browser.find_element(By.ID, 'ctl00_Sustituto_Btn_Guardar2').click() # Save holiday
    
def check_reduced(day):
    
    if day.weekday() == 4:
        return True
    return False
    
def add_workday(browser, reduced):
    available = browser.find_element(By.ID, 'ctl00_Sustituto_Ch_disponible')
    if not available.is_selected():
        available.click()
        
    start_hour = Select(browser.find_element(By.ID, 'ctl00_Sustituto_d_hora_inicio1'))
    start_minute = Select(browser.find_element(By.ID, 'ctl00_Sustituto_D_minuto_inicio1'))
    end_hour = Select(browser.find_element(By.ID, 'ctl00_Sustituto_d_hora_final1'))
    end_minute = Select(browser.find_element(By.ID, 'ctl00_Sustituto_d_minuto_final1'))
    
    if not reduced:
        start_hour.select_by_visible_text('09')
        start_minute.select_by_visible_text('00')
        end_hour.select_by_visible_text('17')
        end_minute.select_by_visible_text('30')
        efective = "08:30"
    else:
        start_hour.select_by_visible_text('09')
        start_minute.select_by_visible_text('00')
        end_hour.select_by_visible_text('16')
        end_minute.select_by_visible_text('00')
        efective = "07:00"
    
    browser.find_element(By.ID, 'ctl00_Sustituto_T_horas').click()
    browser.find_element(By.ID, 'ctl00_Sustituto_T_efectivo').clear()
    browser.find_element(By.ID, 'ctl00_Sustituto_T_efectivo').send_keys(efective)
    browser.find_element(By.NAME, 'ctl00$Sustituto$Btn_Guardar').click() # Save workday
    
def check_day(browser, date):
    browser.find_element(By.ID, 'ctl00_Sustituto_B_Select_calendar').click() # pick calendar
    browser.find_element(By.XPATH, f"//a[@title='{date}']").click() # Select Date
    status = browser.find_element(By.ID, 'ctl00_Sustituto_L_error').get_attribute("innerHTML")
    return { "status": status, "type": get_type(browser) }

def get_month(browser, previous_count=0):
    full_url = BASE_URL + 'iwom_web4/es-corp/app/Jornada/Reg_jornada.aspx'
    browser.get(full_url)
    for x in range(0, previous_count):
        browser.find_element(By.ID, 'ctl00_Sustituto_B_Select_calendar').click() # pick calendar
        browser.find_element(By.XPATH,'//*[@title="Go to the previous month"]').click() # pick date
    current_month = browser.find_element(By.XPATH, "//td[contains(text(), 'de 202')]").get_attribute("innerHTML") # Get current month from calendar
    return current_month

class IwomDate():
    def __init__(self, str_month):
        self.month = str_month.split()[0]
        self.int_month = int(months[self.month])
        self.year = str_month.split()[2]
        self.int_year = int(self.year)
        
    def get_weekdays(self):
        weekdays = []
        c = calendar.Calendar(firstweekday=calendar.MONDAY)
        for week in c.monthdatescalendar(self.int_year, self.int_month):
            for day in week:
                if day.weekday() < 5 and day.month == self.int_month and day <= datetime.date.today():
                    weekdays.append(day)
        return weekdays
    
    def day2iwom(self, day):
        day = str(day).split('-')[2]
        day = day[1:] if day.startswith('0') else day
        return f'{day} de {self.month}'

if __name__ == '__main__':
    # Webdrive options
    chrome_options = Options()
    chrome_options.add_experimental_option("detach", True)
    browser = webdriver.Chrome(options=chrome_options)
    
    # Login
    do_login(browser)
    # Process month
    data = []
    full_month = get_month(browser, 0)
    #full_month = 'enero de 2023'
    
    print (f'Processing month: {full_month}')
    month = IwomDate(full_month)
    for day in month.get_weekdays():
        iwom_day = month.day2iwom(day) # Day in iwom format
        day_result = check_day(browser, iwom_day) # check if day is filled or not
        
        print(f'Processing day: {day}', end="")
        
        cc = ConfluenceCalendar()
        calendar_type = cc.get_calendar_type(str(day)) # Cross confluence Santander UK calendar to check if it's on holiday
        time.sleep(1.5)
        
        # Check if reduced day
        reduced = check_reduced(day)
        
        if not day_result['status']:
            print(f' - Day empty trying to fill it..')
            if calendar_type == 'holiday':
                add_leave(browser, '01 - Vacaciones')
            else:
                add_workday(browser, reduced)
            day_result = check_day(browser, iwom_day)
        else:
            print(f' - Day already filled')
        
        data.append([f'{day} de {full_month}', day_result['status'], calendar_type])
        
    
    table = tabulate(data, headers=['Day', 'Satus', 'Type', 'Calendar Type'])
    print(f'\n{table}')
    