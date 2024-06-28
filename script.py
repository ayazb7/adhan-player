import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta, time as dtime
import time
import os

# Function to get prayer times
def get_prayer_times(testing=False):
    url = "https://www.croydonmosque.com/?section=prayer"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    prayer_times = {}

    table = soup.find('table', id='salaat_times_month')
    today_row = table.find('tr', class_='rowToday')

    if today_row:
        cols = today_row.find_all('td')
        prayer_times['Fajr'] = datetime.strptime(cols[3].text.strip() + 'am', '%I:%M%p').time()
        prayer_times['Dhuhr'] = datetime.strptime(cols[6].text.strip() + 'pm', '%I:%M%p').time()
        prayer_times['Asr'] = datetime.strptime(cols[8].text.strip() + 'pm', '%I:%M%p').time()
        prayer_times['Maghrib'] = datetime.strptime(cols[10].text.strip() + 'pm', '%I:%M%p').time()
        prayer_times['Ishaa'] = datetime.strptime(cols[11].text.strip() + 'pm', '%I:%M%p').time()    

    for prayer, prayer_time in prayer_times.items():
        print(f"{prayer}: {prayer_time}")

    return prayer_times


def check_and_play_adhan(prayer_times):
    now = datetime.now().time()
    for prayer, prayer_time in prayer_times.items():
        if now.hour == prayer_time.hour and now.minute == prayer_time.minute:
            print(f"It's time for {prayer} prayer.")
            play_adhan()

def play_adhan():
    os.system('start adhan.mp3') 

if __name__ == "__main__":
    while True:
        prayer_times = get_prayer_times(testing=False)
        check_and_play_adhan(prayer_times)
        now = datetime.now()
        next_minute = (now + timedelta(minutes=1)).replace(second=0, microsecond=0)
        sleep_duration = (next_minute - now).total_seconds()
        time.sleep(sleep_duration)