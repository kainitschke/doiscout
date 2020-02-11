def general_search_ub_fr(http, studyID, max_results=100):
    # main function. searches in university library Freiburg
    
    dois            = list()
    urls            = list()

    page            = 1
    limit           = 50
    type            = "tx"

    oldlength       = -1
    while (len(urls)<max_results) & (oldlength < len(urls)) & ((len(urls) % limit) == 0): # last bit is necessary, because UB Freiburg relists items if there is nothing more
        oldlength   = len(urls)
        site        = open_ub_fr(http, studyID, page, limit, type)
        extract_urls_ub_fr(site, urls)
        page        = page + 1

    urls            = urls[0: max_results]

    # gets the dois or titles for the extracted urls
    for i in range(0, len(urls)):
        extract_dois_from_urls_from_ub_fr(http, urls[i], dois)

    return dois, urls

def open_ub_fr(http, studyID, page, limit, type):
    # opens the first/next page in the UB Freiburg Search

    mainlink    = "https://katalog.ub.uni-freiburg.de/opac/RDSProxy/Search?lookfor="
    sublink     = mainlink + '"' + studyID + '"' + "&type=" + type + "&limit=" + str(limit) + "&page=" + str(page)

    site        = http.request("GET", sublink).data.decode("utf-8", "ignore")
    return site

def extract_urls_ub_fr(site, urls):
    # gets the urls to the single entries from a search
    start       = site.find("<body")
    start       = site.find('"contentWrapper"', start)
    start       = site.find('"container"', start)
    start       = site.find('"row"', start)
    start       = site.find('"results-listing', start)
    start       = site.find('result-items', start)
    end         = site.find("</form>", start)
    snipped     = site[start : end]

    start       = snipped.find('id="result')
    startn      = snipped.find('id="result', start + 1)
    if startn == -1: startn = len(snipped)

    while start > -1:
        start   = snipped.find('"media-body"', start)
        #start   = snipped.find('title getFull', start)
        start   = snipped.find("href=", start)
        start   = snipped.find('"', start) + 1
        end     = snipped.find('"', start)

        urls.append("https://katalog.ub.uni-freiburg.de" + snipped[start : end])

        start   = snipped.find('id="result', end)
        startn  = snipped.find('id="result', start + 1)
        if startn == -1: startn = len(snipped)

def extract_dois_from_urls_from_ub_fr(http, url, dois):
    # gets single result site of UB Freiburg and extracts the doi

    site        = http.request("GET", url).data.decode("utf-8", "ignore")

    start       = site.find("body")
    start       = site.find('"contentWrapper"', start)
    start       = site.find('"container"', start)
    startd      = site.find('DOI', start)
    if startd > -1:
        from definitions import find_earliest_end
        startd  = site.find('href=', startd)
        startd  = site.find('>', startd)
        startd  = site.find("10.", startd)
        end     = find_earliest_end(site, startd, einschluss=["<", "%"])

        dois.append(site[startd : end])

    else:
        startt  = site.find("RDS_TITLE", start)
        startt  = site.find(">", startt) + 1
        startt  = site.find(">", startt) + 1
        startt  = site.find(">",  startt) + 1
        end     = site.find("<", startt)

        title   = site[startt: end]
        title   = title.replace("\n", "")
        title   = title.strip()

        dois.append(title)