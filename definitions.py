def create_timestamp():
    import datetime
    n           = datetime.datetime.now()
    timestamp   = "%04d%02d%02d_%02d%02d%02d" % (n.year, n.month, n.day, n.hour, n.minute, n.second)
    return timestamp

################################################################

# def read_ids_from_text(file_loc):
#     show_string = 'Reading Text File'
#     printProgressBar(0, 1, prefix=show_string, suffix="remaining: 0:00:00:00", length=50)
#     file_obj    = open(file_loc, 'r')  # open file in read
#     atext       = file_obj.read()
#     file_obj.close()
#     atext = atext.replace(' ', '')
#     printProgressBar(1, 1, prefix=show_string, suffix="remaining: 0:00:00:00", length=50)
#     result      = preprocess_ids(atext)
#     return result


def preprocess_ids(id_txt, not_this_time=list()):

    result      = list()
    anf         = 0
    ende        = id_txt.find('\n', anf + 1)
    snipped     = id_txt[anf : ende]
    while anf > -1:
        act_id  = cut_ids(snipped, not_this_time)
        result  = result + act_id
        anf     = id_txt.find("\n", ende) # \n wird als ein Zeichen erkannt --> also hier nicht "ende+1"
        ende    = id_txt.find("\n", anf + 1)
        if ende == -1: ende = len(id_txt)  # Notwendig, sonst letztes Zeichen ignoriert
        snipped = id_txt[anf + 1: ende]

    return result


def cut_ids(id_txt, not_this_time=list()):  # split if there are multiple IDs in a line; cuts it and returns it # works recursively
    forbidden_words = ["Prüfplancode", "CTRI/2007/091/000008", '\ufeff'] # "EudraCT", "EUDRACT",
    result          = list()
    if (id_txt.find(',') != -1)&(words_contained(',', not_this_time)==False):
        trenner     = id_txt.find(',')
        result      = result + cut_ids(id_txt[0: trenner], not_this_time) + cut_ids(id_txt[trenner + 1: len(id_txt)], not_this_time)

    elif (id_txt.find('"') != -1)&(words_contained('"', not_this_time)==False):
        trenner     = id_txt.find('"')
        result      = result + cut_ids(id_txt[0: trenner], not_this_time) + cut_ids(id_txt[trenner + 1: len(id_txt)], not_this_time)

    elif (id_txt.find(chr(9)) != -1)&(words_contained(chr(9), not_this_time)==False):
        trenner     = id_txt.find(chr(9))
        result      = result + cut_ids(id_txt[0: trenner], not_this_time) + cut_ids(id_txt[trenner + 1: len(id_txt)], not_this_time)

    elif words_contained(id_txt, forbidden_words):
        id_txt      = filter_words(id_txt, forbidden_words)
        result      = result + cut_ids(id_txt, not_this_time)

    elif (id_txt.find('http') != -1)&(words_contained('http', not_this_time)==False):
        result      = list()

    elif (id_txt.find(';') != -1)&(words_contained(';', not_this_time)==False):
        trenner     = id_txt.find(';')
        result      = result + cut_ids(id_txt[0: trenner], not_this_time) + cut_ids(id_txt[trenner + 1: len(id_txt)], not_this_time)

    elif (id_txt.find(':') != -1)&(words_contained(':', not_this_time)==False):
        trenner     = id_txt.find(':')
        result      = result + cut_ids(id_txt[0: trenner], not_this_time) + cut_ids(id_txt[trenner + 1: len(id_txt)], not_this_time)

    elif len(id_txt) == 0:
        result      = list()

    else:
        result.append(id_txt)
    return result

def words_contained(id_txt, forbidden_words):
    for word in forbidden_words:
        if id_txt.find(word) != -1:
            return True
    return False


def filter_words(id_txt, forbidden_words):
    for word in forbidden_words:
        if id_txt.find(word) != -1:
            idx = id_txt.find(word)
            return id_txt[0: idx] + id_txt[idx + len(word): len(id_txt)]


##################################################################

def get_html_files(study_ids, sources, folder):
    import datetime
    import os
    from register_search import identify_source

    show_string     = 'Downloading HTMl-Page-Data'
    ordner_anlegen(folder, 2)

    urls            = list()
    http            = initialize_http()
    start_time      = datetime.datetime.now()
    printProgressBar(0, len(study_ids), prefix=show_string, suffix="remaining: 0:00:00:00", length=50)
    for runner in range(0, len(study_ids)):
        ident       = identify_source(study_ids[runner], sources)  # check which register
        act_url     = sources[1][ident] + study_ids[runner]  # combine to URL
        urls.append(act_url)
        if os.path.exists(folder.html + study_ids[runner] + '.html') == False:
            # print(runner, study_ids[runner])
            site    = http.request('GET', act_url)  # get page data
            f       = open(folder.html + study_ids[runner] + '.html', 'wb')  # write to file
            f.write(site.data)
            f.close()
        if (ident == 3) & (os.path.exists(folder.html + study_ids[runner] + '_res' + '.html')== False):
            res_url = sources[2][ident].replace("???", study_ids[runner])
            site    = http.request('GET', res_url)  # get page data
            f       = open(folder.html + study_ids[runner] + '_res'  + '.html', 'wb')  # write to file
            f.write(site.data)
            f.close()


        printProgressBar(runner+1, len(study_ids), prefix=show_string,
                         suffix=remaining_time(start_time=start_time, step=runner, max=len(study_ids)),
                         length=50)
    return urls

##################################################################

def clearer_text(atext):
    atext           = atext.replace("20%", chr(32))
    atext           = atext.replace("&quot;", '"')
    atext           = atext.replace("&#039;", "'")
    atext           = atext.replace("&nbsp;", chr(32))
    return atext

def string_2_html(string, direction="to_html", ausschluss = list()):
    db  = [["%", "%25"], ## MUST BE FIRST!!!
           ["'", "%27"],
           ["-", "%96"],
           ["ä", "%E4"],
           ["Ä", "%C4"],
           ["ö", "%F6"],
           ["Ö", "%D6"],
           ["ü", "%FC"],
           ["Ü", "%DC"],
           ["é", "%E9"],
           ["É", "%C9"],
           ["è", "%E8"],
           ["È", "%C8"],
           ["ê", "%EA"],
           ["Ê", "%CA"],
           ["ò", "%F2"],
           ["Ò", "%D2"],
           ["ó", "%F3"],
           ["Ó", "%D3"],
           ["â", "%E2"],
           ["Â", "%C2"],
           ["á", "%E1"],
           ["Á", "%C1"],
           ["à", "%E0"],
           ["À", "%C0"],
           ["ô", "%F4"],
           ["Ô", "%D4"],
           ["û", "%FB"],
           ["Û", "%DB"],
           ["ñ", "%F1"],
           ["œ", "%9C"],
           ["ç", "%E7"],
           ["(", "%28"],
           [")", "%29"],
           ['[', "%5B"],
           [']', "%5D"],
           ['/', "%2F"],
           [chr(32), "%20"]]

    if direction == "to_html":
        for i in range(0, len(db)):
            try:
                if ausschluss.index(db[i][0]):
                    pass
            except:
                string  = string.replace(db[i][0], db[i][1])

    # has to backwards because otherwise % is replaced too early
    elif direction == "from_html":
        for i in range(len(db)-1 , -1, -1):
            string  = string.replace(db[i][1], db[i][0])

    return string

def simplify_text(atext, ausnahmen=list()):           # turns every capital letter into small letter. rest is removed
    if len(atext) > 0:
        if   (ord(atext[0]) >= 97)&(ord(atext[0]) <= 122):  # is small letter
            u       = atext[0]
        elif (ord(atext[0]) >= 65)&(ord(atext[0]) <= 90):   # is captial letter
            u       = chr(ord(atext[0]) + 32)               # turn to small letter
        else:
            if words_contained(atext[0], ausnahmen) == True:
                u   = atext[0]
            else:
                u       = ""                                    # everything else is erased
        atext       = u + simplify_text(atext[1:len(atext)], ausnahmen)# rest recursively
    return atext

def decapitalize(atext):
    if len(atext) > 0:  # is empty
        if isinstance(atext, list) == False:    # is a string; not a list
            if (ord(atext[0]) <= 90) & (ord(atext[0]) >= 65):
                small   = chr(ord(atext[0]) + 32)
            else:
                small   = atext[0]
            return small + decapitalize(atext[1:len(atext)])
        else:                                   # is a list; not a string
            for i in range(0, len(atext)):
                atext[i]    = decapitalize(atext[i])
            return atext
    else:
        return ""

def remove_multiple_spaces(input):
    output     = input.replace("\n", " ")
    output     = output.replace("  ", " ")
    if output != input:
        output = remove_multiple_spaces(output)
    return output

##################################################################
def cut_country(string):

    try:
        string              = string + ","
        sammler             = list()

        string              = string.replace(",", ", ")
        string              = string.replace("  ", " ")
        forbidden_words     = ["Electronic", "address", "@", "E-Mail", "e-mail", "email", "Email"]
        start               = 0
        end                 = find_earliest_end(string, start, einschluss=[", ", ". ", chr(32)], check_last_point=False)

        while end < len(string) - 1: #(start > -1)&(end > -1):
            if (words_contained(string[start: end], forbidden_words) == False) & (string[start: end] != "") & (is_number(string[start: end], 80) == False):
                sammler.append(string[start: end].replace(".",""))
            start           = end + 1
            end             = find_earliest_end(string, start, einschluss=[", ", ". ", ",", chr(32)], check_last_point=False)

        org                 = ["Kingdom", "California", "Illinois", "Berkeley", "Wisconsin", "States", "England", "Scotland", "Wales", "Kong",  "Россия"]
        rep                 = ["UK",      "UK",         "USA",      "USA",      "USA",       "USA",     "UK",     "UK",       "UK",    "China", "Russia"]

        for i in range(0, len(org)):
            sammler         = [rep[i] if x == org[i] else x for x in sammler]

        for i in range(len(sammler), 0, -1):
            cl              = sammler[i-1]
            if is_country(cl):
                return cl

        return " "
    except:
        return " "

##################################################################
def is_country(string):
    countries = ["Afghanistan", "Africa", "Albania", "Algeria", "Andorra", "Angola", "Antigua and Barbuda", "Arabia", "Argentina", "Armenia", "Aruba", "Australia", "Austria", "Azerbaijan", "The Bahamas", "Bahrain", "Bangladesh", "Barbados", "Belarus", "Belgium", "Belize", "Benin", "Bermuda", "Bhutan", "Bolivia", "Bosnia", "Bosnia and Herzegovina", "Botswana", "Brazil", "Brunei", "Bulgaria", "Burkina Faso", "Myanmar", "Burma", "Burundi", "Cambodia", "Cameroon", "Canada", "Cape Verde", "Central African Republic", "Chad", "Chile", "China", "Taiwan", "Cook Islands", "Colombia", "Comoros", "Zaire", "Republic of the Congo", "Costa Rica", "Côte d'Ivoire", "Croatia", "Cuba", "Cyprus", "Republic of Cyprus", "Czech Republic", "Denmark", "Djibouti", "Dominica", "Dominican Republic", "East Timor", "Ecuador", "Egypt", "Emirates", "El Salvador", "Equatorial Guinea", "Eritrea", "Estonia", "Ethiopia", "Fiji", "Finland", "France", "Faroe Islands", "Gabon", "The Gambia", "Gambia", "Georgia", "Germany", "Ghana", "Greece", "Grenada", "Guatemala", "Guinea", "Guinea-Bissau", "Guyana", "Haiti", "Herzegovina", "Holy See", "Honduras", "Hungary", "Iceland", "India", "Indonesia", "Iran", "Iraq", "Ireland", "Israel", "Italy", "Ivory Coast", "Jamaica", "Japan", "Jordan", "Kazakhstan", "Kenya", "Kiribati", "Korea", "Kuwait", "Kyrgyzstan", "Lanka", "Laos", "Latvia", "Lebanon", "Lesotho", "Liberia", "Libya", "Liechtenstein", "Lithuania", "Luxembourg", "Republic of Macedonia", "Madagascar", "Malawi", "Malaysia", "Maldives", "Mali", "Malta", "Marshall Islands", "Mauritania", "Mauritius", "Mexico", "Federated States of Micronesia", "Moldova", "Monaco", "Mongolia", "Montenegro", "Morocco", "Mozambique", "Myanmar", "Namibia", "Nauru", "Nepal", "Netherlands", "New Zealand", "Zealand", "Nicaragua", "Niger", "Nigeria", "Niue", "North Korea", "Norway", "Oman", "Pakistan", "Palau", "Palestine", "Panama", "Papua New Guinea", "Paraguay", "Peru", "Rica", "Philippines", "Poland", "Portugal", "Qatar", "Romania", "Russia", "Rwanda", "Saint Kitts and Nevis", "Saint Lucia", "Saint Vincent and the Grenadines", "Samoa", "San Marino", "São Tomé and Príncipe", "Saudi Arabia", "Senegal", "Serbia", "Seychelles", "Sierra Leone", "Singapore", "Slovakia", "Slovenia", "Solomon Islands", "Somalia", "South Africa", "South Korea", "South Sudan", "Spain", "Sri Lanka", "Sudan", "Suriname", "Swaziland", "Sweden", "Switzerland", "Syria", "Taiwan", "Tajikistan", "Tanzania", "Thailand", "Togo", "Tonga", "Trinidad and Tobago", "Tunisia", "Turkey", "Turkmenistan", "Tuvalu", "Uganda", "Ukraine", "United Arab Emirates", "United Kingdom", "UK", "United States", "USA", "Uruguay", "Uzbekistan", "Vanuatu", "Vatican City", "Venezuela", "Vietnam", "Yemen"]
    try:
        countries.index(string)
        return True
    except:
        return False

def is_number(string, percent = 100):
    if len(string) > 0:
        num             = 0
        txt             = 0
        for i in range(0, len(string)):
            if (ord(string[i]) >= 48) & (ord(string[i]) <= 57):
                num     = num + 1
            else:
                txt     = txt + 1
        if (num / (num + txt)) >= (percent / 100):
            return True
        else:
            return False
    else:
        return False

def is_link(string):
    try:
        if string[0:4] == "http":
            return True
        else:
            return False
    except:
        return False

def is_doi(doi):
    try:
        if doi[0:3] == "10.":
            return True
        else:
            return False
    except:
        return False

def titles_2_dois(dois): # search all input for dois and titles and tries to find DOIs for the titles
    import datetime
    from pubmed_plugins import titles_2_dois_by_pubmed
    show_string = 'Titles to Dois'
    printProgressBar(0, len(dois), prefix=show_string, suffix="remaining: 0:00:00:00", length=50)
    start_time  = datetime.datetime.now()

    is_first    = True
    for i in range(0, len(dois)):
        if is_doi(dois[i]) == False:
            if is_first == True:            # only when first, to save time, if unnecessary
                http    = initialize_http()
                is_first= False
            
            sammler     = titles_2_dois_by_pubmed(dois[i], http)
            if sammler != list():
                if (sammler[0] != list()) & (sammler[0] != chr(32)):
                    dois[i]     = sammler

        printProgressBar(i + 1, len(dois), prefix=show_string,
            suffix=remaining_time(start_time=start_time, step=i, max=len(dois)),
            length=50)
    return dois

def extract_bib_info(inputs, browser, http, max_pmids=500, silent = False):
    import datetime
    from pubmed_plugins import search_pubmed_for_pmids, identify_correct_pmid, empty_bib, merge_bib_info
    from definitions import initialize_browser

    if silent == False:
        show_string             = 'Extracting Bib Info'
        printProgressBar(0, len(inputs), prefix=show_string, suffix="remaining: 0:00:00:00", length=50)
        start_time              = datetime.datetime.now()

    bib_info                = empty_bib()
    failed                  = list()
    #dois                    = list()

    for i in range(0, len(inputs)):
        # print(inputs[i])

        retry = 1 # loop so there is a retry if an error occurs
        while retry < 5:
            try:
                new_bib_info, att, browser = collect_bib_info_different_sources(browser, http, inputs[i], "", max_pmids=max_pmids)
                retry = 100
            except:
                retry = retry + 1
                try:
                    geckopath = browser.geckopath
                    folders   = browser.folder
                    browser.close()
                except: pass
                browser = initialize_browser(geckopath, folders)

        if att == 1:
            failed.append(inputs[i])

        bib_info            = merge_bib_info(list(bib_info), list(new_bib_info))

        if silent == False:
            printProgressBar(i + 1, len(inputs), prefix=show_string,
                             suffix=remaining_time(start_time=start_time, step=i, max=len(inputs)),
                             length=50)

    return bib_info, failed, bib_info[0], browser

def collect_bib_info_different_sources(browser, http, input, url, max_pmids=500):
    from pubmed_plugins import identify_correct_pmid, search_pubmed_for_pmids, empty_bib
    from plugins_webofscience import general_search_wos, identify_correct_wos_entry
    from plugin_cochrane_library import search_in_cochrane_library, extract_bib_info_from_cochrane_library

    # is it a doi
    if is_doi(input):
        ## pubmed
        pmids                   = search_pubmed_for_pmids("DOI", input, http, max_pmids=500)
        bib_info_pub            = identify_correct_pmid(http, pmids, input, "DOI")
        ## web of science
        urls, browser           = general_search_wos(browser, http, input, max_results=20, search_tag="DOI", pubmed=False)
        bib_info_wos            = identify_correct_wos_entry(browser, urls, input, "DOI")
        ## cochrane
        bib_info_cochlib        = empty_bib()
        #bib_info_cochlib        = extract_bib_info_from_cochrane_library(http, input)


    # is it emtpy
    elif input == " ":
        bib_info_wos            = list()
        bib_info_pub            = list()
        bib_info_cochlib        = list()

    # is it a link
    elif is_link(input):
        bib_info_wos            = list()
        bib_info_pub            = list()
        bib_info_cochlib        = list()

    # is it a title
    else:
        pmids                   = search_pubmed_for_pmids("title", input, http, max_pmids=max_pmids)
        bib_info_pub            = identify_correct_pmid(http, pmids, input, "title")
        urls, browser           = general_search_wos(browser, http, input, max_results=100, search_tag="Title", pubmed=False)
        bib_info_wos            = identify_correct_wos_entry(browser, urls, input, "Title")
        bib_info_cochlib        = list()
        #print("cochrane missing\n")

    bib_info, attention         = merge_different_sources(bib_info_pub, bib_info_wos, bib_info_cochlib, input)

    return bib_info, attention, browser


def merge_different_sources(bib_info_pub, bib_info_wos, bib_info_cochlib, input=" "):
    from pubmed_plugins import empty_bib

    # getting infos of pubmed and wos together
    if (bib_info_pub == list()) & (bib_info_wos == list()) & ((bib_info_cochlib == list())|(bib_info_cochlib == empty_bib())):  # not found anything in pubmed or wos
        attention               = 1
        bib_info                = empty_bib()

        if is_doi(input):  # check if doi (not found in pubmed and wos): add as doi
            bib_info[0]         = input
        else:  # not doi; therefore store it as title
            bib_info[2]         = input

        bib_info[-2]            = " " # url

    elif bib_info_pub != list():  # found only in pubmed
        attention               = 0
        bib_info                = list(bib_info_pub)

    elif bib_info_pub == list():  # found only in wos
        attention               = 0
        bib_info                = list(bib_info_wos)

    elif bib_info_cochlib == list():
        attention               = 0
        bib_info                = list(bib_info_cochlib)

    # add Wos (resp. cochrane library info) info to pubmed info (if missing there)
    for col in range(0, len(bib_info)):
        if ((bib_info[col] == list()) | (bib_info[col] == chr(32)) | (bib_info[col] == "")) & (bib_info_wos != list()):
            bib_info[col]       = bib_info_wos[col]
        if (bib_info[col] == list()) | (bib_info[col] == chr(32)) | (bib_info[col] == ""):
            try: bib_info[col]       = bib_info_cochlib[col]
            except: pass

    if bib_info_wos != list():
        if is_country(bib_info_wos[5]):
            bib_info[5]             = bib_info_wos[5]
    if bib_info_pub != list():
        if is_country(bib_info_pub[5]):
            bib_info[5]             = bib_info_pub[5]
    if (bib_info_cochlib != list())&(bib_info_cochlib != empty_bib()):
        if is_country(bib_info_cochlib[5]):
            bib_info[5]             = bib_info_cochlib[5]

    bib_info[-2] = ""
    try: bib_info[-2] = bib_info_pub[-2]
    except: pass
    try: bib_info[-2] = bib_info[-2] + '; ' + bib_info_wos[-2]
    except: pass
    try: bib_info[-2] = bib_info[-2] + '; ' + bib_info_cochlib[-2]
    except: pass

    # replace " so the result writing and reading in excel and libre office is not disturbed
    if bib_info[2] != []:
        bib_info[2]                 = bib_info[2].replace('"', "'")

    return bib_info, attention


def compare_title(title_a, title_b):
    # compares if two titles are exactly identical
    # just compares a-z and A-Z, other signs are excluded beforehand
    title_a     = simplify_text(title_a)
    title_b     = simplify_text(title_b)
    if title_a == title_b:
        return True
    else:
        return False

def empty_guidelines(title = False):
    header = ["DOI", "Title", "hit quot", "id", "evidence-level", "society", "guideline-url", "in_awmf", "in_nice", "in_tripdb"]
    if title == True:
        return header
    elif title == "alternative":
        return ["Parent-DOI", "hit quot", "id", "evidence-level", "society", "guideline-url", "in_awmf", "in_nice", "in_tripdb"]
    else:
        result  = []
        for i in range(0, len(header)):
            result.append(list())
        return result

##################################################################

def find_earliest_end(cont, start, ausschluss = [], einschluss = [], check_last_point=True):
    signs = [" ", "\n", "\t", "<", ">", '"', ":", ";"]
    signs = signs + einschluss
    end = len(cont)
    for i in signs:
        if cont.find(i, start) < end:
            if not i in ausschluss:
                if cont.find(i, start) > -1:
                    end = cont.find(i, start)
    if check_last_point == True:
        if cont[end - 1] == ".": end = end - 1  # sometimes thereis an . because of citation; is cutted here
    return end

def follow_to_pubmed_for_doi(sublink, http):   # should also be able to detect DOIs otherwhere
    site        = http.request("GET", sublink, timeout=10)
    site        = site.data.decode("utf-8", errors="ignore")
    start       = site.find("doi")
    start       = site.find("10.", start)
    end         = find_earliest_end(site, start, ausschluss=[":"])
    doi         = site[start:end]
    return doi

def clear_signs(astring):
    signs       = ["\n", "\t", "<labels>", "[---]*","&nbsp", "<label>", "</labels>", "</label>", '"publication"', ">", "<"]
    for i in signs:
        astring = astring.replace(i,"")
    return astring

def clear_text_from_inclusions(text, init = "<", fin = ">"):
    # searches for the init and fin and deletes it from text; is thought for a link or text which got html in them
    start       = text.find(init)
    while start > -1:
        end     = text.find(fin, start + 1)
        if end == -1: end = len(text)
        text    = text[0:start] + text[end + 1 : len(text)]
        start   = text.find(init)
    return text

def clear_text_from_exclusion(text, init = "[", fin = "]"):
    # extracts somethings between two signs/word; is thought for non-international titles where there is the original title in brackets
    start       = text.find(init)
    end         = text.find(fin, start + 1)
    if start == -1: start = 0
    if end   == -1: end   = len(text)
    return text

def only_first_author(results):
    for i in range(0, len(results)):
        end         = find_earliest_end(results[i], start=0, ausschluss=["-","ä","ü","ö"], einschluss=[" ", ",", ";" ])
        results[i]  = results[i][0:end]
    return results

def no_full_stop(input):
    if input[-1] == '.':  return input[0 : - 1]
    else: return input

##################################################################

def read_dois_from_wos_search(atext):
    dois                = list()

    start               = 0#atext.find("\n\n") + 3

    while start > -1:
        start_next      = atext.find("\n\n",   start + 2)

        startdoi        = atext.find("\nDI",   start) + 3
        if (startdoi <= 2) | ((startdoi >= start_next) & (start_next > -1)):
            startdoi    = atext.find("\nTI", start) + 3
            if startdoi > 2: #sometimes emtpy lines in in Wos
                end     = atext.find("\n", startdoi)
                while atext[end+1] == " ":
                    end = atext.find("\n", end + 1)
            else:
                end     = startdoi
        else: # is doi
            end         = atext.find("\n", startdoi)

        doi             = remove_multiple_spaces(atext[startdoi : end].strip())
        doi             = simplify_text(doi, ausnahmen=["1", "2", "3", "4", "5", "6", "7", "8", "9", "0", ".", "(", ")", "_", "/", chr(32), "-"])
        if doi!="":
            dois.append(doi)

        start           = start_next

    return dois

def read_dois_from_ncbi_search(atext):
    dois            = list()
    identifier      = "\n"
    identifier_doi  = "doi:"

    # Berücksichtigen, dass manchmal keine DOIs da. Dann Title merken
    start           = atext.find(identifier)                # start this entry
    startn          = atext.find(identifier,     start + 2) # next entry
    startd = atext.find(identifier_doi, start)              # first doi

    while (start > -1)&(startn > -1):                       # startn also controlled, because csv ends with \n so otherwise here comes an infinity loop
        title       = False                                 # set to false for later so doi is used
        if ((startd > startn) & (startn > -1)) | (startd == -1):  # if DOI > subsequent record --> no doi --> save title
            title   = True

        if title == False:      # there is a doi. take it
            startd  = atext.find("10.",        startd + 1)  # find start of doi
            end     = find_earliest_end(atext, startd)      # end of doi
            dois.append(atext[startd : end])                # append doi
        else:                   # there is no doi. take title
            startd  = atext.find('"', start) + 1            # start of title
            end     = atext.find('"', startd)               # end of title
            if atext[end + 1] == '"':                        # necessary, because there are quotation marks in some titles. they are appear as "" so all double quotations are skipped
                while atext[end+1] == '"':
                    end = atext.find('"', end + 2)

            dois.append(atext[startd : end])                # append title

        dois[-1]    = dois[-1].replace('""', '"')

        start       = atext.find(identifier, end + 1)       # search next record
        startn      = atext.find(identifier, start + 2)     # search the record after that
        startd      = atext.find(identifier_doi, start + 1) # serach DOI

    return dois

def read_info_doi_scout_file(afile, search_idxs="all"):
    import xlrd
    print("Started Reading DoiScout-File")
    dats        = xlrd.open_workbook(afile)
    sheet       = dats.sheet_by_index(0)

    all_idx     = []
    for i in range(0, sheet.ncols):
        all_idx.append(sheet.cell_value(0, i))#.capitalize())
    if search_idxs == "all":
        search_idxs = all_idx

    spec_idx    = []
    for i in search_idxs:
        spec_idx.append(all_idx.index(i))#.capitalize()))

    info        = []
    for j in range(0, len(spec_idx)):
        info.append(list())
        for i in range(1, sheet.nrows):
            info[j].append(sheet.cell_value(i, spec_idx[j]))

    print("Finished Reading DoiScout-File")
    return info, search_idxs

##################################################################

def download_pdfs_from_dois(dois, folder, browser):
    doi_url = "https://dx.doi.org/"

    import os
    from website_plugins import open_pdf_url, try_ovid
    import datetime
    from time import sleep

    show_string = 'Downloading PDFs'

    missings    = list();
    ordner_anlegen(folder, 1)
    http        = initialize_http()
    #browser     = initialize_browser(gecko_path, folder)
    start_time  = datetime.datetime.now()
    for i in range(0, len(dois)):  # !!! ACHTUNG: Hier manchmal verändert für Test schneller
        #print(i)
        if dois[i].find('\x00') > -1:
            missings.append(dois[i])
        else:
            if os.path.exists(folder.pdf + doi_2_filename(dois[i] + ".pdf")) == False:

                ## open website
                try:
                    browser = open_page(browser, doi_url + dois[i])
                except:
                    try:
                        sleep(1)
                        browser = open_page(browser, doi_url + dois[i])
                    except:
                        to_click = False

                ## open PDF
                ordner_leeren(folder)
                org_url     = ""
                try:
                    toclick, org_url, browser = open_pdf_url(browser, http, dois[i], folder)
                except:  # it sometimes happen, that large files exceed the timeout. that results in an error here. therefore, catching error, waiting and hoping
                    toclick = True
                    sleep(5)

                ## Download PDF or try OVID
                if toclick == True:
                    save_pdf_with_loop(browser, folder, 30)
                success = move_downloaded_pdf(dois[i], folder)
                if success == False:
                    try_ovid(browser, http, dois[i], folder, org_url)
                    success = move_downloaded_pdf(dois[i], folder)
                if success == False:
                    missings.append(dois[i])
                    #print(dois[i])

        printProgressBar(i+1, len(dois), prefix=show_string,
                         suffix=remaining_time(start_time=start_time, step=i, max=len(dois)),
                         length=50)

    return missings, browser


def save_pdf_with_loop(browser, folder, loop_length):
    from datetime import datetime
    from time import sleep
    import os
    sleep(.4)
    start = datetime.now()
    max_wait_time = loop_length
    # checker = 0
    # while (checker == 0) & ((datetime.now() - start).seconds <= max_wait_time):
    while (datetime.now() - start).seconds <= max_wait_time:
        try:
            if len(os.listdir(folder.tmp)) < 1:
                download_obj = browser.find_element_by_id("download")
                download_obj.click()
                sleep(.6)
            else:
                return True
        except:
            sleep(1)
    return False


def move_downloaded_pdf(doi, folder):
    import os
    from time import sleep
    from datetime import datetime
    sleep(1.5)
    newfile = doi_2_filename(doi) + ".pdf"
    tmpfile = os.listdir(folder.tmp)

    start = datetime.now()
    max_wait = 10

    ## check whether there are any files
    while (len(tmpfile) < 0) & ((datetime.now() - start).seconds <= max_wait):
        sleep(1)
        tmpfile = os.listdir(folder.tmp)

    tmpfile = os.listdir(folder.tmp)
    ## delete all but one file
    if len(tmpfile) > 1:
        for i in range(1, len(tmpfile)):
            try:
                os.remove(folder.tmp + tmpfile[i])
            except:
                pass

    ## final check whether there is at least one file; otherwise failure
    if len(os.listdir(folder.tmp)) < 1:
        return False

    ## check whether file size remains stable or changing
    tmpfile = os.listdir(folder.tmp)
    oldsize = 0
    try:
        while oldsize != os.stat(folder.tmp + tmpfile[
            0]):  # loop for checking if file size is still changing resp. is still being written
            oldsize = os.stat(folder.tmp + tmpfile[0])
            sleep(1)
    except:
        pass

    tmpfile = os.listdir(folder.tmp)
    try:
        os.rename(folder.tmp + tmpfile[0], folder.pdf + newfile)
    except:
        return False
    sleep(.25)
    return True


def ordner_leeren(folder): # taking out the trash; emptying folders
    import os
    from time import sleep
    sleep(.1)
    tmpfiles = os.listdir(folder.tmp)
    for i in range(0, len(tmpfiles)):
        try:
            os.remove(folder.tmp + tmpfiles[i])
        except:
            pass


def doi_2_filename(doi):
    doi = doi.replace("/", "_")
    return doi


def filename_2_doi(doi):
    doi = doi.replace("_", "/")
    return doi


def month_2_number(bib_info):
    if simplify_text(bib_info[-1]) == "jan": bib_info[-1] = "1"
    if simplify_text(bib_info[-1]) == "feb": bib_info[-1] = "2"
    if simplify_text(bib_info[-1]) == "mar": bib_info[-1] = "3"
    if simplify_text(bib_info[-1]) == "apr": bib_info[-1] = "4"
    if simplify_text(bib_info[-1]) == "may": bib_info[-1] = "5"
    if simplify_text(bib_info[-1]) == "jun": bib_info[-1] = "6"
    if simplify_text(bib_info[-1]) == "jul": bib_info[-1] = "7"
    if simplify_text(bib_info[-1]) == "aug": bib_info[-1] = "8"
    if simplify_text(bib_info[-1]) == "sep": bib_info[-1] = "9"
    if simplify_text(bib_info[-1]) == "oct": bib_info[-1] = "10"
    if simplify_text(bib_info[-1]) == "nov": bib_info[-1] = "11"
    if simplify_text(bib_info[-1]) == "dec": bib_info[-1] = "12"


def daterecognition(input):
    leer            = list()
    month           = " ";  year            = " "; day             = " "

    start           = 0
    while start != -1:
        leer.append(start)
        start       = input.find(" ", start + 1)
    leer[0]         = -1
    leer.append(len(input))

    for i in range(0, len(leer) - 1):
        if (leer[i+1] - leer[i]) == 4:                  # month
            month   = [input[leer[i]+1 : leer[i+1]]]
            month_2_number(month)
            month   = month[0]
        if (leer[i+1] - leer[i]) == 5:                  # year
            year    = input[leer[i]+1 : leer[i+1]]
        if ((leer[i + 1] - leer[i]) >= 2) & ((leer[i + 1] - leer[i]) <= 3): # day
            day     = input[leer[i]+1 : leer[i+1]]

    return month, year, day


def looping(string, contents):  # finds string for looping
    for i in contents:
        if string.find(i) > -1:
            return 1
    return 0


def ordner_anlegen(folder, mode=1): # create folders
    import os
    if os.path.exists(folder.tmp) == False:
        os.mkdir(folder.tmp)
    if os.path.exists(folder.pdf) == False:
        os.mkdir(folder.pdf)
    if mode == 2:
        if os.path.exists(folder.html) == False:
            os.mkdir(folder.html)
        if os.path.exists(folder.results) == False:
            os.mkdir(folder.results)


def delete_empty_folders(folder):
    import os
    if len(os.listdir(folder.tmp))      == 0: os.rmdir(folder.tmp)
    if len(os.listdir(folder.pdf))      == 0: os.rmdir(folder.pdf)
    if len(os.listdir(folder.html))     == 0: os.rmdir(folder.html)
    if len(os.listdir(folder.results))  == 0: os.rmdir(folder.results)


def initialize_browser(gecko_path, folder):
    from selenium import webdriver
    from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
    import platform

    firefox_capabilities = DesiredCapabilities.FIREFOX
    firefox_capabilities['marionette'] = True
    firefox_capabilities['handleAlerts'] = True
    firefox_capabilities['acceptSslCerts'] = True
    firefox_capabilities['acceptInsecureCerts'] = True

    profile = webdriver.FirefoxProfile()
    profile.set_preference('browser.download.folderList', 2)  # custom location; all below is for suppressing download dialog
    profile.set_preference("browser.download.manager.showWhenStarting", False)
    profile.set_preference("browser.helperApps.alwaysAsk.force", False)
    if platform.system() == "Windows":
        profile.set_preference('browser.download.dir', folder.tmp.replace("/","\\"))
    else:
        profile.set_preference('browser.download.dir', folder.tmp)
    profile.set_preference('browser.helperApps.neverAsk.saveToDisk', 'application/pdf')
    profile.set_preference("pdfjs.disabled", True)

    #profile.set_preference('print.always_print_silent', True) # silent print dialog; but directly print
    #profile.set_preference("print.print_to_file", True);

    ## so it does not kill the RAM
    profile.set_preference("browser.cache.disk.enable", False)
    profile.set_preference("browser.cache.memory.enable", False)
    profile.set_preference("browser.cache.offline.enable", False)
    profile.set_preference("network.http.use-cache", False)

    browser = webdriver.Firefox(firefox_profile=profile, capabilities=firefox_capabilities, executable_path=gecko_path)
    browser.set_page_load_timeout(60)

    browser.set_window_size(1277, 893)
    browser.set_window_position(1283, 27)

    browser.counter     = 0
    browser.geckopath   = gecko_path
    browser.folder      = folder

    browser.minimize_window()

    return browser


def initialize_http():
    import urllib3
    http = urllib3.PoolManager()
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    return http


def close_browser(browser, folder):
    import os
    browser.close()
    # os.rmdir(folder.tmp)


def open_page(browser, url, allow_restart = True, n_runner = 10):
    ## is written so that selenium is restarted periodically because it jams RAM
    if (browser.counter > 50) & (allow_restart == True):
        from time import sleep
        # browser.counter = 0
        # browser.delete_all_cookies()
        gecko_path  = browser.geckopath
        folder      = browser.folder
        browser.close()
        browser     = initialize_browser(gecko_path, folder)
        sleep(3)

    browser.counter = browser.counter + 1

    runner          = 0
    while runner < n_runner:
        try:
            browser.get(url)
            break
        except:pass
        runner      = runner + 1

    return browser


class folder_structure:
    def __init__(self, folder, sep):
        self.html       = folder + sep + "html" + sep
        self.pdf        = folder + sep + "fulltexts" + sep
        self.tmp        = folder + sep + "tmp" + sep
        self.results    = folder + sep + "results" + sep
        self.main       = folder + sep


def remove_dublicates(alist):
    alist = sorted(set(alist), key=alist.index)
    return alist


##################################################################
def transform_to_endnote(file, path):
    from output_defs import read_bib_info_file, correct_for_endnote, write_output_endnote
    from pubmed_plugins import add_headers_bib_info

    folder = folder_structure(path[0:(len(path)-1)], "/")

    bib_info, header    = read_info_doi_scout_file(path+file)#read_bib_info_file(path, file)
    correct_for_endnote(bib_info, header, folder)

    add_headers_bib_info(bib_info, header)

    file                = file[0:-5] + "_EndnoteImport" + '.txt'#file[-5:len(file)]

    write_output_endnote(bib_info, folder, file)

    print("Endnote file: %s" % path+file)


###################################################################
#################### Cited by #####################################
###################################################################

def extract_cited_by(elements, browser, http, dois, depth, max_depth, max_results=5000):
    # gets the "cited by" of wos; not recursively, because only dois/titles arrive
    # for recursive; only urls to shorten the run time

    from plugins_webofscience import identify_correct_wos_entry, general_search_wos
    #from definitions import is_doi, remaining_time, printProgressBar
    from pubmed_plugins import empty_bib, identify_correct_pmid, search_pubmed_for_pmids, add_headers_bib_info, idx_header
    from datetime import datetime

    correction              = 5 # three additional fields

    # make empty bib
    bib_info                = empty_bib()
    for i in range(0, correction):      bib_info.append(list())

    show_string             = 'Searching Cited By Depth 0'
    start_time              = datetime.now()
    printProgressBar(0, len(dois), prefix=show_string, suffix="0:00:00:00", length=50)

    ## identify important headers
    hpub                    = idx_header("Cited_By_Pubmed")    + correction
    hwos                    = idx_header("Cited_By_WoS")       + correction
    hcoch                   = idx_header("Cited_By_Cochrane")  + correction

    for i in range(0, len(dois)):

        # get the info for the topmost level from Pubmed
        if is_doi(dois[i]):
            pmids           = search_pubmed_for_pmids("DOI", dois[i], http, max_pmids=50)
            bib_info_pub    = identify_correct_pmid(http, pmids, dois[i], "DOI")
        else:
            pmids           = search_pubmed_for_pmids("title", dois[i], http, max_pmids=50)
            bib_info_pub    = identify_correct_pmid(http, pmids, dois[i], "title")

        # get the info for the topmost level from wos
        if is_doi(dois[i]):  # DOI
            urls, browser   = general_search_wos(browser, http, dois[i], max_results=max_results, search_tag="DOI", pubmed=False)
            bib_info_wos    = identify_correct_wos_entry(browser, urls, dois[i], "DOI")
        else:  # Title
            urls, browser   = general_search_wos(browser, http, dois[i], max_results=max_results, search_tag="Title", pubmed=False)
            bib_info_wos    = identify_correct_wos_entry(browser, urls, dois[i], "Title")

        # getting Infos of Pubmed and WoS together + adding the parent information + adding it to the large bib_info database
        get_together_cited_by_wos_pub(bib_info, bib_info_wos, bib_info_pub, dois[i], dois[i], depth)

        # counting the citations of the sources
        try: cits_pub       = int(bib_info[hpub][-1])
        except: cits_pub    = 0
        try: cits_wos       = int(bib_info[hwos][-1])
        except: cits_wos    = 0
        try: cits_coch      = int(bib_info[hcoch][-1])
        except: cits_coch   = 0

        apmid               = idx_header("PubmedID") + correction
        apmid               = bib_info[apmid][-1]
        
        # call the citations, which will resume recursiveley
        if (depth < max_depth) & ((cits_pub > 0) | (cits_wos > 0) | (cits_coch > 0)):
            #print(dois[i])
            try: # if there was nothing found in wos
                wos_url     = get_wos_url(bib_info_wos[-2])
            except:
                wos_url     = " "
            browser         = sub_extract_cited_by(elements, browser, http, bib_info, dois[i], dois[i], wos_url, depth + 1, max_depth, cits_pub, cits_wos, cits_coch, apmid, correction, max_results=max_results)

        printProgressBar(i + 1, len(dois), prefix=show_string,
                         suffix=remaining_time(start_time=start_time, step=i, max=len(dois)),
                         length=50)

    header                  = add_headers_bib_info(empty_bib())
    header.insert(0, ["Original_DOI"])
    header.insert(1, ["Parent_DOI"])
    header.insert(2, ["SearchDepth"])
    header.insert(3, ["Cited_in_Pubmed"])
    header.insert(4, ["Cited_in_WoS"])

    return bib_info, header, browser


def get_together_cited_by_wos_pub(main_bib_info, bib_info_wos, bib_info_pub, toplevel_doi, parent_doi, depth):
    # getting Infos of Pubmed and WoS together + adding the parent information + adding it to the large bib_info database
    from pubmed_plugins import merge_bib_info, empty_bib

    new_bib_info            = merge_different_sources(bib_info_pub, bib_info_wos, empty_bib())

    new_bib_info[0].insert(0, toplevel_doi)
    new_bib_info[0].insert(1, parent_doi)
    new_bib_info[0].insert(2, str(depth))
    if depth == 0:
        new_bib_info[0].insert(3, "-1")
        new_bib_info[0].insert(4, "-1")
    else:
        new_bib_info[0].insert(3, "0")
        new_bib_info[0].insert(4, "1")

    merge_bib_info(main_bib_info, new_bib_info[0])


def sub_extract_cited_by(elements, browser, http, bib_info, toplevel_doi, parent_doi, wos_url, depth, max_depth, cits_pub, cits_wos, cits_coch, apmid, correction, max_results=5000):
    from plugins_webofscience import sub_extract_cited_by_wos, general_search_wos, identify_correct_wos_entry
    from pubmed_plugins import sub_extract_cited_by_pubmed, idx_header

    if (cits_wos > 0):
        browser                             = sub_extract_cited_by_wos(elements, browser, http, bib_info, toplevel_doi, parent_doi, wos_url, depth, max_depth, max_results=5000)

    if cits_pub > 0:
        browser                             = sub_extract_cited_by_pubmed(browser, http, bib_info, toplevel_doi, parent_doi, wos_url, depth, max_depth, apmid, correction, max_results=5000)

    if cits_coch > 0:
        print("MISSING")

    # next recursive call
    if (depth < max_depth): #if  & (int(bib_info[19][-1]) > 0):

        ## identify important headers
        #correction                          = 5  # five additional fields
        hpub                                = idx_header("Cited_By_Pubmed")     + correction
        hwos                                = idx_header("Cited_By_WoS")        + correction
        hcoch                               = idx_header("Cited_By_Cochrane")   + correction

        for i in range(0, len(bib_info[0])):
            if int(bib_info[2][i]) == depth:
                if (bib_info[1][i] == parent_doi) & (bib_info[1][i] != bib_info[3][i]): # is parent_to the present? and prevent infinite loop by toplevel_doi

                    # counting the citations of the sources
                    try: cits_pub           = int(bib_info[hpub][i])
                    except: cits_pub        = 0
                    try: cits_wos           = int(bib_info[hwos][i])
                    except: cits_wos        = 0
                    try: cits_coch          = int(bib_info[hcoch][i])
                    except: cits_coch       = 0

                    if (cits_pub > 0) | (cits_wos > 0) | (cits_coch > 0):
                        new_apmid           = bib_info[correction + 1][i]
                        new_parent_doi      = bib_info[correction][i]

                        if is_doi(new_parent_doi):

                            urls, browser   = general_search_wos(browser, http, new_parent_doi, max_results=100, search_tag="DOI", pubmed=False)
                            bib_info_wos    = identify_correct_wos_entry(browser, urls, new_parent_doi, "DOI")

                            browser         = sub_extract_cited_by(elements, browser, http, bib_info, toplevel_doi, new_parent_doi, bib_info_wos[-2], depth + 1, max_depth, cits_pub, cits_wos, cits_coch, new_apmid, correction, max_results=max_results)

    return browser


def get_wos_url(url):
    res         = ""
    start       = url.find("https://apps.webof")
    if start > -1:
        ende        = find_earliest_end(url, start, einschluss=[chr(32), ";"], ausschluss=["/", ".", ":", "&", "%", "=", "?"])
        res         = url[start : ende]
    return res


def download_html_as_pdf(name, url, afolder):
    import pdfkit
    options = {'quiet': ''} # output surpressed
    pdfkit.from_url(url, afolder + name + ".pdf", options=options)

###################################################################
#################### Guidelines ###################################
###################################################################

def search_citations_in_guidelines(data, http, browser, keep, silent = False):
    from awmf_plugin import search_in_awmf
    from nice_plugin import search_in_nice
    from plugin_tripdb import search_in_tripdb
    from pubmed_plugins import empty_bib
    import datetime

    result_size     = len(empty_guidelines())
    collection      = empty_bib()
    for i in range(0,result_size - 1):
        collection.append([])

    if silent == False:
        show_string = 'Searching Guidelines'
        printProgressBar(0, len(data[0]), prefix=show_string, suffix="remaining: 0:00:00:00", length=50)
        start_time = datetime.datetime.now()

    for i in range(0, len(data[0])):
        # perform the searches
        #print("%d - %s" % (i, data[0][i]))
        result      = [[],[],[]]
        if keep.awmf == 1:  result[0], browser  = search_in_awmf([item[i] for item in data], browser)
        else:               result[0]           = empty_guidelines()
        if keep.nice == 1:  result[1]           = search_in_nice([item[i] for item in data], http)
        else:               result[1]           = empty_guidelines()
        if keep.tripdb == 1:result[2], browser  = search_in_tripdb(browser, [item[i] for item in data])
        else:               result[2]           = empty_guidelines()
        result                                  = unify_collector(result)

        if result == empty_guidelines(): ## nothing found; create empty line
            if is_doi(data[0][i]):
                collection[0].append(data[0][i])
            else:
                collection[0].append(data[1][i])
            for n in range(1, len(collection)):
                collection[n].append(" ")

        else:
            # try to get more information about the guidelines
            for n in range(0, len(result[0])):
                #print("  %d - %s" % (n, result[1][n]))
                if keep.extract_bib != 0:
                    if is_doi(result[0][n]):
                        this_bib_info, a, b, browser   = extract_bib_info([result[0][n]], browser, http, max_pmids=50, silent=True)
                    else:
                        this_bib_info, a, b, browser   = extract_bib_info([result[1][n]], browser, http, max_pmids=50, silent=True)
                else:
                    this_bib_info                      = empty_bib(mode="spaces")

                if is_doi(data[0][i]):
                    collection[0].append(data[0][i])
                else:
                    collection[0].append(data[1][i])

                for k in range(2, result_size):
                    collection[k - 1].append(result[k][n])

                for k in range(0, len(this_bib_info)):
                    collection[result_size - 1 + k].append(this_bib_info[k][0])

        if silent == False:
            printProgressBar(i + 1, len(data[0]), prefix=show_string, suffix=remaining_time(start_time=start_time, step=i, max=len(data[0])), length=50)

    #header          = [item[i] for item in add_headers_bib_info(empty_bib())]
    #header[0:0]     = empty_guidelines(title="alternative")
    #add_headers_bib_info(collection, header)

    return collection, browser

def unify_collector(collector):
    result                  = empty_guidelines()

    for i in range(0, len(collector) - 1):
        for j in range(0, len(collector[i][1])):
            #if j <= len(collector[i][1]):
            for k in range(0, len(collector[i])): # take to result
                result[k].append(collector[i][k][j])

            for k in range(i + 1, len(collector)): # for deletion
                try:
                    idx     = collector[k][1].index(collector[i][1][j])
                except:
                    idx     = None
                if idx != None:
                    if result[6][-1] != collector[k][6][idx]: ## for urls
                        result[6][-1] = result[6][-1] + " ; " + collector[k][6][idx]
                    for l in range(7,10): ## for found in
                        if collector[k][l][idx] == "1":
                            result[l][-1] = "1"
                    for l in range(0, len(collector[k])):
                        del collector[k][l][idx]
    for k in range(0, len(collector[-1])):
        for i in range(0, len(collector[-1][k])):
            result[k].append(collector[-1][k][i])


    return result


##################################################################
##################################################################
##################################################################
# Other
##################################################################

def printProgressBar(iteration, total, prefix='', suffix='', decimals=1, length=100, fill=chr(9608)): #9932⛌  9761☡  9747☓ 9608█ 9587╳ 10731⧫  10711⧗
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
    """
    prefix          = stretch_prefix(prefix)
    percent         = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength    = int(length * iteration // total)
    bar             = fill * filledLength + '-' * (length - filledLength)
    print('\r%s |%s| %s%% %s' % (prefix, bar, percent, suffix), end='\r')
    # Print New Line on Complete
    if iteration == total:
        print()

def stretch_prefix(prefix):
    length          = 35 - len(prefix)
    empties         = (" " * (int(length/len(" "))+1))[:length]
    return prefix + empties


def remaining_time(start_time, step, max):
    import datetime
    inter_time  = datetime.datetime.now()
    delta       = inter_time - start_time
    full_time   = delta / (step + 1) * (max)
    # delta is sometimes larger than fulltime, by milliseconds at the end of a cicle, than its gets negative but should be 0
    if full_time >= delta:
        remain_time = full_time - delta
        return time_2_string(remain_time)
    else:
        return "remaining: 0:00:00:00"


def time_2_string(atime):
    text = "remaining: " + str(atime.days)
    m, s = divmod(atime.seconds, 60)
    h, m = divmod(m, 60)
    text = text + ":%02d:%02d:%02d" % (h, m, s)
    return text