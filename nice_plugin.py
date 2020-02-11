def search_in_nice(data, http):
    from definitions import unify_collector, no_full_stop, is_doi, empty_guidelines

    collector           = [[],[]] # [list() for n in data]

    #collector[0]        = search_on_nice_site(data[0], http, "standard")
    #collector[1]        = search_on_nice_site('"' + no_full_stop(data[1]) + '"' + " " + data[2], http, "standard")
    if is_doi(data[0]):
        collector[0]        = search_on_nice_site(data[0], http, "evidence")
    else: collector[0]  = empty_guidelines()
    collector[1]        = search_on_nice_site('"' + no_full_stop(data[1]) + '"' + " " + data[2], http, "evidence")

    result              = unify_collector(collector)

    return result


##########################################################
def search_on_nice_site(data, http, stype):
    from definitions import empty_guidelines, simplify_text
    if stype == "standard":
        main_url    = "https://www.nice.org.uk/search?ps=100&pa="
    elif stype == "evidence":
        main_url    = "https://www.evidence.nhs.uk/search?ps=100&pa="
    searchq         = simplify_text(data, ausnahmen=[" ", "-", "/", "1", "2", "3", "4", "5", "6", "7", "8", "9", "0", ".", "_", "(", ")", '"']).replace(" ", "+")

    loop            = 1
    runner          = 1
    result          = empty_guidelines()
    while loop == 1:
        site        = http.request("GET", main_url + str(runner) + "&q=" + searchq).data.decode("utf-8", "ignore")
        if stype == "standard":
            result  = parse_nice_site_results(site, result)
        elif stype == "evidence":
            result  = parse_nice_evidence_results(site, result)
        runner          = runner + 1
        if (len(result[1]) == 0) | ((len(result[1]) % 100) != 0):
            loop    = 0
    return result

##########################################################
def parse_nice_evidence_results(cont, result):
    from definitions import clear_text_from_inclusions, find_earliest_end, clearer_text
    # ["DOI", "Title", "hit quot", "id", "evidence-level", "society", "url", "in_awmf", "in_nice", "in_tripdb"]

    start           = cont.find('class="media"')
    while start > -1:
        end         = cont.find('class="media"', start + 5)
        if end == -1: end = len(cont)
        block       = cont[start:end]

        # url
        startb      = block.find("media-heading")
        startb      = block.find('href="', startb) + len('href="')
        endb        = block.find('"', startb)
        result[6].append(block[startb : endb])

        # title
        startb      = block.find(">", endb) + 1
        endb        = block.find("</a>", startb)
        title       = clear_text_from_inclusions(block[startb: endb]).strip()
        result[1].append(title)

        # society/Journal
        startb      = block.find('class="media-meta"', endb)
        endb        = block.find('</div>', startb)
        subblock    = block[startb : endb]
        if subblock.find('class="media-source"') > -1:
            startsb = subblock.find('class="media-source"')
            startsb = subblock.find(">", startsb) + 1
            endsb   = subblock.find("<", startsb)
            result[5].append(subblock[startsb : endsb])
        elif subblock.find("Publisher:") > -1:
            startsb = subblock.find("Publisher:") + len("Publisher:")
            endsb   = len(subblock)
            result[5].append(clearer_text(subblock[startsb : endsb]).strip())
        else:
            result[5].append(" ")

        # evidence-level
        startb      = block.find("read-summary  pull-left", endb)
        startb      = block.find("<a href", startb)
        startb      = block.find(">", startb) + 1
        endb        = block.find("</a", startb)
        result[4].append(block[startb: endb].strip())

        result[0].append(" ")
        result[2].append(" ")
        result[3].append(" ")
        result[7].append("0")
        result[8].append("1")
        result[9].append("0")

        start       = cont.find('class="media"', start + 5)

    return result

##########################################################
def parse_nice_site_results(cont, result):
    from definitions import clear_text_from_inclusions, find_earliest_end
    # ["DOI", "Title", "hit quot", "id", "evidence-level", "society", "url", "in_awmf", "in_nice", "in_tripdb"]

    start           = cont.find('class="media-body"')
    while start > -1:
        end         = cont.find('class="media-body"', start + 5)
        if end == -1: end = len(cont)
        block       = cont[start:end]

        # title
        startb      = block.find("media-heading")
        startb      = block.find(">", startb) + 1
        endb        = block.find("</a>", startb)
        title       = clear_text_from_inclusions(block[startb : endb]).strip()
        result[1].append(title)

        # id
        id          = title[title.rfind("(") + 1 : title.rfind(")")].strip()
        result[3].append(id)

        # evidence-level
        startb      = block.find("documenttype")
        startb      = block.find(">", startb) + 1
        endb        = block.find("<", startb)
        result[4].append(block[startb : endb].strip())

        result[0].append(" ")
        result[2].append(" ")
        result[5].append(" ")
        result[7].append("0")
        result[8].append("1")
        result[9].append("0")

        start       = cont.find('class="media-body"', start + 5)

    return result