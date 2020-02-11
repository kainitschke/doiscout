def general_search_livivo(browser, studyID, max_results = 100):
    from definitions import open_page

    # open livivo in selenium
    mainlink        = "https://www.livivo.de/"
    browser         = open_page(browser, mainlink)

    dois            = list()

    # search in browser the studyID
    search_livivo(browser, studyID)

    # extract the results information
    extract_search_results_livivo(browser, dois)

    # repeat until all results crawled
    counter         = 1 + 10
    oldlength       = 0
    while (oldlength != len(dois)) & (len(dois) <= max_results) & (len(dois)>=10):
        # length of doi compare
        oldlength   = len(dois)
        # open next result page
        next_page_livivo(browser, counter)
        # extract dois/titles
        extract_search_results_livivo(browser, dois)
        # up the counter
        counter = counter + 10

    # return dois/titles
    return dois[0:max_results], browser

def search_livivo(browser, input):
    # enters the search term and presses enter
    # livivo has to be opened
    from selenium.webdriver.common.keys import Keys
    # find search field
    search_field    = browser.find_element_by_css_selector("#nsearch > input:nth-child(1)")
    # delete input from earlier
    search_field.send_keys(Keys.CONTROL + "a")
    search_field.send_keys(Keys.BACK_SPACE)
    # input study id
    search_field.send_keys('"' + input + '"')
    search_field.send_keys(Keys.ENTER)

    initial_wait(browser)

def initial_wait(browser):
    # gets the 100 results per page and waits for loading
    object          = "#hits_per_page > option:nth-child(5)"
    suc             = wait_for_object(browser, object)
    #if suc == True:
    #    oldpage     = browser.page_source
    #    browser.find_element_by_css_selector(object).click()
    #    wait_for_change(browser, oldpage)

def wait_for_object(browser, object):
    # wait for object to be ready (or no hits)
    from time import sleep
    while True:
        try:
            # check whether no results; then infinity loop
            site    = browser.page_source
            if (site.find("keine Ergebnisse") > -1)|(site.find("no hits") > -1):
                return False
            # check if object available
            browser.find_element_by_css_selector(object)
            return True
        except: sleep(.1)

def wait_for_change(browser, oldpage):
    from time import sleep
    newpage     = browser.page_source
    while oldpage == newpage:
        sleep(.3)
        newpage = browser.page_source

def next_page_livivo(browser, counter):
    from definitions import open_page
    #next_object = ".intro > nav:nth-child(3) > ul:nth-child(2) > li:nth-child(7) > a:nth-child(1)"
    sublink     = "https://www.livivo.de/app/search/search?liststart=" + str(counter) #+ "&dbid=ASP3_ALL"
    oldpage     = browser.page_source
    open_page(browser, sublink)
    wait_for_change(browser, oldpage)
    #try:
    #    browser.find_element_by_css_selector(next_object)
        #wait_for_object(browser, next_object)
    #    oldpage     = browser.page_source
    #    browser.find_element_by_css_selector(next_object).click()
    #    wait_for_change(browser, oldpage)
    #    return True
    #except:
    #    return False

def extract_search_results_livivo(browser, dois):
    # crawls site for the search results

    site            = browser.page_source
    start           = site.find("<body")
    start           = site.find("<main",    start)
    start           = site.find("<section", start)
    #start           = site.find("<ol",      start)
    #end             = site.find("</ol>",    start)
    end             = site.find("</main>", start)
    snipped         = site[start:end]

    start           = snipped.find("<article")
    startn          = snipped.find("<article", start + 1)   # next; the one after
    if startn == -1: startn = len(snipped)                  # correction for last one
    while start > -1:
        startt      = snipped.find("data-doi",start)  # for doi
        startg      = snipped.find("<header", start)  # for title
        startg      = snipped.find("<h3",     startg)

        ## doi
        if (startt > -1)&(startt < startn):     # found doi
            startt  = snipped.find('10.',startt)
            end     = snipped.find('"', startt)
        else:               # no doi, so we take the title instead
            startt  = snipped.find("title",  startg)
            startt  = snipped.find('"',      startt) + 1
            end     = snipped.find('"', startt)

        dois.append(snipped[startt:end])

        start       = snipped.find("<article", end + 1)
        startn      = snipped.find("<article", start + 1)   # next; the one after
        if startn==-1: startn = len(snipped)                # correction for last one