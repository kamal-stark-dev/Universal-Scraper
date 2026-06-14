import sys
import time
import json
import csv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
# for adding '+' symbol
from urllib.parse import quote

# Set encoding to utf-8 to handle Unicode characters
sys.stdout.reconfigure(encoding='utf-8')

search_query = 'phonk songs'

formatted_query = quote(search_query).replace('%20', '+')

YT_URL = f'https://www.youtube.com/results?search_query={formatted_query}'

chrome_options = Options()
chrome_options.add_argument('--headless')

driver = webdriver.Chrome(options=chrome_options)

driver.get(YT_URL)

# Increase the number of scrolls
for _ in range(10):
    driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.END)
    time.sleep(2)  # sleep to ensure elements load

wait = WebDriverWait(driver, 20)

# Wait for at least 20 thumbnails to be present
wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div#thumbnail img')))

html_content = driver.page_source

soup = BeautifulSoup(html_content, 'html.parser')

videos = []
error = 0

# Explicitly wait for each element
for item in soup.select('div#dismissible'):
    try:
        title_tag = item.select_one('h3 a#video-title')
        channel_tag = item.select_one('div#meta ytd-channel-name a')
        channel_logo_tag = item.select_one('div#channel-info yt-img-shadow img')
        thumbnail_tag = item.select_one('div#thumbnail img')
        video_url = 'https://www.youtube.com' + title_tag['href'] if title_tag and 'href' in title_tag.attrs else None
        views_tag = item.select_one('div#metadata-line span.inline-metadata-item:nth-of-type(1)')
        time_uploaded_tag = item.select_one('div#metadata-line span.inline-metadata-item:nth-of-type(2)')

        # Check if all required information is available
        if title_tag and channel_tag and channel_logo_tag and thumbnail_tag and video_url and views_tag and time_uploaded_tag:
            video = {
                'title': title_tag.text.strip(),
                'channel_name': channel_tag.text.strip(),
                'channel_logo': channel_logo_tag['src'] if channel_logo_tag else None,
                'thumbnail_url': thumbnail_tag['src'] if thumbnail_tag else None,
                'video_url': video_url,
                'views': views_tag.text.strip(),
                'time_uploaded': time_uploaded_tag.text.strip(),
            }

            videos.append(video)
    except Exception as e:
        error += 1
        # print(f"Error processing video: {e}")

print(f"Total errors occurred: {error}")

# Save the video data to a CSV file
csv_file_path = './yt-query-scraper/video_data.csv'
with open(csv_file_path, 'w', encoding='utf-8', newline='') as csvfile:
    fieldnames = ['Title', 'Channel Name', 'Channel Logo', 'Thumbnail URL', 'Video URL', 'Views', 'Time Uploaded']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    # Write header
    writer.writeheader()

    # Write video data
    for video in videos:
        writer.writerow({
            'Title': video['title'],
            'Channel Name': video['channel_name'],
            'Channel Logo': video['channel_logo'],
            'Thumbnail URL': video['thumbnail_url'],
            'Video URL': video['video_url'],
            'Views': video['views'],
            'Time Uploaded': video['time_uploaded'],
        })

# Save the video data to a JSON file
json_file_path = './yt-query-scraper/video_data.json'
with open(json_file_path, 'w', encoding='utf-8') as jsonfile:
    json.dump(videos, jsonfile, ensure_ascii=False, indent=2)

# Print video details
"""
for video in videos:
    print(f"Title: {repr(video['title'])}")
    print(f"Channel Name: {video['channel_name']}")
    print(f"Channel Logo: {video['channel_logo']}")
    print(f"Thumbnail URL: {video['thumbnail_url']}")
    print(f"Video URL: {video['video_url']}")
    print(f"Views: {video['views']}")
    print(f"Time Uploaded: {video['time_uploaded']}")
    print('-' * 50)
"""
driver.quit()