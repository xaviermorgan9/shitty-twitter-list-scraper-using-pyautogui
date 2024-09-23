import os
import asyncio
import csv
import threading
import time
import re
import pyautogui
import numpy as np
from queue import Queue
from playwright.async_api import async_playwright

def find_color(color_hex):
    target_color = tuple(int(color_hex[i:i + 2], 16) for i in (1, 3, 5))
    screenshot = pyautogui.screenshot()
    screenshot_np = np.array(screenshot)
    for y in range(screenshot_np.shape[0]):
        for x in range(screenshot_np.shape[1]):
            if tuple(screenshot_np[y, x][:3]) == target_color:
                return (x, y)
    return None

def scroll_down():
    while True:
        scroll_wheel_position = find_color('#3E4144') # color might be different for u so change it 
        if scroll_wheel_position:
            x, y = scroll_wheel_position
            pyautogui.moveTo(x, y)
            pyautogui.click()
            for _ in range(10):
                pyautogui.scroll(-1000)
            pyautogui.moveTo(x, y)
        else:
            print("Scroll area not found. Retrying...")
        time.sleep(0.1)

def extract_email(description):
    email_pattern = r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+'
    emails = re.findall(email_pattern, description)
    return ', '.join(emails) if emails else None

async def scrape_profile(playwright, username):
    _xhr_calls = []

    def intercept_response(response):
        if response.request.resource_type == "xhr":
            _xhr_calls.append(response)
    
    profile_url = f'https://twitter.com/{username}'
    browser = await playwright.chromium.launch(headless=True)
    context = await browser.new_context()
    page = await context.new_page()
    page.on("response", intercept_response)
    
    await page.goto(profile_url)
    await page.wait_for_selector("[data-testid='primaryColumn']")
    await asyncio.sleep(3)

    bio = None
    join_date = None
    nickname = None
    user_data_calls = [f for f in _xhr_calls if "UserBy" in f.url]
    for xhr in user_data_calls:
        try:
            data = await xhr.json()
            user_result = data['data']['user']['result']
            bio = user_result['legacy']['description']
            join_date = user_result['legacy']['created_at']  
            nickname = user_result['legacy']['name'] 
            break
        except Exception as e:
            print(f"Error extracting data for {username}: {e}")

    await browser.close()
    return bio, join_date, nickname

async def process_queue(bio_queue):
    async with async_playwright() as playwright:
        with open('followers.csv', 'a', newline='', encoding='utf-8') as csvfile:
            csv_writer = csv.writer(csvfile)
            
            if os.stat('followers.csv').st_size == 0:
                csv_writer.writerow(['Username', 'Nickname', 'Bio', 'Emails', 'Join Date'])

            while True:
                username = bio_queue.get()
                if username is None:
                    break

                print(f"Processing {username}")
                bio, join_date, nickname = await scrape_profile(playwright, username.strip('@'))
                emails = extract_email(bio) if bio else None

                csv_writer.writerow([username, nickname if nickname else '', bio if bio else '', emails if emails else '', join_date if join_date else ''])
                csvfile.flush()  
                print(f"Saved {username}: Nickname - {nickname}, Bio - {bio}, Emails - {emails}, Join Date - {join_date}")
                bio_queue.task_done()

def scrape_usernames_to_queue(list_url, bio_queue):
    async def scrape():
        async with async_playwright() as playwright:
            browser = await playwright.chromium.launch(headless=False)
            context = await browser.new_context(viewport=None)
            page = await context.new_page()
            await page.goto('https://twitter.com/login')
            print("Please log in to Twitter manually.")
            await page.wait_for_selector('a[href="/home"]')
            print("Logged in successfully.")
            await page.goto(list_url)
            followers = set()
            scrolling_thread = threading.Thread(target=scroll_down)
            scrolling_thread.daemon = True
            scrolling_thread.start()
            while True:
                follower_data = await page.evaluate('''
                    Array.from(document.querySelectorAll('a[role="link"] div[dir="ltr"]')).map(userElement => {
                        const usernameSpan = userElement.querySelector('span');
                        const username = usernameSpan && usernameSpan.innerText.startsWith('@') ? usernameSpan.innerText : null;
                        return username;
                    }).filter(username => username);
                ''')
                new_followers = [f for f in follower_data if f not in followers]
                if not new_followers:
                    print("No new followers found, retrying...")
                    await asyncio.sleep(1.5)
                    continue
                for username in new_followers:
                    followers.add(username)
                    bio_queue.put(username)
                    print(f"Scraped follower: {username}")
                await asyncio.sleep(1.5)
            await context.close()
            await browser.close()

    asyncio.run(scrape())

if __name__ == "__main__":
    bio_queue = Queue()
    
    bio_processing_thread = threading.Thread(target=lambda: asyncio.run(process_queue(bio_queue)))
    bio_processing_thread.start()
    
    twitter_list_url = "https://twitter.com/i/lists/1617772739917647876/followers" # input ur list here
    
    scrape_usernames_to_queue(twitter_list_url, bio_queue)
    
    bio_queue.put(None)
    bio_processing_thread.join()
