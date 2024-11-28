import socket
import sys
import mariadb
import requests
import json
from datetime import datetime
from urllib3.exceptions import InsecureRequestWarning
from subprocess import Popen

s = socket.socket()
host = socket.gethostname()
port = 2000
s.bind((host, port))
    
try:
    conn = mariadb.connect(
        user="StatsSiteBatchJobs",
        password="UUo**wF4%Xb7cTuSY88@6Xu@!",
        host="192.168.3.1",
        port=13306,
        database="WarThunder"

    )
except mariadb.Error as e:
    print(f"Error connecting to MariaDB Platform: {e}")
    sys.exit(1)

# Get Cursor
cur = conn.cursor(dictionary=True)

# Pull token information row if any tokens with more than 5 minutes left exist
cur.execute("SELECT * FROM WarThunder.AccessToken WHERE WarThunder.AccessToken.LastRefresh > TIMESTAMPADD(MINUTE, 5, NOW()) LIMIT 1")

results = cur.fetchall()

if not results:
    # Stop Python from warning about the certificate on ip 185.253.20.200
    requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

    # Set credentials and the users to search for
    email = 'wt-web-scraped@gmail.com'
    password = 'abcd1234'

    # Call suspicious endpoint to get a login token
    url = 'https://185.253.20.200/login.php'
    data = {'client': 'win_72ba0e93-a10f-421b-8a6b-16dc182652d5','game': 'wt','gapp_id': '79','login': email,'meta': '1','password': password,'v': '2'}
    loginInformationResponse = requests.post(url, data=data, verify=False)

    # Pull the login token and user id into seperate variables
    loginInformation = json.loads(loginInformationResponse.content)
    token = loginInformation['jwt']
    uidHint = loginInformation['user_id']
    
    cur.execute("INSERT INTO WarThunder.AccessToken (Token, UidHint) VALUES (?, ?)",(token, uidHint))
    
    now = datetime.now()
    iso_date = now.isoformat()
    print(iso_date, f"- requested new token, inserted as ID: {cur.lastrowid}")
    cur.execute("DELETE FROM WarThunder.AccessToken WHERE WarThunder.AccessToken.LastRefresh < TIMESTAMPADD(MINUTE, 5, NOW())")
    conn.commit()