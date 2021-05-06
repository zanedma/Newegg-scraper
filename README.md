# Newegg-scraper
Bot that checks Newegg's stock and notifies the user via email if specified item(s) are available

# Requirements
* Python 3
* Google API python client
  * pip3 install --upgrade google-api-python-client
  * pip install --upgrade google-api-python-client
* BeautifulSoup 4
  * pip install beautifulsoup4
  
 # Usage
 `python scraper.py <email> <link1> <link2>...`
 
 Where:
 * `email` is the email address to send in stock notifications
 * `link1 - linkn` are links to Newegg product pages to check if they are in stock
