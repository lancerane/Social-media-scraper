from bs4 import BeautifulSoup
import urllib.request
import socialshares
import pandas as pd

# Enter list of domains to be scraped
domains = ['http://www.peoplesmomentum.com/','https://fullfact.org/' ]

# Enter a path to save final CSV file to
filename = 'test.csv'

# Try to convert each url into a html document
names=[]
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
        names.append(link.get('href'))

urls = [name for name in names if name.startswith('http')]

# Run each url through SM apis to get share counts. Collect in a dictionary
dct = {'url':[], 'facebook':[], 'pinterest':[], 'google':[], 'reddit ups':[], 'reddit downs':[], 'linkedin':[]}

for url in urls:
    counts = socialshares.fetch(url, ['facebook', 'pinterest', 'google', 'reddit', 'linkedin'])

    dct['url'].append(url)
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
