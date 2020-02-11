def general_search_base_search(http, studyID, max_results = 100):
    from random import randint
    from time   import sleep

    mainlink        = 'https://www.base-search.net/Search/Results?lookfor='

    dois            = list()
    urls            = list()

    results_pp      = 10        # the results per page

    page            = 1
    oldlength       = -1
    while (len(dois)<max_results) & (len(dois) > oldlength) & ((len(dois) % results_pp) == 0):
        oldlength   = len(dois)

        sublink     = mainlink + '"' + studyID + '"' + "&page=" + str(page)
        site        = http.request("GET", sublink).data.decode("utf-8", "ignore")

        # look whether too many searches from ip
        if site.find("viele Suchanfragen von Ihrer IP-Adresse") > -1:
            1 / 0       # provokes error; is caught in the function above

        # extracts results
        if (site.find("No documents found.") == -1) & (site.find("Keine zu Ihrer Anfrage passenden Dokumente gefunden.") == -1): # if there are any
            extract_results_base_search(site, dois, urls)

        page        = page + 1

        sleep(randint(2, 5))  # waits a random time to throw off their algorithm

    return dois, urls

def extract_results_base_search(site, dois, urls):
    # extracts the entries from http.requested data
    from definitions import is_doi, string_2_html
    start               = site.find("ResultsBox")
    end                 = site.find("</form", start)
    snipped             = site[start : end]

    start               = snipped.find('"Results"')
    startn              = snipped.find('Datenlieferant', start + 1)
    if startn == -1: startn = len(snipped)
    while start > -1:
        subsnipped      = snipped[start : startn]
        adoi            = ""
        aurl            = ""

        # search through urls; also for dois
        starturl        = subsnipped.find('>URL:<')
        starturl        = subsnipped.find("href=", starturl)
        while starturl > -1:
            # get url

            starturl    = subsnipped.find('"',     starturl) + 1
            endurl      = subsnipped.find('"',     starturl)
            aurl        = subsnipped[starturl : endurl]

            # get doi from url
            startdoi    = aurl.find("doi")
            if startdoi > -1:
                startdoi= aurl.find("10.", startdoi)
                adoi    = aurl[startdoi : len(aurl)]
                break

            #starturl    = subsnipped.find('"http"', starturl + 1)
            starturl = subsnipped.find("href=", starturl)

        if aurl == "":
            a = 1

        urls.append(aurl)
        if is_doi(adoi):
            dois.append(adoi)
        else:               # there is no doi; search for title
            starttitle  = subsnipped.find("Titel:")
            starttitle  = subsnipped.find(">", starttitle)
            starttitle  = subsnipped.find(">", starttitle + 1) + 1
            endtitle    = subsnipped.find("<", starttitle)
            title       = string_2_html(subsnipped[starttitle : endtitle], direction = "from_html")
            dois.append(title)

        start           = snipped.find('"Results"', startn + 1)
        startn          = snipped.find('Datenlieferant', start + 1)
        if startn == -1: startn = len(snipped)