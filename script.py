import os
import time
import logging
import argparse
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import requests

# Clear logs at the start of the script
with open('adhan_service.log', 'w'):
    pass

logging.basicConfig(
    filename='adhan_service.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
)

def fetch_prayer_times():
    """Fetch prayer times from the mosque website and parse the table."""
    url = 'https://croydonmosque.com/?section=prayer'
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Locate the correct table
        table = soup.find('table', {'id': 'salaat_times_month'})
        if not table:
            raise ValueError("Prayer times table not found.")
        
        rows = table.find_all('tr')[2:]  # Skip header rows
        
        prayer_times = {}
        today = datetime.now().strftime('%d').lstrip('0')  # Strip leading zero
        
        for row in rows:
            cols = row.find_all('td')
            if not cols:
                continue  # Skip empty rows
            
            # Ensure we match today's date
            if cols[0].text.strip() == today:
                prayer_times['Fajr'] = cols[3].text.strip()
                prayer_times['Dhuhr'] = cols[6].text.strip()
                prayer_times['Asr'] = cols[8].text.strip()
                prayer_times['Maghrib'] = cols[10].text.strip()
                prayer_times['Ishaa'] = cols[11].text.strip()
                break

        if not prayer_times:
            raise ValueError("Prayer times for today not found in the table.")
        
        # Convert to 24-hour format, handling PM for Asr, Maghrib, Ishaa
        for prayer, time_str in prayer_times.items():
            time_obj = datetime.strptime(time_str, '%H:%M')
            if prayer in ['Asr', 'Maghrib', 'Ishaa'] and time_obj.hour < 12:
                time_obj += timedelta(hours=12)  # Convert PM times
            prayer_times[prayer] = time_obj.strftime('%H:%M')
        
        return prayer_times

    except Exception as e:
        logging.error(f"Failed to fetch prayer times: {e}")
        return None

def parse_prayer_time(time_str):
    """Parses prayer time strings to datetime."""
    try:
        prayer_time = datetime.strptime(time_str, '%H:%M')
        now = datetime.now()
        return prayer_time.replace(year=now.year, month=now.month, day=now.day)
    except Exception as e:
        logging.error(f"Failed to parse prayer time {time_str}: {e}")
        return None

def get_next_prayer_time(prayer_times):
    """Returns the next prayer time and its name."""
    now = datetime.now()
    for prayer, time_str in prayer_times.items():
        prayer_time = parse_prayer_time(time_str)
        if prayer_time and prayer_time > now:
            return prayer, prayer_time
    return None, None

def check_and_play_adhan(prayer_times, audio_command):
    """Check if it's time for Adhan and play it."""
    now = datetime.now()
    for prayer, time_str in prayer_times.items():
        prayer_time = parse_prayer_time(time_str)
        if prayer_time and now >= prayer_time and now < prayer_time + timedelta(minutes=5):
            logging.info(f"It's time for {prayer} prayer.")
            play_adhan(audio_command)
            break

def play_adhan(audio_command):
    """Play the Adhan audio."""
    logging.info("Playing Adhan...")
    os.system(audio_command)

def parse_args():
    parser = argparse.ArgumentParser(description="Adhan Player")
    parser.add_argument('platform', choices=['windows', 'linux', 'mac'], help="The platform to run the script on")
    return parser.parse_args()

def main():
    args = parse_args()
    audio_command = {
        'windows': 'start adhan.mp3',
        'linux': 'omxplayer -o alsa:hw:UACDemoV10,0 adhan.mp3',
        'mac': 'afplay adhan.mp3'
    }[args.platform]

    while True:
        prayer_times = fetch_prayer_times()
        logging.info(f"Fetched prayer times: {prayer_times}")
        if prayer_times:
            check_and_play_adhan(prayer_times, audio_command)

            next_prayer, next_prayer_time = get_next_prayer_time(prayer_times)
            if next_prayer:
                logging.info(f"Next prayer is {next_prayer} at {next_prayer_time.time()}")
                sleep_duration = (next_prayer_time - datetime.now()).total_seconds()
                time.sleep(max(0, sleep_duration))
            else:
                logging.warning("No upcoming prayers found. Retrying in 10 minutes.")
                time.sleep(600)
        else:
            logging.error("Failed to fetch prayer times. Retrying in 10 minutes.")
            time.sleep(600)

if __name__ == "__main__":
    main()
