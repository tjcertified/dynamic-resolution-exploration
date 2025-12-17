import requests
import ntplib
import json
from datetime import datetime, timezone, timedelta

# This block of code generates 10 TDN DGA URLs by using the current UTC time 
# from an established ntp server, then normalizing that time to midnight and
# creating a span of 5 days prior to today. Using this start and end date, the
# algorithm makes an API request to stackexchange.com, asking for all posts 
# between those dates made on stackoverflow.com, ordered by number of votes, 
# descending. The first ID in the list is then used to establish which domain 
# in the list of "acceptable" domains to start with, and which length between 9
# and 15 to start with. Then, the algorithm filters the list for the first 10
# "question" posts it finds (rather than "answers"), and requests the full text
# of those 10 posts. Using that retrieved text, the DGA grabs a number of 
# characters up to the starting length established earlier that are either
# consonants or numbers, skipping the first few characters because these are 
# always the html <p> tag and decrease variability. After generating a URL from
# this string and the currently selected "acceptable" domain, the domain index
# is updated, and the current length is updated to again increase entropy in
# the output, hopefully making the domain harder to find by being variable
# length and variable "ending" domain.
# 
# While this is reliably repeatable in clients, it is NON-DETERMINISTIC because
# it relies on non-knowable public data, due to the "order by votes" mechanism
# (unless the algorithm seed is discovered, but even then, ordering can introduce
# unpredictable components).

# establish constants
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
from_date = to_date - timedelta(days=10)

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
    fb_port = 0

    # Dynamically generate port to connect to based on letters in URL
    # by adding ascii numeric value of first 5 characters
    for ch in range(5):
        fb_port += ord(filtered_body[ch])
        
    
    dga_strings.append(filtered_body + ACCEPTABLE_DGA_DOMAINS[starting_domain_index] + ":" + str(fb_port))
    # Update to the next appropriate index in the domain ending list
    starting_domain_index +=1
    starting_domain_index %= len(ACCEPTABLE_DGA_DOMAINS)

print("First 10 DGA urls with dynamic port:")
print("------------------")
for url in dga_strings:
    print(url)
