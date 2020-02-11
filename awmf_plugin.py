def search_in_awmf(data, browser):
    from definitions import unify_collector, no_full_stop, is_doi, empty_guidelines

    collector                   = [[], []]  # [list() for n in data]

    if is_doi(data[0]):
        collector[0], browser   = search_on_awmf_site(data[0], browser)
    else: collector[0]          = empty_guidelines()
    collector[1], browser       = search_on_awmf_site(no_full_stop(data[1]) + " " + data[2], browser)

    result                      = unify_collector(collector)

    return result, browser

##############################################
def search_on_awmf_site(info, browser):
    from definitions import open_page, empty_guidelines
    from selenium.webdriver.common.keys import Keys

    result          = empty_guidelines()

    url             = "https://www.awmf.org/leitlinien/leitlinien-suche.html"
    browser         = open_page(browser, url)

    obj             = "div.wrapp:nth-child(1) > input:nth-child(1)"
    search_field    = browser.find_element_by_css_selector(obj)
    search_field.send_keys(Keys.CONTROL + "a")    # highlights everything
    search_field.send_keys(Keys.BACK_SPACE)       # deletes everything
    search_field.send_keys(info)

    obj             = "input.btn-search:nth-child(1)"
    browser.find_element_by_css_selector(obj).click()

    loop            = 1
    while loop == 1:

        if browser.page_source.find("Ihre Suche ergab leider keine Treffer") == -1:
            parse_awmf_results(browser.page_source, result)

        try:
            obj = "ul.pagebrowser:nth-child(6) > li:nth-child(13) > a:nth-child(1)"
            if browser.find_element_by_css_selector(obj).text != "weiter":
                obj = "ul.pagebrowser:nth-child(6) > li:nth-child(12) > a:nth-child(1)"
            try:
                browser.find_element_by_css_selector(obj).click()
            except:
                loop    = 0
        except:
            loop = 0

    return result, browser

##############################################
def parse_awmf_results(cont, result):
    #from definitions import empty_guidelines
    #["DOI", "Title", "hit quot", "id", "evidence-level", "society"]
    #result      = empty_guidelines()
    #runner      = 0
    start       = cont.find("search-results-wrapper")
    end         = cont.find('class="pagebrowser"', start)
    cont        = cont[start:end]
    start       = 0
    while start > -1:
        # hit quot
        start   = cont.find("Treffergenauigkeit", start)
        start   = cont.find(":", start) + 1
        end     = cont.find("%", start)
        result[2].append("%1.3f" % (float(cont[start:end])/100))

        # Title
        start   = cont.find("title=", end)
        start   = cont.find('"', start) + 1
        end     = cont.find('"', start)
        result[1].append(cont[start : end].strip())

        #id
        start   = cont.find("Registrierungsnummer", end)
        start   = cont.find(":", start) + 1
        end     = cont.find(",", start)
        result[3].append(cont[start : end].strip())

        ## level
        start   = cont.find("Entwicklungsstufe", end)
        start   = cont.find(":", start) + 1
        end     = cont.find("<", start)
        result[4].append(cont[start:end].strip())

        ## society
        startx  = cont.find("Fachgesellschaft(en)", end)
        if startx != -1:
            start   = startx   # sometimes there is no society
            start   = cont.find(":", start) + 1
            end     = cont.find("<", start)
            result[5].append(cont[start : end].strip())
        else:
            result[5].append(" ")

        ## url
        start   = cont.find('"leitlinien-download"', end)
        end     = cont.find("</ul>", start)
        block   = cont[start : end]

        start2  = block.find('href="') + len('href="')
        while start2 > -1:

            end2    = block.find('"', start2)
            url     = "https://www.awmf.org/" + block[start2 : end2]
            start2  = block.find(">", end2) + 1
            end2    = block.find("<", start2)
            pdftype = block[start2 : end2].strip()
            if pdftype == "Langfassung":
                break
            else:
                url = " "
            start2 = block.find('href="', end2) + len('href="')
        result[6].append(url)

        result[0].append(" ")
        result[7].append("1")
        result[8].append("0")
        result[9].append("0")

        start   = cont.find("search-results text-block", end)
