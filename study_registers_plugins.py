########################################################
################### NCT ################################
########################################################

def extract_dois_NCT(cont, http):
    result          = list()
    failed_doi      = list()
    result, failed_doi = sub_NCT(cont, "Publications:", result, failed_doi, http)
    result, failed_doi = sub_NCT(cont, "Publications automatically indexed", result, failed_doi, http)
    return result, failed_doi

def sub_NCT(cont, Suchwort , result, failed_doi, http):

    from definitions import find_earliest_end, follow_to_pubmed_for_doi, clear_signs

    start           = cont.find(Suchwort)
    end             = cont.find("Responsible Party", start)

    start           = cont.find('title="', start) + len('title="')
    while (start < end) & (start > -1):
        ref_end     = cont.find('"', start + 5)
        if cont[start:ref_end].find("doi") > -1:
            start   = cont.find("doi", start)
            start   = cont.find("10.", start)  # all dois start with 10
            ref_end = find_earliest_end(cont, start)
            result.append(cont[start:ref_end])
        else:

            # extract Link to subpage with URl of CG
            mainlink    = "https://clinicaltrials.gov"
            link_start  = cont[::-1].find("href"[::-1], len(cont)-start)      # find the URl just BEFORE
            link_start  = len(cont) - link_start -1                 # correction because index is "backwards" before
            link_start  = cont.find('"', link_start) + 1
            link_end    = cont.find('"', link_start  + 1)
            link        = cont[link_start : link_end]
            if link[len(link)-1] == ".": link = link[0 : len(link)-1]
            sublink     = mainlink + link

            ## get site with link to pubmed
            site        = http.request("GET", sublink)
            site        = site.data.decode("utf-8")
            substart    = site.find("You are about to leave")
            substart    = site.find("URL", substart)
            substart    = site.find("http", substart)
            subend      = site.find('"', substart + 1)

            erg         = follow_to_pubmed_for_doi(site[substart : subend], http)
            #print(erg)
            if erg == '':
                failed_doi.append(clear_signs(cont[start:ref_end]))
            else:
                result.append(erg)

        start = cont.find('title="', start) + len('title="')

    return result, failed_doi

########################################################
################### ISRCTN #############################
########################################################

def extract_dois_ISRCTN(cont, http):
    result          = list()
    failed_doi      = list()
    result, failed_doi = sub_ISRCTN_summary(cont, result, failed_doi, http)
    result, failed_doi = sub_ISRCTN_citations(cont, result, failed_doi, http)
    return result, failed_doi

def sub_ISRCTN_summary(cont, result, failed_doi, http):

    from definitions import follow_to_pubmed_for_doi, clear_signs

    start           = cont.find("Publication list")
    end             = cont.find("Publication citations", start)

    start           = cont.find('href="', start) + len('href="')
    while (start < end) & (start > -1):
        ref_end     = cont.find('"', start)
        sublink     = cont[start:ref_end]
        erg         = follow_to_pubmed_for_doi(sublink, http)
        #print(erg)
        if erg == '':
            failed_doi.append(clear_signs(cont[start:ref_end]))
        else:
            result.append(erg)
        start       = cont.find('href="', start) + len('href="')

    return result, failed_doi

def sub_ISRCTN_citations(cont, result, failed_doi, http):
    from definitions import find_earliest_end, follow_to_pubmed_for_doi, clear_signs

    start           = cont.find("Publication citations")
    end             = cont.find("Additional files", start)

    start           = cont.find('Results', start) + len('Results')
    while (start < end) & (start > -1):
        ref_end     = cont.find("Results", start + 5)
        if cont[start : ref_end].find("doi") > -1:
            start   = cont.find("doi", start)
            start   = cont.find("10.", start)
            ref_end = find_earliest_end(cont, start)
            result.append(cont[start:ref_end])
        else:
            start   = cont.find("http://www.ncbi.nlm.nih.gov", start)
            ref_end = find_earliest_end(cont, start+20)

            erg     = follow_to_pubmed_for_doi(cont[start : ref_end], http)
            # print(erg)
            if erg == '':
                failed_doi.append(clear_signs(cont[start:ref_end]))
            else:
                result.append(erg)

        start       = cont.find('Results', start) + len('Results')


    return result, failed_doi

########################################################
################### DRKS ###############################
########################################################

def extract_dois_DRKS(cont, http):
    from definitions import find_earliest_end, follow_to_pubmed_for_doi, clear_signs

    result          = list()
    failed_doi      = list()

    start           = cont.find(''"publications"'')
    if start == -1: start = cont.find("Publications, Results")
    end             = cont.find("START CUT HERE", start)

    start           = cont.find('"publication"', start)
    while (start < end) & (start > -1):
        ref_end     = cont.find("</li>", start)

        if cont[ref_end-1] == "*":
            a = 1               # place holder. do nothing

        elif cont[start:ref_end].find("doi") > -1:
            start = cont.find("doi", start)
            start = cont.find("10.", start)
            ref_end = find_earliest_end(cont, start, einschluss=["?"])
            result.append(cont[start:ref_end])

        elif cont[start:ref_end].find("DOI") > -1:
            start   = cont.find("DOI", start)
            start   = cont.find("10.", start)
            ref_end = find_earliest_end(cont, start, einschluss=["?"])
            result.append(cont[start:ref_end])

        elif cont[start:ref_end].find("http") > -1:
            # get link
            start_link  = cont.find('href="', start) + len('href="')
            end_link    = find_earliest_end(cont, start_link + 20, [' '])
            sublink     = cont[start_link: end_link]
            # get text
            start_text  = cont.find(">", end_link) + 1
            end_text    = cont.find("<", start_text)

            if sublink.find("pdf") > -1:
                failed_doi.append(clear_signs(cont[start_text:end_text] + '; ' + cont[start_link:end_link]))
            else:
                try:
                    erg = follow_to_pubmed_for_doi(sublink, http)
                except:
                    erg = ''

                if erg == '':
                    failed_doi.append(clear_signs(cont[start_text:end_text] + '; ' + cont[start_link:end_link]))
                else:
                    result.append(erg)

        else:
            failed_doi.append(clear_signs(cont[start : ref_end]))

        start = cont.find('"publication"', start + 5)

    return result, failed_doi


########################################################
################### EudraCT ############################
########################################################

def extract_dois_EudraCT(cont, http):
    result          = list()
    failed_doi      = list()
    
    return result, failed_doi

###########################################################
###########################################################
####### for checking of study register result #############
###########################################################
###########################################################

def check_for_study_reg_results_NCT(id, folders):

    site        = open_html(id, folders)
    isthere     = -1

    if site.find("No Results Posted") > -1:
        isthere = 0
    if (site.find("Study Results") > -1):
        if isthere == -1:
            isthere = 1
        else:
            isthere = -1
    if (site.find("Results Submitted") > -1):
        if isthere == -1:
            isthere = 2
        else:
            isthere = -1

    return isthere

def check_for_study_reg_results_DRKS(id, folders):

    site        = open_html(id, folders)
    a, b        = extract_dois_DRKS(site, [])
    if (a!=list()) | (b!=list()):
        return 1
    else:
        return 0

def check_for_study_reg_results_ISRCTN(id, folders):
    
    site        = open_html(id, folders)
    start       = site.find("Basic results")#"Results - basic reporting")
    end         = site.find("</p>", start)

    if site[start:end].find("noValue") > -1:
        start   = site.find("Participant level data")
        end     = site.find("</p>", start)
        if site[start:end].find("tored in repository") > -1:
            return 1
        else:
            return 0
    else:
        return 1


def check_for_study_reg_results_EudraCT(id, folders):

    site        = open_html(id, folders)
    isthere     = -1

    if site.find("No results available") > -1:
        isthere = 0
    if (site.find("View results") > -1):
        if isthere == -1:
            isthere = 1
        else:
            isthere = -1

    return isthere

def open_html(id, folders):
    # opens the previously stored html file from hard disc
    f       = open(folders.html + id + ".html")
    site    = f.read()
    f.close()
    return site

###########################################################
###########################################################
############# for the result downloads ####################
###########################################################
###########################################################

def download_results_nct(id, url, folders):
    #from definitions import download_html_as_pdf
    from weasyprint import HTML, CSS
    #download_html_as_pdf(id, url, folders.results)
    HTML(url).write_pdf(folders.results + id + ".pdf", stylesheets=[CSS(string='@page { size: A3; margin: 0.2cm}')])


def download_results_eudract(id, url, folders, http):
    from definitions import download_html_as_pdf, save_pdf_with_loop
    import os
    download_html_as_pdf("EudraCT" + id, url, folders.results)
    if os.path.exists(folders.html + id + '_res' + '.html'):
        f           = open(folders.html + id + '_res' + '.html')
        cont        = f.read()
        f.close()

        start       = cont.find("Summary report(s)")
        if start > -1:
            end     = cont.find("</tr", start)
            cont2   = cont[start:end]
            start   = cont2.find("href")
            start   = cont2.find('"', start) + 1
            end     = cont2.find('"', start)
            act_url = cont2[start:end]
            pdf     = http.request('GET', cont2[start:end]).data
            f       = open(folders.results + "EudraCT" + id + "_2.pdf", 'wb')
            f.write(pdf)
            f.close()


