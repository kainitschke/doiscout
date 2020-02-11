def general_search_wos(browser, http, studyID, max_results=100, search_tag="Topic", pubmed = True):
    from pubmed_plugins import identify_correct_pmid, search_pubmed_for_pmids
    from definitions    import is_doi

    dois        = list()
    urls        = list()

    # Search in WOS
    browser     = establish_new_session(browser)
    search_in_wos(browser, studyID, search_tag)

    site        = browser.page_source
    extract_urls_wos(site, dois, urls)

    while (len(dois)<max_results) & ((len(dois)%10)==0) & (len(dois)>0):
        next_page_wos(browser)
        site    = browser.page_source
        extract_urls_wos(site, dois, urls)

    dois        = dois[0:max_results]
    urls        = urls[0:max_results]

    # Lookup information found; is here because first try in pubmed; second again wos

    if pubmed == True:
        for i in range(0, len(dois)):
            follow_wos          = 0
            pmids               = search_pubmed_for_pmids("title", dois[i], http, 20)
            bib_info            = identify_correct_pmid(http, pmids, dois[i], "title")
            if bib_info != list():
                if is_doi(bib_info[0]):
                    dois[i]     = bib_info[0]
                else:
                    follow_wos  = 1
            else:
                follow_wos      = 1

            if follow_wos == 1:     # pubmed was not satisfactory
                dois[i]         = get_doi_from_wos(browser, urls[i])

        return dois, browser

    else:
        return urls, browser

def establish_new_session(browser):
    # opens WebOfKnowledge; looks whether establish new session is necessary
    from definitions import open_page

    mainlink    = "https://www.webofknowledge.com/"
    browser     = open_page(browser, mainlink, allow_restart=True)

    site        = browser.page_source
    if site.find('Establish new session') > -1:
        a = 1
        print("ESTABLISH NEW SESSION")
    return browser

def get_doi_from_wos(browser, url):
    from definitions import find_earliest_end, open_page
    open_page(browser, url, allow_restart=False)
    site        = browser.page_source

    start       = site.find("10.")
    end         = find_earliest_end(site, start, einschluss=["<", '"'])
    doi         = site[start : end]

    return doi

def search_in_wos(browser, studyID, search_tag):
    from selenium.webdriver.common.keys import Keys
    # select all databases
    browser.find_element_by_css_selector('#select2-databases-container').click()
    find_element_all_databases(browser)

    # set as topic
    browser.find_element_by_css_selector("#select2-select1-container").click()
    find_element_search_tag(browser, search_tag)

    # delete and insert into Search Field
    search_field     = browser.find_element_by_css_selector("#value\(input1\)")
    search_field.send_keys(Keys.CONTROL + "a")
    search_field.send_keys(Keys.BACK_SPACE)
    search_field.send_keys('"' + studyID + '"')

    # press search button
    find_search_button(browser)

    try:
        obj     = "div.paginationBar:nth-child(2) > div:nth-child(4) > div:nth-child(1) > div:nth-child(2) > div:nth-child(1) > form:nth-child(1) > div:nth-child(7) > li:nth-child(5)"
        browser.find_element_by_css_selector(obj).click()
    except: pass

def extract_urls_wos(site, dois, urls):
    # gets the search results on wos in this page

    start           = site.find("<body")
    start           = site.find('main-container',           start)
    start           = site.find('NEWsummaryPage',           start)
    start           = site.find('NEWsummaryDataContainer',  start)
    start           = site.find('l-wrapper-row',            start)
    start           = site.find('l-column-content',         start)
    start           = site.find('l-content',                start)
    start           = site.find('"summary_records_form"',   start)
    start           = site.find('summaryRecordsTable',      start)
    start           = site.find('records_chunks',           start)
    start           = site.find('search-results',           start)
    end             = len(site)
    snipped         = site[start : end]

    start           = snipped.find('id="RECORD')
    while start > -1:
        start       = snipped.find("search-results-content", start)
        start       = snipped.find("href=", start)
        start       = snipped.find('"', start) + 1
        end         = snipped.find('"', start)

        url         = snipped[start:end]
        url         = url.replace("&amp;", "&")
        urls.append("https://apps.webofknowledge.com" + url)

        start       = snipped.find(">", end) + 1
        start       = snipped.find(">", start) + 1
        end         = snipped.find("<", start)

        title       = snipped[start : end]
        title       = title.replace("&amp;", "&")

        dois.append(title)

        start       = snipped.find('id="RECORD', end)

def extract_bib_info_from_wos_url(site, url, do_second_title = False):
    # extracts bib_info from wos site
    # follows pubmed-bib_info; see pubmed_plugins
    #
    # doi, pmid, title, number_authors, authors, country, pub_year, journal_name, volume, issue, pages,
    # received_year, received month, accepted year, accepted month, publication_type, url,
    # abstract

    from pubmed_plugins import empty_bib
    from definitions    import daterecognition, clear_text_from_inclusions, is_doi
    bib_info        = empty_bib()

    ## snip relevant information of wos page
    start           = site.find('<body')
    start           = site.find('', start + 1)
    start           = site.find('NEWfullRecord', start + 1)
    start           = site.find('id="records_form"', start + 1)
    start           = site.find('NEWfullRecordDataContainer', start + 1)
    start           = site.find('"l-content"', start + 1)
    end             = site.find('sidebar-container', start + 1)
    snipped         = site[start : end]

    # extract information from that snipped

    value           = "" # "value

    ## DOI
    bib_info[0]     = sub_extract_bib_info_from_wos_url_special(snipped, '>DOI:<', value)
    if is_doi(bib_info[0]) == False: # first attempt fails in .1% because WoS is different in special subdatabases
        bib_info[0] = sub_extract_bib_info_from_wos_url_special(snipped, '>DOI:', value)
    ## Pubmed-ID
    bib_info[1]     = sub_extract_bib_info_from_wos_url_special(snipped, '>PubMed ID:', value)
    ## Title
    bib_info[2]     = sub_extract_bib_info_from_wos_url_special(snipped, 'class="title"',value)
    ## Numbers and names of authrors
    authors, auth_number\
                    = sub_extract_bib_info_from_wos_url_authors(snipped)
    ##### number authors
    bib_info[3]     = auth_number
    ##### authors
    bib_info[4]     = authors
    ## country
    bib_info[5]     = sub_extract_bib_info_from_wos_url_country(snipped)
    ## publication year
    bib_info[6]     = clear_text_from_inclusions(sub_extract_bib_info_from_wos_url_special(snipped, '>Published:',value), "(", ")").strip()
    #bib_info[6]     = bib_info[6][bib_info[6].find(chr(32))+1 : len(bib_info[6])] # cut month away
    bib_info[6]     = bib_info[6][-4:len(bib_info[6])]# cut only year
    ## journal name
    bib_info[7]     = sub_extract_bib_info_from_wos_url_special(snipped, 'class="sourceTitle"',value)
    ## volume
    bib_info[8]     = sub_extract_bib_info_from_wos_url_special(snipped, '>Volume:', value)
    ## issue
    bib_info[9]     = sub_extract_bib_info_from_wos_url_special(snipped, '>Issue:', value)
    ## pages
    bib_info[10]    = sub_extract_bib_info_from_wos_url_special(snipped, '>Pages:', value)
    ## received_year
    bib_info[11]    = " "
    ## received month
    bib_info[12]    = " "
    ## received day
    bib_info[13]    = " "
    ## accepted year
    bib_info[14]    = " "
    ## accepted month
    bib_info[15]    = " "
    ## accepted day
    bib_info[16]    = " "
    ## epub date
    month, year, day= daterecognition(clear_text_from_inclusions(sub_extract_bib_info_from_wos_url_special(snipped, '>Published Electronically:', value), "(", ")" ))
    bib_info[17]    = day
    bib_info[18]    = month
    bib_info[19]    = year
    ## print date # month
    month, year, day= daterecognition(clear_text_from_inclusions(sub_extract_bib_info_from_wos_url_special(snipped, '>Published:', value), "(", ")" ))
    bib_info[20]    = day
    bib_info[21]    = month
    bib_info[22]    = year
    ## publication type
    bib_info[23]    = " "
    bib_info[24]    = sub_extract_bib_info_from_wos_url_special(snipped, 'Document Type:', "")
    ## times cited Pubmed
    bib_info[25]    = " "
    ## times cited Wos
    bib_info[26]    = sub_extract_bib_info_from_wos_url_cited_by(site)
    ## times cited Cochrane
    bib_info[27]    = " "
    ## cited in Pubmed
    #bib_info[28]    = " "
    ## cited in WoS
    #bib_info[29]    = " "
    # have to be last two
    ## URL
    bib_info[28]    = clear_text_from_inclusions(url, "<", ">")
    ## Abstract
    bib_info[29]    = sub_extract_bib_info_from_wos_url_special(snipped, '>Abstract<', "p")
    alt_abstract    = sub_extract_bib_info_from_wos_url_special(snipped, '>Abstract:', "").strip() # again necessary for foreign language abstracts
    if alt_abstract != "":
        bib_info[29] = alt_abstract


    for i in range(0, len(bib_info)):
        if bib_info[i] == list():
            bib_info[i] = " "
        else:
            bib_info[i] = tidy_up(str(bib_info[i]))

    if do_second_title == False:
        return bib_info
    else:
        second_title    = sub_extract_bib_info_from_wos_url_special(snipped, 'label="Main content"',"div")
        return bib_info, second_title

def sub_extract_bib_info_from_wos_url_cited_by(site):
    start       = site.find(">All Times Cited Counts<")
    if start > -1: # found the all times cited
        start       = site.find("</script>",    start)
        start       = site.find("<a",           start)
        #start       = site.find("href=",        start)
        #start       = site.find('"',            start) + 1
        #end         = site.find('"',            start)
        #url         = 'https://apps.webofknowledge.com' + site[start : end].replace("&amp;", "&")

        start       = site.find(">",            start) + 1
        end         = site.find("</a>",         start)
        number      = tidy_up(site[start : end]).replace(",", "").replace(" in All Databases", '')
    else:
        start       = site.find(">In Web of Science Core Collection<") + len(">In Web of Science Core Collection<")
        if start+1 > len(">In Web of Science Core Collection<"):
            #start   = site.find("href=",        start)
            #start   = site.find('"',            start) + 1
            #end     = site.find('"',            start)
            #url     = 'https://apps.webofknowledge.com' + site[start: end].replace("&amp;", "&")

            start   = site.find(">", start) + 1
            end     = site.find("</div>", start)
            end     = site.find("</div>", end + 1)
            number  = tidy_up(site[start: end]).replace(",", "").replace("Times Cited", '').replace("In Web of Science Core Collection","").replace(" ", "")
        else:
            number  = " "
            #url     = " "

    return number#, url



def sub_extract_bib_info_from_wos_url_country(site):
    from definitions import cut_country, clear_text_from_inclusions
    start           = site.find(">Addresses:") + len(">Addresses:")
    if start > len(">Addresses:"):
        start       = site.find('class="fr_address_row', start)
        if start > -1:
            start       = site.find('<a', start)
            start       = site.find('>', start) + 1
            end         = site.find('</a>', start)
            address     = site[start: end]
        else:
            start       = site.find("span>", site.find(">Addresses:") + len(">Addresses:")) + len("span>")
            end         = site.find("</p", start)
            address     = site[start : end]
    else:  # check; sometimes there is only address instead of addresses
        start       = site.find(">Address:") + len(">Address:")
        end         = site.find("</p>", start)
        address     = clear_text_from_inclusions(site[start : end])


    country         = cut_country(address)

    return country

def sub_extract_bib_info_from_wos_url_authors(site):
    auth_number     = 0
    authors         = ""

    start2           = 0
    while start2 > -1:
        start       = start2
        start       = site.find(">By:<", start)
        end         = site.find('</p>', start)
        start2      = site.find(">By:<", end)
    site            = site[start : end]

    start           = site.find('a title=')
    while start > -1:
        start       = site.find(">", start) + 1
        end         = site.find("<", start)
        auth        = site[start : end]
        authors     = authors + auth + "; "
        auth_number = auth_number + 1
        start = site.find('a title=', end)

    return authors[0:-2], auth_number

def sub_extract_bib_info_from_wos_url(site, input_string):
    start           = site.find(input_string) + len(input_string)
    if start >= len(input_string):
        start       = site.find('>', start) + 1
        start       = site.find('>', start) + 1
        start       = site.find('>', start) + 1
        end         = site.find('<', start)
        info        = tidy_up(site[start : end])
        return info
    else:
        return " "

def sub_extract_bib_info_from_wos_url_special(site, input_string, special_character):
    start = site.find(input_string) + len(input_string)
    if start >= len(input_string):
        start       = site.find("<" + special_character, start)
        start       = site.find(">", start) + 1
        end         = site.find("</" + special_character, start)
        info        = tidy_up(site[start : end])
        if site.find(input_string, end) > -1:
            info    = sub_extract_bib_info_from_wos_url_special(site[end: len(site)], input_string, special_character)
        return info
    else:
        return " "


def tidy_up(input):
    input       = input.replace("\t", " ")
    input       = input.replace("\n", " ")
    while input.find("<") > -1:
        start   = input.find("<")
        end     = input.find(">", start)
        input   = input[0:start] + input[end + 1 : len(input)]
    input       = input.replace("&amp;", "&")
    input       = input.replace("  ", " ")
    return input.strip()

def identify_correct_wos_entry(browser, urls, input, input_type):
    # scans through several urls for the correct entry
    # returns the bib_info of this title, gotten from WebOfScience
    #from pubmed_plugins import empty_bib
    from definitions    import compare_title, decapitalize, open_page, no_full_stop
    for i in range(0, len(urls)):
        open_page(browser, urls[i], allow_restart=False)
        site            = browser.page_source
        new_bib_info, second_title    = extract_bib_info_from_wos_url(site, urls[i], do_second_title=True)
        if input_type == "DOI":
            if decapitalize(input) == decapitalize(new_bib_info[0]):
                return new_bib_info
        elif input_type == "Title":
            if compare_title(new_bib_info[2], input)  | ((second_title != "") & (compare_title(no_full_stop(second_title), input))):
                return new_bib_info
    return list()

def next_page_wos_cited_by(browser):
    try:
        obj         = 'a.snowplow-navigation-nextpage-bottom'
        browser.find_element_by_css_selector(obj).click()
    except:
        try:
            obj         = "div.paginationBar:nth-child(2) > div:nth-child(4) > div:nth-child(1) > div:nth-child(3) > form:nth-child(1) > table:nth-child(7) > tbody:nth-child(1) > tr:nth-child(1) > td:nth-child(3) > a:nth-child(1)"
            browser.find_element_by_css_selector(obj).click()
        except:
            obj         = "div.paginationBar:nth-child(2) > div:nth-child(4) > div:nth-child(1) > div:nth-child(3) > form:nth-child(1) > nav:nth-child(7) > table:nth-child(1) > tbody:nth-child(1) > tr:nth-child(1) > td:nth-child(3) > a:nth-child(1)"
            browser.find_element_by_css_selector(obj).click()

def open_cited_url(browser, url):
    # opens the cited by dialog
    from definitions import open_page, clear_text_from_inclusions

    if browser.current_url != url:
        open_page(browser, url, allow_restart=False)

    mainlink            = "https://apps.webofknowledge.com"

    site                = browser.page_source

    start               = site.find("<body")
    start               = site.find("NEWfullRecord", start)
    start               = site.find("NEWfullRecordDataContainer", start)
    start               = site.find("l-column-content", start)
    start               = site.find("sidebar-container", start)
    start               = site.find("card-box", start)

    start_l             = site.find("All Times Cited Counts", start)
    if start_l > -1:  # "in all databases" available
        start           = site.find("block-text-content-scorecard", start)
        start           = site.find("</script", start)
        start           = site.find("href", start)
        start           = site.find('"', start) + 1
        end             = site.find('"', start)

    else:           # not this "in all databases", but
        start           = site.find("flex-row-partition1", start)
        start           = site.find("href", start)
        start           = site.find('"', start) + 1
        end             = site.find('"', start)

    if site[start:end].find("javascript") != -1: # necessary, because no link when 0
        start           = -1
        end             = -1

    sublink         = mainlink + site[start:end].replace("&amp;","&")
    if sublink == mainlink:
        return False
    else:
        sublink         = clear_text_from_inclusions(sublink, "<", ">")
        open_page(browser, sublink, allow_restart=False)
        return True


###################################################################
def sub_extract_cited_by_wos(elements, browser, http, bib_info, toplevel_doi, parent_doi, url, depth, depth_max, max_results=5000):
    from pubmed_plugins import search_pubmed_for_pmids, identify_correct_pmid
    from definitions import is_doi, open_page, get_together_cited_by_wos_pub, sub_extract_cited_by
    #from plugins_webofscience import open_cited_url, extract_urls_wos, next_page_wos_cited_by

    # recursively
    new_dois                            = list()
    new_urls                            = list()

    # open cited by in browser
    any_cite                            = open_cited_url(browser, url)

    # where there any citations at all?
    if any_cite:

        # get urls of all "cited by" entries
        site                            = browser.page_source
        aurl                            = browser.current_url
        prevurl                         = " "
        extract_urls_wos(site, new_dois, new_urls)
        while (len(new_dois) < max_results) & ((len(new_dois) % 10) == 0) & (len(new_dois) > 0) & (aurl != prevurl):
            try:
                next_page_wos_cited_by(browser)
                prevurl                 = aurl
                aurl                    = browser.current_url
                if prevurl != aurl:  # precaution, because infinity loop when exact 10/20/30... results
                    site                = browser.page_source
                    extract_urls_wos(site, new_dois, new_urls)
            except: # can happen when less wos entries than formerly stated existed. seems to be an error in Reuters's WoS
                print("Error in Result retrieval for DOI %s\n" % parent_doi)
                break


        # get bib_infos of those urls and recall their sources if depth is deep enough
        for u in range(0, len(new_urls)):
            # get bib_info
            ## is loop, because sometimes empty pages which is false
            stat                        = 0
            while stat == 0:
                try:
                    open_page(browser, new_urls[u], allow_restart=False)  # open site
                    site                = browser.page_source
                    bib_info_wos        = extract_bib_info_from_wos_url(site, new_urls[u])
                except:
                    pass

                try:
                    int(bib_info_wos[3])
                    stat                = 1
                except:
                    pass
            ## end of opening loop

            if is_doi(bib_info_wos[0]):
                pmids                   = search_pubmed_for_pmids("DOI", bib_info_wos[0], http, max_pmids=30)
                bib_info_pub            = identify_correct_pmid(http, pmids, bib_info_wos[0], "DOI")
            else:
                pmids                   = search_pubmed_for_pmids("title", new_dois[u], http, max_pmids=30)
                bib_info_pub            = identify_correct_pmid(http, pmids, new_dois[u], "title")

            # getting Infos of Pubmed and WoS together + adding the parent information + adding it to the large bib_info database
            get_together_cited_by_wos_pub(bib_info, bib_info_wos, bib_info_pub, toplevel_doi, parent_doi, depth)

    return browser


        
###################################################################
###################################################################
##################### dynamic css selektors #######################
###################################################################
###################################################################
def next_page_wos(browser):
    obj         = ["div.paginationBar:nth-child(2) > div:nth-child(4) > div:nth-child(1) > div:nth-child(3) > form:nth-child(1) > table:nth-child(8) > tbody:nth-child(1) > tr:nth-child(1) > td:nth-child(3) > a:nth-child(1) > i:nth-child(1)",
                   "div.paginationBar:nth-child(2) > div:nth-child(4) > div:nth-child(1) > div:nth-child(3) > form:nth-child(1) > nav:nth-child(8) > table:nth-child(1) > tbody:nth-child(1) > tr:nth-child(1) > td:nth-child(3) > a:nth-child(1)",
                   "a.snowplow-navigation-nextpage-top > i:nth-child(1)"]
    for i in range(0, len(obj)):
        try:
            browser.find_element_by_css_selector(obj[i]).click()
            return
        except: pass

def find_element_all_databases(browser):
    # find the "all databases" and clicks it
    # changes its name therefore "dynamic" css selector
    from time import sleep

    control     = 1

    while control == 1:
        try:
            site        = browser.page_source

            start       = site.find('class="select2-container')
            start       = site.find('class="select2-dropdown', start)
            start       = site.find('class="select2-results"', start)
            start       = site.find('id="select2-databases-results"', start) + 10
            start       = site.find('id="', start) + len('id="')
            end         = site.find('"', start)

            obj         = '#' + site[start:end]
            obj         = into_css_object(obj)

            browser.find_element_by_css_selector(obj).click()

            control     = 0
        except:
            sleep(.8)


def find_element_search_tag(browser, search_tag):
    # find the "topics" and clicks it
    # changes its name therefore "dynamic" css selector
    site        = browser.page_source

    start       = site.find("<body")
    start       = site.find('class="select2-container', start)
    start       = site.find('class="select2-dropdown', start)
    start       = site.find('id="select2-select1-results', start)
    #start       = site.find('id="', start) + len('id="')
    #start       = site.find('id="', start) + len('id="')

    match       = 0
    while (start > -1) & (match == 0):
        start       = site.find('id="', start) + len('id="')
        end         = site.find('"', start)
        namestart   = site.find(">", end) + 1
        nameend     = site.find("<", namestart)
        name        = site[namestart : nameend]
        if name == search_tag:
            match   = 1

    obj         = '#' + site[start:end]
    obj         = into_css_object(obj)

    browser.find_element_by_css_selector(obj).click()

def find_search_button(browser):
    # find the "Search" button and presses it
    # changes its name therefore "dynamic" css selector
    site        = browser.page_source

    start       = site.find("<body")
    start       = site.find('GeneralSearch_input_form', start)
    start       = site.find('"block-search"', start)
    start       = site.find('"block-search-content"', start)
    start       = site.find('"search-criteria"', start)
    start       = site.find('"search_table"', start)
    start       = site.find('class="button', start)
    start       = site.find('id="', start) + len('id="')
    end         = site.find('"', start)

    obj         = '#' + site[start:end]
    obj         = into_css_object(obj)
    try:
        browser.find_element_by_css_selector(obj).click()
    except:
        try:
            browser.find_element_by_css_selector(".primary-button").click()
        except:
            browser.find_element_by_css_selector("button.primary-button:nth-child(1)").click()

def into_css_object(obj):
    obj = obj.replace("/", "\\/")
    obj = obj.replace(".", "\\.")
    obj = obj.replace("?", "\\?")
    obj = obj.replace("=", "\\=")
    obj = obj.replace("&amp;", "\\&")
    return obj
