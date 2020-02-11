def start_sct():
    from definitions import initialize_browser, folder_structure
    from gui_data import check_geckodriver
    dois, groups, ids   = read_cochrane_file()
    folder              = folder_structure("/home/nitschke/Downloads/test_ubersetzung")
    #browser             = initialize_browser(check_geckodriver(1), folder)
    #get_everything(dois, groups, ids, browser)

    f = open("/home/nitschke/Downloads/test_ubersetzung/zugeordnet_CC_Gruppen.txt", "w")
    f.write("DOI\tCC_group\tID\n")
    for i in range(0, len(groups)):
        f.write(dois[i])
        f.write("\t")
        f.write(groups[i])
        f.write("\t")
        f.write(ids[i])
        f.write("\n")
    f.close()


#######################################################
def read_cochrane_file():
    from os import path

    afile       = path.split('/home/nitschke/Downloads/all_cochrane.txt')
    fid         = open(afile[0]+ path.sep + afile[1])
    content     = fid.read()
    fid.close()

    start       = content.find("DOI:")
    dois        = []
    while start != -1:
        start   = content.find("10", start)
        end     = content.find("\n", start)
        dois.append(content[start : end])
        start   = content.find("DOI:", end)

    start       = content.find("CC:")
    groups        = []
    while start != -1:
        start   = content.find("[", start)
        end     = content.find("]", start)
        groups.append(content[start + 1 : end])
        start   = content.find("CC:", end)

    start       = content.find("ID:")
    ids         = []
    while start != -1:
        start   = content.find(" ", start) + 1
        end     = content.find("\n", start)
        ids.append(content[start: end])
        start   = content.find("ID:", end)

    return dois, groups, ids

#######################################################
def get_site(browser, sublink):
    from definitions import open_page

    mainlink    = "https://www.cochranelibrary.com/cdsr/doi/"

    ## ENGLISH
    open_page(browser, mainlink + sublink + "/full/en")
    cont        = browser.page_source

    ## get abstract english
    abstract_en = extract_abstract(cont)

    ## get PLS english
    pls_en      = extract_pls(cont)

    ## GERMAN

    open_page(browser, mainlink + sublink + "/full/de")
    cont        = browser.page_source

    ## get abstract german
    abstract_ger= extract_abstract(cont)

    ## get pls german
    pls_ger     = extract_pls(cont)

    return abstract_en, pls_en, abstract_ger, pls_ger

#######################################################
def extract_abstract(cont):
    from definitions import clear_text_from_inclusions
    start       = cont.find("abstract full_abstract")
    start       = cont.find("<p>", start) + len("<p>")
    end         = cont.find("</div>", start)
    subcont     = cont[start : end]
    subcont     = clear_titles(subcont)
    subcont     = clear_text_from_inclusions(subcont)
    result      = dissect_text(subcont.strip())
    return result

#######################################################
def extract_pls(cont):
    from definitions import clear_text_from_inclusions
    start   = cont.find("abstract_plainLanguageSummary")
    if start > -1:
        start   = cont.find("<p>", start) + len("<p>")
        start   = cont.find("<p>", start) + len("<p>")
        end     = cont.find("</div>", start)
        subcont = cont[start: end]
        subcont = clear_titles(subcont)
        subcont = clear_text_from_inclusions(subcont)
        result  = dissect_text(subcont.strip())
    else:
        result = []
    return result


#######################################################
def clear_titles(cont):
    start       = cont.find("<h3")
    while start != -1:
        end     = cont.find("</h3>", start)
        cont    = cont[0:start] + cont[end + len("</h3>"): len(cont)]
        start   = cont.find("<h3")
    return cont

#######################################################
def dissect_text(cont):
    result      = []
    start       = 0
    while start < len(cont):
        end     = find_earliest_end_ch(cont, start)# cont.find(".", start)
        #part    = cont.find(":", start)
        #if (part > -1) & (part < end):
        #    end = part
        result.append(cont[start:end+1].strip())
        start   = end + 1
    return result

#######################################################
def get_everything(dois, groups, ids, browser):
    #dois = ["10.1002/14651858.CD012292.pub2"]
    for i in (0, len(dois)):
        print("%d / %d" % (i, len(dois)))
        abstract_en, pls_en, abstract_ger, pls_ger = get_site(browser, dois[i])
        if len(abstract_en) == len(abstract_ger):
            print(1)
        else:
            for j in range(0, len(abstract_en)):
                print("%s" % abstract_en[j])
                print("%s" % abstract_ger[j])
                print("\n")

        if len(pls_en) == len(pls_ger):
            print(1)
        else:
            print(1)

#######################################################
def find_earliest_end_ch(cont, start, ausschluss = [], einschluss = [], check_last_point=True):
    import re
    signs       = [".", "?", "!", "\n", "\t"]
    signs       = signs + einschluss
    passit      = ["i.e.", "i. e.", "z. B.", "z.B.", "e.g.", "e. g.", "d.h.", "d. h."]
    passit      = passit + ausschluss
    passreg     = ["[0-9]{2}[.]{1} (Jan(uar)?|Feb(ruar)?|Mär(z)?|Apr(il)?|Mai|Jun(i)?|Jul(i)?|Aug(ust)?|Sep(tember)?|Okt(ober)?|Nov(ember)?|Dez(ember)?)",            # dates, mostly in germany
                   "[0-9]{1}[.]{1}[0-9]{1}"]    # 1.2 numbers
    end         = len(cont)
    for i in signs:
        if (cont.find(i, start) < end) & (cont.find(i, start) > -1):
            end = cont.find(i, start)

    for i in passit:
        if (cont.find(i, start) > -1) & (cont.find(i, start) <= end):
            end = find_earliest_end_ch(cont, end + len(i))


    for i in passreg:
        x   =  re.search(i, cont[start : len(cont)])
        if x != None:
            if x.start()+start <= end:
                end = find_earliest_end_ch(cont, start + x.end())
            #break

    if check_last_point == True:
        if cont[end - 1] == ".": end = end - 1

    return end
