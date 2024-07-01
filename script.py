import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta, time as dtime
import time
import os
import json

CACHE_FILE = 'prayer_times_cache.json'

def time_to_string(t):
    return t.strftime('%H:%M')

def string_to_time(s):
    return datetime.strptime(s, '%H:%M').time()

def cache_prayer_times(prayer_times):
    serializable_prayer_times = {date: {prayer: time_to_string(t) for prayer, t in times.items()} for date, times in prayer_times.items()}
    with open(CACHE_FILE, 'w') as f:
        json.dump(serializable_prayer_times, f)

def load_cached_prayer_times():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, 'r') as f:
            cached_prayer_times = json.load(f)
            return {date: {prayer: string_to_time(t) for prayer, t in times.items()} for date, times in cached_prayer_times.items()}
    return None

# Function to get prayer times
def get_prayer_times(testing=False):
    url = "https://www.croydonmosque.com/?section=prayer"
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        prayer_times = {}
        table = soup.find('table', id='salaat_times_month')
        rows = table.find_all('tr')

        for row in rows:
            cols = row.find_all('td')
            if len(cols) > 11: 
                date = cols[0].text.strip().zfill(2) 
                prayer_times[date] = {
                    # 'test': dtime(hour=16, minute=30),
                    'Fajr': datetime.strptime(cols[3].text.strip() + 'am', '%I:%M%p').time(),
                    'Dhuhr': datetime.strptime(cols[6].text.strip() + 'pm', '%I:%M%p').time(),
                    'Asr': datetime.strptime(cols[8].text.strip() + 'pm', '%I:%M%p').time(),
                    'Maghrib': datetime.strptime(cols[10].text.strip() + 'pm', '%I:%M%p').time(),
                    'Ishaa': datetime.strptime(cols[11].text.strip() + 'pm', '%I:%M%p').time()
                }
        
        cache_prayer_times(prayer_times)
        
        today_date = datetime.now().strftime('%d').zfill(2)
        today_prayer_times = prayer_times.get(today_date)
        
        if today_prayer_times:
            for prayer, prayer_time in today_prayer_times.items():
                print(f"{prayer}: {prayer_time}")

        return today_prayer_times

    except Exception as e:
        print(f"Failed to fetch from the website due to {e}. Loading from cache...")
        cached_prayer_times = load_cached_prayer_times()
        if cached_prayer_times:
            today_date = datetime.now().strftime('%d').zfill(2)
            today_prayer_times = cached_prayer_times.get(today_date)
            
            if today_prayer_times:
                for prayer, prayer_time in today_prayer_times.items():
                    print(f"{prayer}: {prayer_time}")

            return today_prayer_times
        else:
            print("No cached data available.")
            return {}

def get_next_prayer_time(prayer_times, cached_prayer_times):
    now = datetime.now().time()
    future_prayers = {prayer: prayer_time for prayer, prayer_time in prayer_times.items() if prayer_time > now}
    
    if not future_prayers:
        next_prayer = 'Fajr'
        tomorrow_date = (datetime.now() + timedelta(days=1)).strftime('%d').zfill(2)
        next_prayer_time = datetime.combine(datetime.now() + timedelta(days=1), cached_prayer_times[tomorrow_date][next_prayer])
    else:
        next_prayer = min(future_prayers, key=future_prayers.get)
        next_prayer_time = datetime.combine(datetime.now(), future_prayers[next_prayer])
    
    return next_prayer, next_prayer_time

def check_and_play_adhan(prayer_times):
    now = datetime.now().time()
    for prayer, prayer_time in prayer_times.items():
        if now.hour == prayer_time.hour and now.minute == prayer_time.minute:
            print(f"It's time for {prayer} prayer.")
            play_adhan()

def play_adhan():
    os.system('afplay adhan.mp3')
    # os.system('start adhan.mp3')
    # os.system('omxplayer -o local adhan.mp3') 

def main():
    while True:
        prayer_times = get_prayer_times(testing=False)
        cached_prayer_times = load_cached_prayer_times()
        if prayer_times:
            check_and_play_adhan(prayer_times)
        
            next_prayer, next_prayer_time = get_next_prayer_time(prayer_times, cached_prayer_times)
            print(f"Next prayer is {next_prayer} at {next_prayer_time.time()}")
            
            sleep_duration = (next_prayer_time - datetime.now()).total_seconds()
            time.sleep(sleep_duration)
        else:
            time.sleep(60)

if __name__ == "__main__":
    main()
