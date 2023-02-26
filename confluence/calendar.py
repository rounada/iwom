import requests, os, pyjq, datetime

from dotenv import load_dotenv
load_dotenv()

class ConfluenceCalendar():
    
    def __init__(self, calendar_id='fb57678e-5912-4195-a55f-a591aaece1e2', headers=None):
        self.headers = headers or {}
        for var in ['CONFLUENCE_BASE_URL', 'CONFLUENCE_TOKEN', 'CA_CERT_PATH']:
            value = os.getenv(var)
            if value is None:
                raise Exception(f'{var} environment variable is not defined')
            
        self.headers['Authorization'] = f'Bearer {os.environ["CONFLUENCE_TOKEN"]}'
        self.base_url = os.environ['CONFLUENCE_BASE_URL']
        self.calendar_id = calendar_id
        self.ca_cert_path = os.environ['CA_CERT_PATH']
    
    def is_holiday_day(self, day):
        path = 'rest/calendar-services/1.0/calendar/events.json'
        url = f'{self.base_url}/{path}'
        params = {
            'subCalendarId': 'fb57678e-5912-4195-a55f-a591aaece1e2',
            'userTimeZoneId': 'Europe/London',
            'start': f'{day}T00:00:00Z',
            'end': f'{day}T23:59:00Z'
        }
        response = requests.get(url, headers=self.headers, params=params, verify=self.ca_cert_path)
        
        self.handle_response_status(response)
        
        current_user=os.environ.get('USER')
        query='.events[] | select(.invitees[].name == "%s") | {"start": .start, "end": .end }' % (current_user.upper())
        ranges = pyjq.all(query, response.json())
        for range in ranges:
            start_date = datetime.datetime.fromisoformat(range['start'][0 : 10])
            end_date = datetime.datetime.fromisoformat(range['end'][0 : 10])
            current_day = datetime.datetime.fromisoformat(day)
            if current_day >= start_date and current_day <= end_date:
                return True
        return False
            
    def get_calendar_type(self, day):
        if self.is_holiday_day(day):
            return 'holiday'
        else:
            return 'workday'
        
    def handle_response_status(self, response):
        if response.status_code >= 400:
            raise Exception(f'Error in API Request {response.status_code}: {response.text}')
        
        
        
        
if __name__ == '__main__':
    from tabulate import tabulate
    import calendar
    
    confluence_calendar = ConfluenceCalendar('fb57678e-5912-4195-a55f-a591aaece1e2')
    
    data = []
    
    now = datetime.datetime.now()

    year = now.year
    month = now.month

    first_day, num_days = calendar.monthrange(year, month)
    
    print(f'Number of days: {num_days} First day {first_day} Year: {year} Month {month}')

    for day in range(1, num_days+1):
        day = datetime.datetime(year, month, day)
        str_day = day.isoformat()
        is_holiday = confluence_calendar.is_holiday_day(str_day[0 : 10])
        
        data.append([str_day, is_holiday])

    table = tabulate(data, headers=['Day', 'Holiday'])
    print(table)
    

