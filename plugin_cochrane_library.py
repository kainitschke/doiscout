
def search_in_cochrane_library(browser, studyID, mode="all"):
    # open cochrane lib in selenium, enters the one (!) search string
    # gains and returns the links of the results found

    from definitions import remove_dublicates, open_page

    main_site               = "http://onlinelibrary.wiley.com/cochranelibrary/search"

    urls                    = list()

    # search in "Search All Text"
    if mode == "all":
        try:
        ## open site
            browser = open_page(browser, main_site)
            # Search Tag/Mode
            ## click on the select things and select "Search All Text"
            browser.find_element_by_xpath("/html/body/div[2]/div/form/div/fieldset[1]/ol/li/select/option[1]").click()
            ## enter Study ID in resp. field
            browser.find_element_by_css_selector('#searchCriteria0').send_keys(studyID)
            ## click on search
            browser.find_element_by_css_selector('#submitSearch').click()
            ## get the results
            extract_search_results_cochrane(browser, urls, max_results=100)
        except: pass

        # search in "Title, Abstract, Keywords"
        try:
            ## for some reasons here is found more than in "all fields"
            ## open site again
            browser = open_page(browser, main_site)
            ## click on the select things and select "Search All Text"
            browser.find_element_by_xpath("/html/body/div[2]/div/form/div/fieldset[1]/ol/li/select/option[6]").click()
            ## enter Study ID in resp. field
            browser.find_element_by_css_selector('#searchCriteria0').send_keys(studyID)
            ## click on search
            browser.find_element_by_css_selector('#submitSearch').click()
            ## get the results
            extract_search_results_cochrane(browser, urls, max_results=200)
        except: pass

    if mode == "DOI":
        try:
            browser = open_page(browser, main_site)
            # Search Tag/Mode
            ## click on the select things and select "DOI"
            browser.find_element_by_xpath("/html/body/div[2]/div/form/div/fieldset[1]/ol/li/select/option[10]").click()
            ## enter DOIs in resp. field
            browser.find_element_by_css_selector('#searchCriteria0').send_keys(studyID)
            ## click on search
            browser.find_element_by_css_selector('#submitSearch').click()
            ## get the results
            extract_search_results_cochrane(browser, urls, max_results=100)
        except: pass


    urls                    = remove_dublicates(urls)
    return urls, browser

def extract_search_results_cochrane(browser, entries, max_results=100):
    # takes the already open cochrane library search site and extracts all the founds results
    from time        import sleep
    sleep(0.3)

    new_page                = True                              # contains if there still is a new page or last result was extracted already

    while new_page == True:

        site                = browser.page_source               # get page info
        start               = site.find("searchResults")        # find start of Results
        start               = site.find("resultSet",     start) # find start of Results
        end                 = site.find("refineResults", start) # find end of results; resp. start of next paragraph
        snipped             = site[start : end]                 # cut the results for further processing

        # find link
        start               = snipped.find("<li")
        start               = snipped.find("href", start)
        start               = snipped.find('"'   , start) + 1
        end                 = snipped.find('"'   , start)

        while (start > 0) & (end > -1) & (len(entries) < max_results):
            link            = snipped[start:end]

            #if (link == "")|(link == '/browse/publications'):
            #    a = 1
            #elif is_doi(wiley_doi_from_link_text(link)):
            #    entries.append(wiley_doi_from_link_text(link))
            #else:
            entries.append("http://onlinelibrary.wiley.com" + link)

            # find link
            start           = snipped.find("<li", end)
            start           = snipped.find("href", start)
            start           = snipped.find('"', start) + 1
            end             = snipped.find('"', start)


        new_page            = next_page_cochrane_library(browser, site)

def extract_bib_info_from_cochrane_library(http, input):
    # extracts bib_info from the cochrane library
    # input can be the direct link to the site or the DOI
    from definitions import is_link, is_doi, daterecognition, string_2_html
    from pubmed_plugins import empty_bib

    if is_doi(input):
        input               = "http://onlinelibrary.wiley.com/doi/" + string_2_html(input, ausschluss = ["/"]) + "/full"
    if is_link(input) == False:
        disp("error - not yet implemented")

    bib_info                = empty_bib()
    try: # produces error if page does not exist; caught here
        site                    = http.request("GET", input).data.decode("utf-8", "ignore")

        bib_info[0]             = sub_extract_bib_info_from_cochrane_library(site, "DOI:")       # DOI
        bib_info[1]             = " "                                                            # Pubmed ID
        bib_info[2]             = get_title(site)                                                # Title
        authors, numbers        = sub_extract_bib_info_cl_author(site)
        bib_info[3]             = numbers                                                        # number of authors
        bib_info[4]             = authors                                                        # authors
        bib_info[5]             = get_country(site)                                              # country
        month, year, day        = daterecognition(sub_extract_bib_info_from_cochrane_library(site, "First published:"))
        bib_info[6]             = year                                                           # publication year
        bib_info[7]             = " "                                                            # Journal name
        bib_info[8]             = " "                                                            # volume
        bib_info[9]             = " "                                                            # issue
        bib_info[10]            = " "                                                            # pages
        bib_info[11]            = " "                                                            # received_year
        bib_info[12]            = " "                                                            # received_month
        bib_info[13]            = " "                                                            # received_day
        bib_info[14]            = " "                                                            # accepted_year
        bib_info[15]            = " "                                                            # accepted_month
        bib_info[16]            = " "                                                            # accepted_day
        bib_info[17]            = " "                                                            # epub_day
        bib_info[18]            = " "                                                            # epub_month
        bib_info[19]            = " "                                                            # epub_year
        bib_info[20]            = " "                                                            # print_day
        bib_info[21]            = " "                                                            # print_month
        bib_info[22]            = " "                                                            # print_year
        bib_info[23]            = " "                                                            # publication type
        bib_info[24]            = " "                                                            # times cited Pubmed
        bib_info[25]            = " "                                                            # times cited WoS
        bib_info[26]            = sub_extract_bib_info_from_cochrane_library(site, "Cited by")   # times cited Cochrane
        bib_info[27]            = input                                                          # url
        bib_info[28]            = get_abstract(site)                                             # abstract

    except:pass

    return bib_info

def sub_extract_bib_info_from_cochrane_library(input, identifier):
    start                   = input.find('<article id="main-content"')
    end                     = input.find("</article>", start)
    input                   = input[start : end]

    start                   = input.find(identifier)
    start                   = input.find("</span>", start) + len("</span>")
    start                   = input.find("<", start) + 1
    start                   = input.find(">", start) + 1
    end                     = input.find("<", start)

    res                     = input[start : end]
    if res == '': res       = " "

    return res

def wiley_doi_from_link_text(link):
    # tries to take the doi directly form the link instead of opening it to reduce time costs
    try:
        start   = link.find("10.")
        end     = link.find("/full", start)
        doi     = link[start:end]
        return doi
    except:
        return " "

def next_page_cochrane_library(browser, site):
    # opens next page in cochrane library search results
    # returns if there was another page
    from time import sleep

    start               = site.find("paginationFilter")
    if start > -1:
        ## finds page info on site and cuts it
        end             = site.find("</fieldset", start)
        snipped         = site[start:end]

        ## find presently opened
        selected        = snipped.find("selected")

        xpath   = next_xpath(snipped, selected)

        if xpath != False:
            # open xpath in browser; wait necessary, because otherwise too fast
            browser.find_element_by_xpath(xpath).click()
            sleep(.3)

            # previous/next butten go to infinite loop, therefore change xpath
            if xpath.find("LinkNext") > -1:
                xpath   = next_xpath(snipped, 0)

            # wait until ready
            wait_for_proceeed(browser, xpath)

            new_page    = True
        else:
            new_page    = False

    else:
        new_page        = False

    return new_page

def next_xpath(snipped, selected):
    # finds the xpath for the next element; for "Next" and "previous" there is something special
    ## ignore previous and search after; otherwise ignore
    prev    = snipped.find("LinkPrevious")
    if prev > selected:
        selected = prev
        selected = snipped.find("</li", selected)

    ## find next page
    next    = snipped.find("id=", selected)

    ## only proceed if there are subsequent pages
    if next > -1:
        start = snipped.find('"', next) + 1
        end = snipped.find('"', start)
        xpath = '//*[@id="%s"]' % snipped[start:end]
        return xpath
    else:
        return False

def wait_for_proceeed(browser, xpath):
    # functions waits until the next page of cochrane library search (wiley) was loaded
    from time import sleep
    next    = 0
    while next == 0:
        sleep(.2)
        try:
            # as long as the button is available, it is still loading
            # works because as soon as the page is loaded, the present result page is no longer a button, but only text
            # hence, it is no longer as xpath identifiable, hence error, hence "except"
            # does not work with the "next" button, because that is not disabled for next 150 entries, so infinity loop
            # therefore, other xpath above
            browser.find_element_by_xpath(xpath)
        except:
            next = 1

def cl_get_id_from_frame(http, url):
    # open url in selenium; tries to catch the DOI from there
    from definitions import find_earliest_end
    try:
        #browser.get(url)
        #browser.switch_to_frame("sidebar")
        ##site        = browser.page_source
        url         = url.replace("frame.html", "sect0.html")
        site        = http.request("GET", url).data.decode("utf-8","ignore")
        start       = site.find("DOI")
        start       = site.find("10.", start)
        end         = find_earliest_end(site, start)
        if start > -1:
            return site[start : end]
        else:
            return " "
    except:
        return " "

def is_in_cochrane_library(browser, dois, timestamp):
    from definitions import printProgressBar, remaining_time
    import datetime

    # Progress things
    show_string             = "Searching Cochrane Lib."
    start_time              = datetime.datetime.now()
    printProgressBar(0, len(dois), prefix=show_string, suffix="remaining: 0:00:00:00", length=50)

    result                  = [list(), list()]

    for i in range(0, len(dois)):

        urls                = search_in_cochrane_library(browser, dois[i], mode = "DOI")
        result[0].append(dois[i])
        if   len(urls) == 0: result[1].append("0")
        elif len(urls) == 1: result[1].append("1")
        elif len(urls) >  1: result[1].append("2")
        else:                result[1].append("-99")

        printProgressBar(i + 1, len(dois), prefix=show_string,
                         suffix=remaining_time(start_time=start_time, step=i, max=len(dois)),
                         length=50)

    return result

####################################################################################
####################################################################################
####################################################################################
## further definitions for getting bibliographic information

def sub_extract_bib_info_cl_author(input):
    start                   = input.find('<article id="main-content"')
    end                     = input.find("</article>", start)
    input                   = input[start: end]

    numbers                 = 0
    authors                 = ""

    start                   = input.find('article-header__authors-name"')
    while start > -1:
        numbers             = numbers + 1
        start               = input.find(">", start) + 1
        end                 = input.find("<", start)
        name                = input[start : end]

        name                = remodel_name(name)
        authors             = authors + name + "; "

        start               = input.find('article-header__authors-name"', start + 6)

    if authors == "":
        authors             = " "
    else:
        authors             = authors[0:-2]
    return authors, numbers

def remodel_name(name):
    spaces                  = [n for (n, e) in enumerate(name) if e == chr(32)]
    #starts                  = list(spaces); starts.insert(0, 0)
    ends                    = list(spaces); ends.append(len(name))

    rnames                  = name[ends[-2]+1 : ends[-1]]
    if len(ends) > 1:
        rnames              = rnames + ', ' + name[0]
    if len(ends) > 2:
        rnames              = rnames + name[ ends[0] + 1 : ends[1]]

    return rnames

def get_country(input):
    from definitions import cut_country
    start                   = input.find('<article id="main-content"')
    end                     = input.find("</article>", start)
    input                   = input[start: end]

    add                     = " "
    #start                   = input.find('Corresponding author') % for corresponding authors
    start                   = input.find("article-header__authors-item-aff-addr")
    #if start > -1:          # find direct address
    #    end                 = input.find("</div>", start)
    #    input               = input[start: end]

     #   start               = input.find("<p")
     #   start               = input.find(">", start + 1) + 1
     #   end                 = input.find("<", start)
     #   add                 = input[start : end]

    #else:
    start               = input.find("<li>", start)
    start               = input.find(">", start) + 1
    end                 = input.find("<", start)
    add                 = input[start : end]

    country                 = cut_country(add)
    return country

def get_title(input):
    start                   = input.find('<article id="main-content"')
    end                     = input.find("</article>", start)
    input                   = input[start: end]

    start                   = input.find('class="article-header__title"')
    start                   = input.find('>', start) + 1
    end                     = input.find('<', start)

    title                   = input[start : end]
    title                   = title.replace("&#x2010;", '-')
    return title

def get_abstract(input):
    start                   = input.find('<article id="main-content"')
    end                     = input.find("</article>", start)
    input                   = input[start: end]

    start                   = input.find('id="en_main_abstract"')
    start                   = input.find(">", start) + 1
    end                     = input.find('</div>', start)
    input                   = input[start : end]

    start                   = input.find("<")
    while start > -1:
        end                 = input.find(">", start) + 1
        input               = input[0 : start] + ". " + input[end : len(input)]
        start               = input.find("<")

    return input

####################################################################################
####################################################################################
####################################################################################
####################################################################################
####################################################################################
## here is an autonomous script that gets all cochrane review groups review's DOIs
## it is not accessible from the GUI

def get_cochrane_groups_reviews():
    from definitions import initialize_browser, initialize_http, folder_structure, extract_bib_info, create_timestamp
    from pubmed_plugins import empty_bib, add_headers_bib_info
    from output_defs import write_output_is_in_cochrane, write_linewise, writing_file
    import os
    from time import sleep

    groups = ["Acute Respiratory Infections Group",
         "Airways Group",
         "Anaesthesia, Critical and Emergency Care Group",
         "Back and Neck Group",
         "Bone, Joint and Muscle Trauma Group",
         "Breast Cancer Group",
         "Childhood Cancer Group",
         "Colorectal Cancer Group",
         "Common Mental Disorders Group",
         "Consumers and Communication Group",
         "Cystic Fibrosis and Genetic Disorders Group",
         "Dementia and Cognitive Improvement Group",
         "Developmental, Psychosocial and Learning Problems Group",
         "Drugs and Alcohol Group",
         "Effective Practice and Organisation of Care Group",
         "ENT Group",
         "Epilepsy Group",
         "Eyes and Vision Group",
         "Fertility Regulation Group",
         "Gynaecological, Neuro-oncology and Orphan Cancer Group",
         "Gynaecology and Fertility Group",
         "Haematological Malignancies Group",
         "Heart Group",
         "Hepato-Biliary Group",
        "HIV/AIDS Group",
        "Hypertension Group",
        "IBD Group",
        "Incontinence Group",
        "Infectious Diseases Group",
        "Injuries Group",
        "Kidney and Transplant Group",
        "Lung Cancer Group",
        "Metabolic and Endocrine Disorders Group",
        "Methodology Review Group",
        "Movement Disorders Group",
        "Multiple Sclerosis and Rare Diseases of the CNS Group",
        "Musculoskeletal Group",
        "Neonatal Group",
        "Neuromuscular Group",
        "Oral Health Group",
        "Pain, Palliative and Supportive Care Group",
        "Pregnancy and Childbirth Group",
        "Public Health Group",
        "Schizophrenia Group",
        "Skin Group",
        "STI Group",
        "Stroke Group",
        "Tobacco Addiction Group",
        "Upper GI and Pancreatic Diseases Group",
        "Urology Group",
        "Vascular Group",
        "Work Group",
        "Wounds Group"]

    timestamp               = create_timestamp()
    folders                 = folder_structure("/home/nitschke/Downloads/cochrane_psychologie/searches/02_OR_uber_Cochrane_Library/cochrane_gruppen/")
    #browser                 = initialize_browser(os.getcwd()+"/geckodriver", folders)
    http                    = initialize_http()

    bib_info                = empty_bib()
    bib_info.append(list()) # for group
    dois                    = list()
    group_sammler           = list()

    for i in range(0, len(groups)):

        counter             = 0
        old_dois_length     = len(dois) - 1

        while len(dois) > old_dois_length:
            ## go through groups, get dois for every entry from the html

            old_dois_length = len(dois)
            counter         = counter + 1

            agroup          = groups[i].replace(chr(32),"%20")
            agroup          = agroup.replace("/", "%252F")
            sublink         = "http://www.cochranelibrary.com/review-group/" + agroup + "/?stage=review" + "&page=" + str(counter)
            site            = http.request("GET", sublink).data.decode("utf-8", "ignore")

            start       = site.find('class="results-block__articles"')
            end         = site.find("</section>", start)
            subsite     = site[start:end]

            #start       = subsite.find('mainTitle')
            start = subsite.find("href=")
            while start > -1:
                start   = subsite.find("doi", start)
                start   = subsite.find("10", start)
                end     = subsite.find("/full", start)
                dois.append(subsite[start:end])
                group_sammler.append(groups[i])
                start   = subsite.find("href=", start)

        afile           = writing_file(timestamp + '_DOIs_' + groups[i].replace("/","-") + ".txt", folders, 1)
        for r in range(0, len(dois)):
            afile.write(dois[r] + '\n')
        writing_file(afile, mode=2)

        print(create_timestamp(), " ", len(dois), " ", groups[i])

        dois = list()

    #bib_info, failed, weg, browser = extract_bib_info(dois, browser, http)
    #header              = add_headers_bib_info(empty_bib())
    #header.append(["Review_Group"])

    #x                   = [[] for r in range(len(dois))]
    #bib_info.append(x)
    #for r in range(0, len(dois)):
    #    bib_info[-1][r] = group_sammler[r]
    #headers             = list()
    #for r in range(0, len(header)): # header
    #    headers.append(header[r][0])



