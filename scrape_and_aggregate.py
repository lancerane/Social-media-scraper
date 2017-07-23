def scrape_and_aggregate(domains):

    from bs4 import BeautifulSoup
    import urllib.request
    # import requests
    import socialshares
    import pandas as pd

    # Try to convert each url into a html document
    urls = []
    inaccessible = []
    for domain in domains:
        try:
            with urllib.request.urlopen(domain) as response:
               html = response.read()
        except:
            inaccessible.append(domain)
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
    dct = {'URL':[], 'Facebook':[], 'Pinterest':[], 'Google':[], 'Linkedin':[]}

    for url in urls:
        # Find any '//' after http:// and convert to '/'
        idx = url.find('/')
        cleaned_url = url[:idx+1] + url[idx+1:].replace('//', '/')

        try:
            counts = socialshares.fetch(cleaned_url, ['facebook', 'pinterest', 'google', 'linkedin']) # can also query reddit, but unreliable

        # If no data, skip that url
        except TypeError:
            continue

        dct['URL'].append(cleaned_url)

        # try:
        #     header = requests.head(cleaned_url).headers
        #     dct['Modified date'].append(header['Last-Modified'])
        # except:
        #     dct['Modified date'].append('n/a')

        if 'facebook' in counts:
            dct['Facebook'].append(counts['facebook']['share_count'])
        else:
            dct['Facebook'].append('n/a')
        if 'pinterest' in counts:
            dct['Pinterest'].append(counts['pinterest'])
        else:
            dct['Pinterest'].append('n/a')
        if 'google' in counts:
            dct['Google'].append(counts['google'])
        else:
            dct['Google'].append('n/a')
        if 'linkedin' in counts:
            dct['Linkedin'].append(counts['linkedin'])
        else:
            dct['Linkedin'].append('n/a')

    dataframe = pd.DataFrame(dct)
    dataframe = dataframe.set_index('URL').reset_index()

    return dataframe, inaccessible
