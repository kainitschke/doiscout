
def google_scholar_is_empty_search_site(site):
    start       = site.find('<div id="gs_res_ccl_mid"')
    start       = site.find('>', start)
    end         = site.find("</div", start)
    if (end - start) < 20:
        return True
    else:
        return False

#####################################################################
################## General Search ###################################
#####################################################################
def google_scholar_general_search(browser, search_string, timestamp, mail_add="", max_results=300):
    # searches google scholar for a specified string
    # crawls through all pages until no more results, or max_results is reached
    # function return the links of the results

    main_site   = "https://scholar.google.de/scholar?start="
    stepper     = 10

    links       = list()

    page        = 0
    sublink     = main_site + str(page) + "&q=" + search_string
    open_despite_recaptcha(browser, sublink, timestamp, mail_add)

    while (google_scholar_is_empty_search_site(browser.page_source) == False) & ((page) <= max_results):          # are there any more results at all & # are we above max_results

        links   = links + google_scholar_general_search_results_links(browser.page_source)

        # call next google scholar result site
        page    = page + stepper
        sublink = main_site + str(page) + "&q=" + search_string
        open_despite_recaptcha(browser, sublink, timestamp, mail_add)

    if len(links) > max_results: links = links[0:max_results] # if too many results extracted, cut the rest

    return links

def google_scholar_general_search_results_links(site):
    # gets the 10 search results of a google scholar page
    # extracts and returns the links of the main results
    links                   = list()

    start                   = site.find('<div id="gs_res_ccl_mid"')
    start                   = site.find('>', start)
    end                     = len(site)
    snipped                 = site[start:end]

    start                   = snipped.find("gs_rt")
    end                     = snipped.find("</div", start)
    subsnipped              = snipped[start : end]

    while (start > -1) & (end > -1):
        # find interesting part

        if (subsnipped.find("[ZITATION]") > -1) | (subsnipped.find("[CITATION]") > -1):   # crawl title of citation
            crawl           = "citation"
        elif subsnipped.find("href") > -1:                                  # link crawling
            crawl           = "url"
        else:                                                               # website crawling
            crawl           = "citation"


        if crawl == "citation":
            # website crawling
            title_start = subsnipped.find("gs_ctu")
            title_end = subsnipped.find("</h3", title_start)

            # the following is necessary, because there are multiple </span> but we are only interested in the very last one, before </h3
            weg = subsnipped.find("</span>", title_start)
            while (weg < title_end) & (weg > -1):
                title_start = weg + len("</span>")
                weg = subsnipped.find("</span>", title_start)

            authors_start = subsnipped.find("<div", title_end)
            authors_start = subsnipped.find(">", authors_start) + 1
            authors_end = len(subsnipped)

            # tidy up
            title = (clear_not_link_entry(
                subsnipped[title_start:title_end])).strip()  # strip deletes spaces at start and end
            authors = (clear_not_link_entry(subsnipped[authors_start:authors_end])).strip()

            # add to collection
            links.append(title + "/////" + authors)

        elif crawl == "url":
            # link crawling
            substart = subsnipped.find("href")
            substart = subsnipped.find('"', substart) + 1
            subend = subsnipped.find('"', substart)

            # add to collection
            links.append(subsnipped[substart:subend])


        # next entry
        start           = snipped.find("gs_rt", end + 1)
        end             = snipped.find("</div", start)
        subsnipped      = snipped[start : end]
    return links

def clear_not_link_entry(string):
    # function clear html and weird signs from strings obtained from google scholar
    # clear html props
    start           = string.find("<")
    end             = string.find(">", start)
    while start > -1:
        string      = string[0:start] + string[end + 1 : len(string)] # cut everything in between
        start       = string.find("<")
        end         = string.find(">", start)

    # find other curious signs
    start           = string.find("&#")
    end             = string.find(";", start)
    while start > -1:
        string      = string[0:start] + string[end: len(string)]  # cut everything in between
        start       = string.find("&#")
        end         = string.find(";", start)

    return string

#####################################################################
################## Search DOIs on sites #############################
#####################################################################

def gs_identify_dois_on_html(browser, http, links):
    from definitions    import find_earliest_end, is_link, is_doi, open_page
    from pubmed_plugins import titles_2_dois_by_pubmed

    dois            = list()
    urls            = list()

    for i in range(0, len(links)):
        #print(links[i])
        if is_link(links[i]) == True:

            if links[i].find("print") == -1: # tries to catch print commands

                # http request
                try:                # http request produces error for some site (i.e. nature)
                    site        = http.request("GET", links[i]).data.decode("utf-8", "ignore")
                    start       = site.find("doi")
                    if start == -1:
                        start   = site.find("DOI")
                except:             # so if error, here start as -1 so selenium is called in the step later
                    start       = -1

                # selenium (if http request failed)
                if start  == -1:    # if http not working, try selenium, sometimes helpful
                    try:
                        open_page(browser, links[i])
                        site    = browser.page_source
                        start   = site.find("doi")
                        if start == -1:
                            start = site.find("DOI")
                    except: pass
                # find doi
                try:
                    start       = site.find("10.", start)
                    end         = find_earliest_end(site, start, einschluss=["&","="])
                    adoi        = site[start:end]
                    if adoi[-1] == ")": adoi = adoi[0:-1]
                except:
                    adoi        = " "

            else:
                adoi            = " "

        else: # no link --> look up title in pubmed; extremely unlikely to find anything because google scholar cuts titles so there will not be a full match
            trenner         = links[i].find("/////")
            adoi            = titles_2_dois_by_pubmed(links[i][0:trenner], http)

        #print(adoi)
        if is_doi(adoi):                    # were we able to find the doi
            urls.append(links[i])
            dois.append(adoi)
        else:                               # no doi was found
            if is_link(links[i]):           # was there an initial link
                urls.append(links[i])
                dois.append(" ")
            else:                           # just title and was not able to get anything from this
                dois.append(links[i])
                urls.append(" ")

    return dois, urls


#####################################################################
################## Anti-Captcha #####################################
#####################################################################

def open_despite_recaptcha(browser, url, timestamp, mail_add):
    # opens url in selenium
    # catches the case if there is a captcha; waits until user answered to it
    # if there is none, the page is just opened, linke browser.get() would
    # info mail is sent
    from time import sleep
    from definitions import open_page
    open_page(browser, url)
    if is_captcha(browser):
        from mail_defs import mail_captcha
        mail_captcha(mail_add, timestamp)
    while is_captcha(browser):
        sleep(1)

def is_captcha(browser):
    # detects captcha
    if browser.page_source.find("captcha") > -1:
        return True
    else:
        return False
    