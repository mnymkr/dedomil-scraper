import re
import requests
import os
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from bs4 import BeautifulSoup
import threading
import argparse

lock = threading.Lock()

MAX_THREADS = 20
JAR_DIR = "jar"

def has_exact_k800i(html_text):
    """Return True if 'K800i' appears standalone, not as 'CZ/K800i' etc."""
    return re.search(r'(?<![A-Za-z0-9/])K800i(?![A-Za-z0-9/])', html_text) is not None

def download_jar(jar_url):
    filename = jar_url.split("/")[-1] + ".jar"
    os.makedirs(JAR_DIR, exist_ok=True)
    filepath = os.path.join(JAR_DIR, filename)

    try:
        resp = requests.get(
            jar_url,
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; rv:128.0) Gecko/20100101 Firefox/128.0"},
            timeout=10
        )
        if resp.status_code == 200:
            with open(filepath, "wb") as f:
                f.write(resp.content)
            print(f"Downloaded: {filename}")
            return True
        else:
            print(f"Failed to download {filename} (status {resp.status_code})")
    except Exception as e:
        print(f"Error downloading {filename}: {e}")
    return False

def scrape_game(game_id):
    print(f"Scraping game ID: {game_id}")
    url = f"http://dedomil.net/games/{game_id}/screen/8"

    try:
        resp = requests.get(
            url,
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; rv:128.0) Gecko/20100101 Firefox/128.0"},
            timeout=60
        )
        if resp.status_code != 200:
            print(f"Scraping failed for game ID {game_id} (status {resp.status_code})")
            return f"{game_id}: nay (error)"

        html = resp.text
        soup = BeautifulSoup(html, "html.parser")

        # First try exact K800i
        if has_exact_k800i(html):
            print(f"Exact K800i reference found for {game_id}")
            jar_link_tag = soup.find("a", href=re.compile(r"/download-jar/"))
            if jar_link_tag:
                jar_link = "http://dedomil.net" + jar_link_tag["href"]
                if download_jar(jar_link):
                    return f"{game_id}: yay"
                else:
                    return f"{game_id}: nay (download failed)"
            else:
                print(f"No .jar link found for {game_id}")
                return f"{game_id}: nay (no downloads found)"

        # Fallback: largest available version
        print(f"No valid K800i reference for {game_id} — trying largest available version...")
        jar_links = []
        for load_div in soup.find_all("div", class_="LOAD"):
            jar_a = load_div.find("a", href=re.compile(r"/download-jar/"))
            if not jar_a:
                continue
            size_text = load_div.get_text(strip=True)
            size_match = re.search(r"(\d+(?:\.\d+)?)\s*(kB|MB)", size_text, re.IGNORECASE)
            if size_match:
                size_value = float(size_match.group(1))
                if size_match.group(2).lower() == "mb":
                    size_value *= 1024
                jar_links.append((size_value, "http://dedomil.net" + jar_a["href"]))

        if jar_links:
            largest_link = max(jar_links, key=lambda x: x[0])[1]
            if download_jar(largest_link):
                return f"{game_id}: yay (largest available)"
            else:
                return f"{game_id}: nay (download failed)"
        else:
            print(f"No working .jar for {game_id}")
            return f"{game_id}: nay (no working .jar)"

    except Exception as e:
        print(f"Error scraping game ID {game_id}: {e}")
        return f"{game_id}: nay (error), {e}"

def get_failed_ids_from_log(logfile):
    failed_ids = []
    with open(logfile, "r") as f:
        for line in f:
            # Ignore specific "no working .jar" and "no downloads found" cases
            if "nay (no working .jar)" in line or "nay (no downloads found)" in line:
                continue
            match = re.match(r"(\d+): nay", line)
            if match:
                failed_ids.append(int(match.group(1)))
    return failed_ids

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--retry", action="store_true", help="Retry failed downloads from a log file")
    args = parser.parse_args()

    if args.retry:
        log_file = input("Enter the log file path: ").strip()
        game_ids = get_failed_ids_from_log(log_file)
    else:
        start = int(input("Enter start game ID: "))
        end = int(input("Enter end game ID: "))
        game_ids = list(range(start, end + 1))

    total = len(game_ids)
    log_entries = []

    with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        for result in executor.map(scrape_game, game_ids):
            with lock:
                log_entries.append(result)

    # Write log
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    range_str = f"{game_ids[0]}-{game_ids[-1]}"
    log_filename = f"{timestamp}_{range_str}.log"
    with open(log_filename, "w") as f:
        f.write(f"Total tried: {total}\n")
        f.write(f"Total successful: {sum(1 for e in log_entries if ': yay' in e)}\n")
        f.write("\n".join(log_entries))
    print(f"Log saved to {log_filename}")

if __name__ == "__main__":
    main()
