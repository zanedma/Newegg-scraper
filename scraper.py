import base64
from email.mime.text import MIMEText
import pickle
import os.path
import time
import sys
import requests
from bs4 import BeautifulSoup
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

SCOPES = ['https://www.googleapis.com/auth/gmail.send']

def establish_gmail_service():
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    return build('gmail', 'v1', credentials=creds)


def get_html(url: str)->bytes:
    print(f'[scraper] checking {url}')
    resp = requests.get(url)
    return resp.status_code, resp.content


def check_stock(content: bytes)->bool:
    soup = BeautifulSoup(content, 'html.parser')
    found = soup.findAll('div', {'class': 'product-inventory'})
    if len(found) <= 0: return False
    for div in found:
        if "In stock." in div.contents[0]: return True
    return False


def notify(link: str, email: str, service)->None:
    msg_text = 'The following product is in stock: ' + link
    msg = MIMEText(msg_text)
    msg['to'] = email
    msg['from'] = email
    msg['subject'] = '[Newegg Scraper] An item is in stock'
    raw_message = base64.urlsafe_b64encode(msg.as_bytes())
    to_send = {'raw': raw_message.decode()}
    try:
        response = service.users().messages().send(userId='me', body=to_send).execute()
    except Exception as error:
        print(error)
        print('[scraper] error sending notification')
        return
    if response is None:
        print("This")
        print('[scraper] error sending notification')
    else:
        print('[scraper] successfully sent notification')


if __name__ == "__main__":
    email = sys.argv[1]
    links = sys.argv[2:]
    service = establish_gmail_service()
    assert len(links) > 0, "Must provide at least 1 link"
    while True:
        for link in links:
            status, content = get_html(link)
            if status != 200:
                print(f'[scraper] received status {status}')
                continue
            if check_stock(content):
                print('[scraper] product is in stock')
                notify(link, '', service)
            else:
                print('[scraper] product is out of stock')
        time.sleep(60)