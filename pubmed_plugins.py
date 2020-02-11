def titles_2_dois_by_pubmed(title, http):
    from definitions import is_doi
    pmids           = search_pubmed_for_pmids("title", title, http)
    if pmids == list():
        doi         = title
    else:
        doi         = identify_correct_pmid(http, pmids, title, "title")
        if is_doi(doi[0]):
            doi     = doi[0]
        else:
            doi     = title
    return doi

def search_pubmed_for_pmids(mode, input, http, max_pmids=500):
    # searches the "mode" (i.e. "title" or "doi") in the pubmed database for their pubmed-ids
    from definitions import string_2_html

    try:
        main_url        = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"  # main url
        eutil           = "esearch"
        searchdb        = "pubmed"

        if mode == "DOI":
            input = input.replace("(",'_')
            input = input.replace(")", '_')
        else:
            input = clear_logical_relations(input)
            input = reduce_search_terms_number(input, 13)
            input = string_2_html(input)

        if mode == "AllFields":
            modestring  = ""
        else:
            modestring      = "[" + mode + "]"
        sublink         = main_url + eutil + ".fcgi?" + "db=" + searchdb + "&term=" + input + modestring + "&retmax=" + str(max_pmids)
        site            = http.request("GET", sublink).data.decode("utf-8", "ignore")

        pmids           = list()
        start           = site.find("<IdList>") + len("<IdList>")
        end             = site.find("</IdList>")

        snipped         = site[start : end]

        start           = snipped.find("<Id>")
        end             = snipped.find("</Id>", start)

        while start > -1:
            pmids.append(snipped[start + + len("<Id>") : end])
            start       = snipped.find("<Id>",  end + 1)
            end         = snipped.find("</Id>", start  )

    except:
        pmids           = list()

    return pmids

def identify_correct_pmid(http, pmids, input, input_type):
    # identifies the one correct pmid of multiple entred pmids
    from definitions import compare_title
    #bib_info        = list()
    for i in range(0, len(pmids)):
        bib_info    = extract_bib_from_pubmed(http, pmids[i])
        if input_type == "DOI":
            comp    = bib_info[0]
        elif input_type == "title":
            comp    = bib_info[2]
        if compare_title(input, comp):
            # break
            return bib_info
    return list()

def empty_bib(mode="empty"):
    # creates an empty bib of the right size for the entries
    bib_info    = list()
    if mode == "empty":
        for i in range(0, 30):
            bib_info.append(list())  # empty lists for every entry in bib_info
    elif mode == "spaces":
        for i in range(0, 30):
            bib_info.append(" ")
    return bib_info

def merge_bib_info(org_bib, add_bib):
    # adding the add_bib to the existing bib
    for i in range(0, len(add_bib)):
        if add_bib[i] != list():
            org_bib[i].append(add_bib[i])
        else:
            org_bib[i].append(" ")
    return org_bib

def idx_header(input):
    # finds the index of a specific header text
    header      = add_headers_bib_info(empty_bib())
    idx         = header.index([input])
    return idx

def add_headers_bib_info(bib_info, header = list()):
    # adds the headers/meanings of the columns for the output file to be written
    if header == list():
        header       = ["DOI", "PubmedID", "Title", "Number of Authors", "Author", "Country", \
                       "Year", "Journal", "Volume", "Issue", "Pages", \
                       "Received in Year", "Received in Month", "Received in Day", "Accepted Year", "Accepted Month", "Accepted Day", \
                       "epub_day", "epub_month", "epub_year", "print_day", "print_month", "print_year", \
                       "Publication_Type_Pubmed", "Publication_Type_WoS", "Cited_By_Pubmed", "Cited_By_WoS", "Cited_By_Cochrane", "URL", "Abstract"]

    #endnoteable     = [False] * len(header)
    #trues           = [0, 2, 4, 6, 7, 8, 9, 10, 23, 26]
    #for i in trues: endnoteable[i] = True

    for i in range(0,len(bib_info)):
        bib_info[i].insert(0, header[i])
    return bib_info#, endnoteable

def extract_bib_from_pubmed(http, pmid):    
    # extracts pubmed bibliographic information for one pubmed-Id
    # out-list is as follows:
    # doi, pmid, title, number_authors, authors, country, pub_year, journal_name, volume, issue, pages,
    # received_year, received month, accepted year, accepted month, publicationt_type, number cited by, url cited by
    # url, abstract

    from definitions import is_doi, month_2_number

    main_url        = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"  # main url
    eutil           = "efetch"
    searchdb        = "pubmed"
    rettype         = "abstract"

    sublink         = main_url + eutil + ".fcgi?" + "db=" + searchdb + "&id=" + pmid + "&rettype=" + rettype
    site            = http.request("GET", sublink).data.decode("utf-8", "ignore")

    bib_info        = list()

    bib_info, weg   = sub_extract_bib_from_pubmed(bib_info, site, "ArticleIdList", 'ArticleId IdType="doi"')        # DOI
    if is_doi(bib_info[0]) == False: # sometimes the doi is stored elsewhere
        bib_info, weg \
                    = sub_extract_bib_from_pubmed(list(), site, "Article", 'ELocationID EIdType="doi"')           # DOI (when stored for E-Publication
    #bib_info[0]     = decapitalize(bib_info[0])     # decapitalize
    bib_info, weg   = sub_extract_bib_from_pubmed(bib_info, site, "ArticleIdList", 'ArticleId IdType="pubmed"')     # Pubmed-ID
    bib_info, weg   = sub_extract_bib_from_pubmed(bib_info, site, "Article", "ArticleTitle")                        # Title
    bib_info        = sub_extract_bib_from_pubmed_authors(bib_info, site)                                           # author number + author names + country # special because multiple and some processing
    bib_info, weg   = sub_extract_bib_from_pubmed(bib_info, site, "Journal", "Year")                                # Publication Year
    bib_info, weg   = sub_extract_bib_from_pubmed(bib_info, site, "Journal", "Title")                               # Journal name
    bib_info, weg   = sub_extract_bib_from_pubmed(bib_info, site, "Journal", "Volume")                              # Volume
    bib_info, weg   = sub_extract_bib_from_pubmed(bib_info, site, "Journal", "Issue")                               # Issue
    bib_info, weg   = sub_extract_bib_from_pubmed(bib_info, site, "Journal", "MedlinePgn")                          # Pages
    bib_info, weg   = sub_extract_bib_from_pubmed(bib_info, site, 'PubMedPubDate PubStatus="received"', "Year")     # Received Year
    bib_info, weg   = sub_extract_bib_from_pubmed(bib_info, site, 'PubMedPubDate PubStatus="received"', "Month")    # Received Month
    bib_info, weg   = sub_extract_bib_from_pubmed(bib_info, site, 'PubMedPubDate PubStatus="received"', "Day")  # Received Year
    bib_info, weg   = sub_extract_bib_from_pubmed(bib_info, site, 'PubMedPubDate PubStatus="accepted"', "Year")     # Accepted Year
    bib_info, weg   = sub_extract_bib_from_pubmed(bib_info, site, 'PubMedPubDate PubStatus="accepted"', "Month") # Accepted Month
    bib_info, weg   = sub_extract_bib_from_pubmed(bib_info, site, 'PubMedPubDate PubStatus="accepted"', "Day")  # Accepted Month

    bib_info, weg   = sub_extract_bib_from_pubmed(bib_info, site, 'ArticleDate DateType="Electronic"', "Day")  # epub_date
    bib_info, weg   = sub_extract_bib_from_pubmed(bib_info, site, 'ArticleDate DateType="Electronic"', "Month")     # epub_date
    month_2_number(bib_info)
    bib_info, weg   = sub_extract_bib_from_pubmed(bib_info, site, 'ArticleDate DateType="Electronic"', "Year")      # epub_date

    bib_info, weg   = sub_extract_bib_from_pubmed(bib_info, site, 'PubDate', "Day")  # print_date
    bib_info, weg   = sub_extract_bib_from_pubmed(bib_info, site, 'PubDate', "Month")                               # print_date
    month_2_number(bib_info)
    bib_info, weg   = sub_extract_bib_from_pubmed(bib_info, site, 'PubDate', "Year")                                # print date

    bib_info, weg   = sub_extract_bib_from_pubmed(bib_info, site, 'PublicationTypeList', "PublicationType", multiple = True)        # Publication Type Pubmed
    bib_info.append(" ")                                                                                            # Publication Type WoS
    sub_extract_cited_by(http, bib_info, pmid)                                                                                           # number cited by Pubmed
    bib_info.append(" ")                                                                                            # number cited by WoS
    bib_info.append(" ")                                                                                            # number cited by Cochrane
    #bib_info.append(" ")                                                                                            # cited in Pubmed
    #bib_info.append(" ")                                                                                            # cited in WoS
    bib_info.append("https://www.ncbi.nlm.nih.gov/pubmed/" + pmid)                                                  # url
    bib_info, weg   = sub_extract_bib_from_pubmed(bib_info, site, "Abstract", "AbstractText")                       # Abstract

    return bib_info

def sub_extract_bib_from_pubmed(bib_info = list(), site = "", outer = "", inner="", multiple = False):
    from definitions import find_earliest_end, clearer_text
    outer_start         = site.find("<"  + outer) + len(outer) + 1

    sammler = list()
    extract = " "
    
    if outer_start > len(outer) + 1:
        # finds the right entry within the xml file
        pre_end             = find_earliest_end(outer, 0, einschluss=[chr(32)]) # because in XML end statement is often shorter

        outer_end           = site.find("</" + outer[0:pre_end] + ">", outer_start)
        snipped             = site[outer_start : outer_end + 1]

        inner_start         = snipped.find("<" + inner) + len(inner)
        if inner_start > (len(inner) - 1):
            inner_start     = snipped.find(">", inner_start)
        inner_end           = snipped.find("<", inner_start)

        while (inner_start > (len(inner) - 1))&(inner_end > -1):
            extract         = snipped[inner_start + 1 : inner_end]
            extract         = clearer_text(extract)
            sammler.append(extract.replace("\n", ""))
            inner_start     = snipped.find("<" + inner, inner_end + 4)
            if inner_start > -1:
                inner_start = snipped.find(">", inner_start)
                inner_end   = snipped.find("<", inner_start)

    try:
        if multiple == False:
            bib_info.append(sammler[0])
        else:
            coll = sammler[0]
            for i in range(1, len(sammler)):
                coll = coll + '; ' + sammler[i]
            bib_info.append(coll)

    except:
        bib_info.append(" ")
    return  bib_info, sammler

def sub_extract_bib_from_pubmed_authors(bib_info, site):
    # specific for authors and country; therefore own function
    from definitions import cut_country

    weg, lastnames          = sub_extract_bib_from_pubmed(list(), site, "AuthorList", "LastName")           # Last Names
    weg, initials           = sub_extract_bib_from_pubmed(list(), site, "AuthorList", "Initials")           # Initials
    weg, country            = sub_extract_bib_from_pubmed(list(), site, "AffiliationInfo", "Affiliation")   # Country

    bib_info.append(str(len(lastnames)))                                       # number of authors appended

    # collecting authors
    try:
        if lastnames != list():                                             # are there authors?
            if len(lastnames) == len(initials):                                 # are there as many initials as lastnames
                author_string       = lastnames[0] + ', ' + initials[0]         # enter first author
                for i in range(1, len(lastnames)):
                    author_string   = author_string+ '; ' + lastnames[i] + ', ' + initials[i]   # add remaining authors
            else:                                                               # are there too many or too few initials. sometimes happens. with this code there is no way of knowing which initial belongs where and which is missing; so all are excluded (pubmed example: 20118170)
                author_string       = lastnames[0]
                for i in range(1, len(lastnames)):
                    author_string   = author_string + '; ' + lastnames[i]
            bib_info.append(author_string)                                      # names of authors appended
        else:                                                                   # no authors but collective found
            weg, other          = sub_extract_bib_from_pubmed(list(), site, "AuthorList", "CollectiveName")           # Last Names
            other_string        = other[0]
            for i in range(1, len(other)):
                other_string    = other_string + '; ' + other[i]
            bib_info.append(other_string)      # Collective
            #bib_info.append(' ')        # no initials for Collective
    except:
        if len(bib_info) <= 4: # was there already something written? no? set empty
            bib_info.append(' ') # last names


    # collecting country
    try:
        bib_info.append(cut_country(country[0])) # only first country
    except:
        bib_info.append(" ")

    return bib_info

def reduce_search_terms_number(input, number):
    # cuts search terms because pubmed seems to have problems with too many search terms
    from definitions import find_earliest_end
    start   = 0
    word    = list()
    while (start < len(input)) & (len(word) < number):
        end     = find_earliest_end(input, start, einschluss=[" ", "-", ".", ";"])
        word.append(input[start:end].strip())
        start   = end + 1

    output = ""
    for i in word:
        output  = output + " " + i

    return output.strip()

def clear_logical_relations(input):
    input = input.replace(" and ", " ")
    input = input.replace(" and,", " ")
    input = input.replace(" and;", " ")
    input = input.replace(" or ", " ")
    input = input.replace(" or,", " ")
    input = input.replace(" or;", " ")
    input = input.replace(" a ", " ")
    input = input.replace(" A ", " ")
    input = input.replace(" for ", " ")
    input = input.replace(" in ", " ")
    input = input.replace(" of ", " ")
    input = input.replace("  ", " ")
    return input

def sub_extract_cited_by(http, bib_info, pmid):
    #mainlink        = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/elink.fcgi?dbfrom=pubmed&linkname=pubmed_pmc_refs&id="
    mainlink = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/elink.fcgi?dbfrom=pubmed&linkname=pubmed_pubmed_citedin&id="
    sublink         = mainlink + pmid
    site            = http.request("GET", sublink).data.decode("utf-8", "ignore")

    weg, pmids      = sub_extract_bib_from_pubmed(list(), site=site, outer="LinkSetDb", inner="Id", multiple=True)
    bib_info.append(str(len(pmids)))
    return pmids

def sub_extract_cited_by_pubmed(browser, http, bib_info, toplevel_doi, parent_doi, wos_url, depth, depth_max, apmid, correction, max_results=5000):
    from definitions import is_doi, merge_different_sources
    from plugins_webofscience import identify_correct_wos_entry, general_search_wos

    pm_idx                  = idx_header("PubmedID") + correction
    pmids                   = sub_extract_cited_by(http, list(), apmid)

    for p in range(0, len(pmids)):
        do_it               = True

        # check for present parent_doi
        for i in range(0, len(bib_info[1])):
            if bib_info[1][i] == parent_doi:
                try:
                    # check if pubmed id is already there
                    a       = bib_info[pm_idx][i].index(pmids[p])
                    do_it   = False
                    bib_info[3][i]  = "1" # set cited by Pubmed to true
                except: pass

        if do_it == True:
            bib_info_pub    = extract_bib_from_pubmed(http, pmids[p])

            if is_doi(bib_info_pub[0]):
                urls, browser   = general_search_wos(browser, http, bib_info_pub[0], max_results=max_results, search_tag="DOI", pubmed=False)
                bib_info_wos    = identify_correct_wos_entry(browser, urls, bib_info_pub[0], "DOI")
            else:
                urls, browser   = general_search_wos(browser, http, bib_info_pub[2], max_results=max_results, search_tag="Title", pubmed=False)
                bib_info_wos    = identify_correct_wos_entry(browser, urls, bib_info_pub[2], "Title")

            bib_info_cochlib    = empty_bib()

            new_bib_info, weg   = merge_different_sources(bib_info_pub, bib_info_wos, bib_info_cochlib)

            new_bib_info.insert(0, toplevel_doi)
            new_bib_info.insert(1, parent_doi)
            new_bib_info.insert(2, str(depth))
            new_bib_info.insert(3, "1")
            new_bib_info.insert(4, "0")

            merge_bib_info(bib_info, new_bib_info)

    return browser