def general_search_tripdb(browser, studyID):
    from definitions import open_page
    mainlink        = "https://www.tripdatabase.com/search?criteria="
    sublink         = mainlink + '"' + studyID + '"'
    browser         = open_page(browser, sublink)

    dois            = list()
    urls            = list()

    site            = browser.page_source
    extract_results_tripdb(site, dois, urls)

    return dois, urls, browser


def extract_results_tripdb(site, dois, urls, max_results=100):
    start           = site.find("<body")
    start           = site.find("<main",        start)
    start           = site.find('id="results"', start)
    end             = site.find("</main")
    snipped         = site[start : end]

    start           = snipped.find("grade")
    while (start > -1) & (len(dois) < max_results):
        start       = snipped.find("<h3",     start)
        start       = snipped.find("href=",   start)
        start       = snipped.find('"',       start) + 1
        end         = snipped.find('"',       start)

        urls.append(snipped[start : end])

        start       = snipped.find(">", end) + 1
        end         = snipped.find("<", start)

        dois.append(snipped[start : end])

        start       = snipped.find("grade", end + 1)


###########################################################
#################### for guidelines #######################
###########################################################

def search_in_tripdb(browser, data):
    from definitions import unify_collector, no_full_stop, is_doi, empty_guidelines

    collector                   = [[],[]]##[list() for n in data]

    #if is_doi(data[0]):
    #    collector[0], browser   = guideline_search_tripdb(browser, data[0])
    #else: collector[0]          = empty_guidelines()
    collector[0]          = empty_guidelines()
    collector[1], browser       = guideline_search_tripdb(browser, '"' + no_full_stop(data[1]) + '"' + " " + data[2])

    result                      = unify_collector(collector)
    return result, browser

def guideline_search_tripdb(browser, data):
    from definitions import simplify_text, empty_guidelines, open_page
    mainlink            = "https://www.tripdatabase.com/search?categoryid=16%2C18%2C10%2C9%2C4&page="
    searchq             = simplify_text(data, ausnahmen=[" ", "-", "/", "1", "2", "3", "4", "5", "6", "7", "8", "9", "0", ".", "_", "(", ")", '"']).replace(" ", "+")

    loop                = 1
    runner              = 1
    result              = empty_guidelines()
    n_res               = 1
    while (loop == 1) & (n_res > len(result[1])):
        browser         = open_page(browser, mainlink + str(runner) + "&criteria=" + searchq)
        site            = browser.page_source
        result, n_res   = parse_tripdb_guidelines(site, result)
        runner          = runner + 1
        if (len(result[1]) == 0) | ((len(result[1]) % 20) != 0):
            loop        = 0
    return result, browser

def parse_tripdb_guidelines(cont, result):
    from definitions import clear_text_from_inclusions, is_doi
    # ["DOI", "Title", "hit quot", "id", "evidence-level", "society", "in_awmf", "in_nice", "in_tripdb"]

    # pre look if there are results at all
    start       = cont.find('id="resultcount')
    start       = cont.find(">", start) + 1
    end         = cont.find("<", start)
    if int(cont[start:end]) == 0:
        return result, 0
    n_res = int(cont[start: end])

    start       = cont.find('class="result')
    while (start > -1) & (n_res > len(result[1])):
        end     = cont.find('class="meta"', start)
        block   = cont[start : end]

        startb  = block.find('class="href')
        startb  = block.find('href="', startb) + len('href="')
        endb    = block.find('"', startb)
        result[6].append(block[startb: endb])


        startb  = block.find(">", endb) + 1
        endb    = block.find("</a>", startb)
        result[1].append(block[startb : endb].replace("&amp;", "&").strip())

        startb  = block.find('class="pub"')
        startb  = block.find(">", startb) + 1
        endb    = block.find("</a>", startb)
        result[5].append(block[startb: endb].strip())

        startb  = block.find('class="pyramid')
        startb  = block.find(">", startb) + 1
        endb    = block.find("</span>", startb)
        result[4].append(clear_text_from_inclusions(block[startb: endb]).strip())

        startb  = block.find('score="') + len('score="')
        endb    = block.find('"', startb)
        result[2].append("%1.3f" % (float(block[startb: endb])/100))

        startb  = block.find('docid="') + len('docid="')
        endb    = block.find('"', startb)
        result[3].append(block[startb: endb].strip())

        startb  = block.find('class="href')
        startb2 = block.find("10.", startb)
        endb    = block.find('"', startb)
        if is_doi(block[startb2 : endb].strip()):
            result[0].append(block[startb2: endb].strip())
        else:
            result[0].append(" ")

        result[7].append("0")
        result[8].append("0")
        result[9].append("1")

        start   = cont.find('class="result', end)

    return result, n_res

