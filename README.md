# Description
Automatically fill the hours in iwom taking into account:

1. No fill weekends
2. Fill as holidays if it is noted in the confluence Santander uk calendar: https://confluence.almuk.santanderuk.corp/calendar/calendarPage.action?spaceKey=APIMANAGERUK&calendarId=49f2f1f0-240e-416a-8034-7b3b25c69163
3. Covers from the beginning of the current month to the current day
4. If it's Friday fill reduced time
5. Fill holidays based on Santander UK Confluence calendar

## Schedule:

Monday to Thursday -> 09:00 - 17:30

Friday -> 09:00 - 16:00

## TODO:

* Include previous months

* Calculate reduced working hours based on months


# Dependencies
```
Python3 / pip
```
# Install requirements modules
```
pip3 install -r requirements.txt
```
# Create config env

Rename .env.example by .env

Fill env vars

```
BASE_URL='https://www.bpocenter-dxc.com/'
IWOM_USER='XXX XXXXXX XXXX'
IWOM_PASS='PASSWORD'
CONFLUENCE_TOKEN='TOKEN'
CONFLUENCE_BASE_URL='https://confluence.almuk.santanderuk.corp'
CA_CERT_PATH='santander-ca.cer'
```
# Run
```
python3 fill-days.py 
```
