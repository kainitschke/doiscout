
def get_gesundheitsinformationen_refs():

    from definitions import initialize_http,  folder_structure
    from output_defs import write_output_endnote

    folder      = folder_structure("/home/nitschke/Downloads/")

    http        = initialize_http()

    subsites    = extract_topics(http)
    sources     = extract_sources(subsites, http)
    results     = parse_sources(sources)

    write_output_endnote(results, folder, "gesundheits.txt")


########################################################################
def extract_topics(http):
    link_pre    = "https://www.gesundheitsinformation.de/themen-von-a-bis-z.2003.de.html?filter*cats*0=5&filter*char="
    link_post   = "&filter*type=all"

    result = [[], []]

    for i in range(97, 97+26):
        print(chr(i))
        link_full   = link_pre + chr(i) + link_post

        site        = http.request("GET", link_full, timeout=10)
        site        = site.data.decode("utf-8", errors="ignore")

        start       = site.find("acc-body iq-list")
        end         = site.find("</ul>", start)
        site        = site[start : end]

        start       = start   = site.find("title=")
        runner      = 0
        while (start > -1):
            ## Titel
            start   = start + len("title=") + 1
            end     = site.find('"', start)
            title   = site[start : end]
            result[0].append(title)

            ## Link
            start   = site.find("href=", end) + len("href=") + 1
            end     = site.find('"', start)
            sublink = site[start : end]
            result[1].append(sublink.replace("amp;",""))

            runner  = runner + 1
            start   = site.find("title=", end)

    return result

########################################################################
def extract_sources(subsites, http):
    link_pre        = "https://www.gesundheitsinformation.de/"
    result          = [[], []]

    for i in range(0, len(subsites[1])):
        print(subsites[0][i])
        link_full       = link_pre + subsites[1][i]
        site            = http.request("GET", link_full, timeout=10)
        site            = site.data.decode("utf-8", errors="ignore")

        start           = site.find('title="Quellen"')
        start           = site.find("acc-body acc-body-first", start)
        end             = site.find("</div>", start)
        site            = site[start : end]

        start           = site.find("<p>")
        while start > -1:
            start       = start
            end         = site.find("</p>", start)
            sub         = site[start : end]

            substart    = sub.find(">")
            onesource   = ""
            while (substart > -1)&(substart < len(sub)-1):
                substart    = substart + 1
                subend      = sub.find("<", substart)
                onesource   = onesource + sub[substart : subend]
                substart    = sub.find(">", subend)

            result[0].append(subsites[0][i])
            result[1].append(onesource)

            start   = site.find("<p>", end)

    return result

########################################################################
def parse_sources(sources):
    header          = ["Thema", "Publication Type", "Full", "Authors", "Title", "Journal", "Year", "Pages"]
    result          = []
    for i in range(0, len(header)):
        result.append([])

    for i in range(0,len(sources[0])):
        #print(sources[1][i])
        result[0].append(sources[0][i])
        pub         = publication_type(sources[1][i])
        result[1].append(pub)
        result[2].append(sources[1][i])
        if pub == "Journal Article":
            parse_article(sources[1][i], result)
        elif pub == "Book":
            parse_book(sources[1][i], result)
        else:
            for j in range(3, len(result)):
                result[j].append(" ")


    return result

########################################################################
def publication_type(string):
    if string.find("AWMF-Registernr") > -1:
        return "AWMF-Guideline"
    if string.find(";") > -1:
        start = string.index(";")
        if string.find(":", start) > -1:
            return "Journal Article"
        return "Book"
    return "unbekannt"

########################################################################
def parse_article(string, result):
    start           = 0
    end             = string.find(".", start)
    authors         = string[start : end]
    result[3].append(authors.strip())

    start           = end + 1
    end             = string.find(".", start)
    title           = string[start : end]
    result[4].append(title.strip())

    start           = end + 1
    end             = string.find("20", start)
    if end == -1:
        end         = string.find("19", start)
    journal         = string[start : end]
    result[5].append(journal.strip())

    start           = end
    end             = start + 4
    year            = string[start : end]
    result[6].append(year.strip())

    start           = string.find(":", end) + 1
    end             = len(string)
    pages           = string[start : end]
    result[7].append(pages.strip())

########################################################################
def parse_book(string, result):
    start       = 0
    end         = string.find(".", start)
    authors     = string[start: end]
    result[3].append(authors.strip())

    start       = end + 1
    end         = string.find(".", start)
    title       = string[start: end]
    result[4].append(title.strip())

    start       = end + 1
    end         = string.find(";", start)
    journal     = string[start: end]
    result[5].append(journal.strip())

    start       = string.find("20", end)
    if start == -1:
        start   = string.find("19", end)
    end         = len(string)
    year        = string[start : end]
    result[6].append(year)

    result[7].append(" ")
