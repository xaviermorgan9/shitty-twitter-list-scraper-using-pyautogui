# Twitter Follower Scraper

This Python script automates the process of scraping follower details (username, nickname, bio, email, and join date) from a Twitter list. It uses `Playwright` for browser automation, `PyAutoGUI` for screen interactions like scrolling, and `asyncio` for asynchronous processing.

## Features
- Has some of the worst code that probably won't work on your pc without changing a few things
- Scrapes follower data from a specified Twitter list.
- Extracts email addresses from bios using regular expressions.
- Automatically scrolls down the list using color detection to find the scroll bar.
- Saves all scraped data in a CSV file (`followers.csv`).

## Requirements

### Hardware

- **Desktop Environment:** Since the script uses `PyAutoGUI` to automate scrolling, it requires a full desktop environment with graphical access.

### Software Dependencies

- **Python version:** Python 3.8 or higher is required.
- **Required Python packages:** The following Python libraries are needed for this script to function properly:

    - `Playwright`: For browser automation.
    - `PyAutoGUI`: For simulating user actions like scrolling and clicking.
    - `Numpy`: For processing screenshots.
    - `Asyncio`: For handling asynchronous tasks.

## Installation

1. **Clone the repository:**

    Clone the repository or download the Python script to your local environment.

    ```bash
    git clone https://github.com/xaviermorgan9/shitty-twitter-list-scraper-using-pyautogui
    ```

2. **Install dependencies:**

    Use the provided `requirements.txt` to install all necessary libraries:

    ```bash
    pip install -r requirements.txt
    ```

3. **Install Playwright browsers:**

    After installing Playwright, run this command to install the required browser binaries:

    ```bash
    playwright install
    ```

## How to Use

1. **Run the script:**

    Execute the main script using Python:

    ```bash
    python twitter-list-scraper.py
    ```

2. **Log in to Twitter:**

    A browser window will open, and you will be prompted to manually log in to your Twitter account. The script waits until login is successful.

3. **Start scraping:**

    After login, the script will automatically start scraping follower details from the provided Twitter list URL. It scrolls down to load more followers and stores their details in a CSV file (`followers.csv`).

4. **CSV Output:**

    The output CSV file will contain the following columns:

    - `Username`
    - `Nickname`
    - `Bio`
    - `Emails` (1/100 attempts will get email)
    - `Join Date`

5. **Stop the script:**

    You can stop the script anytime by closing the terminal or interrupting the Python process. The CSV file will contain all scraped data up to that point.

## Configuration

- **Twitter List URL:** Update the `twitter_list_url` variable in the script to scrape a different Twitter list.
- **CSV File:** You can modify the output CSV file name or location by changing the file handling code inside the `process_queue` function.

## Limitations

- **Manual Twitter login:** The script requires manual login to Twitter because automatic login via credentials is restricted by Twitter.
- **Scroll area detection:** The scroll detection relies on specific colors (`#3E4144`) for Twitter’s scrollbar. If Twitter’s design changes, this may need to be adjusted.
