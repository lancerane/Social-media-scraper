import urllib.request
import socialshares
import pandas as pd
import IPython
from bs4 import BeautifulSoup

# Enter list of domains to be scraped
domains = [ 'http://markcurtis.info/', 'http://medialens.org/' ]

# Enter a path to save final CSV file to
filename = 'test.csv'

# Try to convert each url into a html document
urls = []
for domain in domains:
    try:
        with urllib.request.urlopen(domain) as response:
           html = response.read()
    except:
        print('unable to parse %s' % domain)
        continue

    soup = BeautifulSoup(html,'html.parser')

    # Get a list of urls from the domain
    for link in soup.find_all('a'):
        url = link.get('href')

        # For internal links, prepend the domain address
        try:
            if url.startswith('http'):
                urls.append(url)
        
            elif url.startswith('/http'):
                urls.append(url[1:])
            else:
                urls.append(domain + url)

        # If the url is empty, skip it
        except AttributeError:
            continue

# Run each url through SM apis to get share counts. Collect in a dictionary
dct = {'url':[], 'facebook':[], 'pinterest':[], 'google':[], 'reddit ups':[], 'reddit downs':[], 'linkedin':[]}

for url in urls:
    # Find any '//' after http:// and convert to '/'
    idx = url.find('/')
    cleaned_url = url[:idx+1] + url[idx+1:].replace('//', '/')
    try:
        counts = socialshares.fetch(cleaned_url, ['facebook', 'pinterest', 'google', 'reddit', 'linkedin'])
        
    # If no data, skip that url
    except TypeError:
        continue

    dct['url'].append(cleaned_url)
    if 'facebook' in counts:
        dct['facebook'].append(counts['facebook']['share_count'])
    else:
        dct['facebook'].append('na')
    dct['pinterest'].append(counts['pinterest'])
    dct['google'].append(counts['google'])
    dct['reddit ups'].append(counts['reddit']['ups'])
    dct['reddit downs'].append(counts['reddit']['downs'])
    dct['linkedin'].append(counts['linkedin'])

# Convert to CSV and save

dataframe = pd.DataFrame(dct)
dataframe = dataframe.set_index('url').reset_index()
dataframe.to_csv(filename, index=False)
