def scrape_and_aggregate(domains):

    from bs4 import BeautifulSoup
    import urllib.request
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
    dct = {'URL':[], 'facebook':[], 'pinterest':[], 'google':[], 'linkedin':[]}

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
        if 'facebook' in counts:
            dct['facebook'].append(counts['facebook']['share_count'])
        else:
            dct['facebook'].append('na')
        if 'pinterest' in counts:
            dct['pinterest'].append(counts['pinterest'])
        else:
            dct['pinterest'].append('na')
        if 'google' in counts:
            dct['google'].append(counts['google'])
        else:
            dct['google'].append('na')
        if 'linkedin' in counts:
            dct['linkedin'].append(counts['linkedin'])
        else:
            dct['linkedin'].append('na')

    dataframe = pd.DataFrame(dct)
    dataframe = dataframe.set_index('URL').reset_index()

    return dataframe, inaccessible
