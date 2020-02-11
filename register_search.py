def register_search_main(elements, study_ids, browser, http, mail_add, folders, timestamp, keep):
    # is the main search for the Study Register Publications
    # searches the specified Sources and gets Info about it with Pubmed

    import datetime
    from definitions    import printProgressBar, remaining_time, is_doi
    from pubmed_plugins import empty_bib, identify_correct_pmid, search_pubmed_for_pmids
    #from output_defs    import write_output_register_search

    mode                    = 1
    bib_info                = empty_bib()
    results                 = [list(), list(), list(), list()]      # study_id reference; doi/title; source (url); method which found the ref
    failed_message          = [list(), list()]

    try:

        ################################################################
        ################ 4: Search google scholar ###################### starting with google because than recaptcha at start
        ################################################################
        if keep.google_scholar == 1:
            source = 4  # "Google_Scholar"
            ############################################################
            from plugin_google_scholar import google_scholar_general_search, gs_identify_dois_on_html

            # Progress things
            show_string = "Searching GoogleScholar"
            start_time = datetime.datetime.now()
            printProgressBar(0, len(study_ids), prefix=show_string, suffix="remaining: 0:00:00:00", length=50)

            for i in range(0, len(study_ids)):
                try:
                    # print(i, study_ids[i])
                    # get links from google scholar
                    links = google_scholar_general_search(browser, study_ids[i], timestamp, mail_add, max_results=10000)

                    # follow linkgs and extract dois when possible
                    dois, urls = gs_identify_dois_on_html(browser, http, links)

                    # adding results to collection
                    for j in range(0, len(dois)):
                        add_single_result(results, i, dois[j], urls[j], source)
                except:
                    failed_message[0].append(source)
                    failed_message[1].append(study_ids[i])

                printProgressBar(i + 1, len(study_ids), prefix=show_string,
                                 suffix=remaining_time(start_time=start_time, step=i, max=len(study_ids)),
                                 length=50)

        ################################################################
        ############# 1: Search the registers themselves ###############
        ################################################################
        if keep.study_reg != 1:
            stud_reg_res        = ""
        else:
            source              = 1#"Study_Register"

            org_source = (["NCT", "DRKS", "ISRCTN", "EudraCT"], [                                   #1 Names of Registers
                "https://clinicaltrials.gov/ct2/show/",                                             #2 Link to resp. site
                "http://www.drks.de/drks_web/navigate.do?navigationId=trial.HTML&TRIAL_ID=",        #3 Link to results
                "https://www.isrctn.com/",
                "https://www.clinicaltrialsregister.eu/ctr-search/search?query="
            ], [
                "https://clinicaltrials.gov/ct2/show/results/????sect=X6543210",
                "",
                "",
                "https://www.clinicaltrialsregister.eu/ctr-search/trial/???/results"])

            ############################################################
            from definitions import get_html_files
            #from output_defs import write_output_register_search_old
            from gui_data    import feedback_both

            try:

                ch_study_ids        = prepare_study_reg_names_for_study_reg_search(list(study_ids)) # for some reason this function directly alters the input in memory

                # Get HTML Files of Study Registers
                urls                = get_html_files(ch_study_ids, org_source, folders)
                try:

                    # Identifiy and follow Links
                    dois, no_dois, failed_dois, total_fails \
                                    = identify_dois(ch_study_ids, study_ids, org_source, http, folders)

                    # adding results to collection
                    for i in range(0, len(dois[0])):
                        add_single_result(results, dois[0][i], dois[1][i], urls[dois[0][i]], source)

                    for i in range(0, len(failed_dois[0])):
                        add_single_result(results, failed_dois[0][i], failed_dois[1][i], urls[failed_dois[0][i]], source)

                    for i in range(0, len(total_fails)):
                        failed_message[0].append(source)
                        failed_message[1].append(study_ids[total_fails[i]])

                    # Check different study register numbers for provided results within the registers
                    stud_reg_res    = check_for_available_results(ch_study_ids, org_source, folders)

                except:
                    mode[0]         = 3  # identifing DOIs error
                    feedback_both(elements, "An Error occurred during the identification of the dois")

                # Get the results (pdfs) provided by study registers
                if elements.checks.study_res.value.get() == 1:
                    download_study_register_results(browser, ch_study_ids, folders, org_source, stud_reg_res, http)
                    
            except:
                mode[0]             = 2  # downloading HTML Study Registers error
                feedback_both(elements, "An Error occurred during downloading the webpages of the study registers")

        ################################################################
        ######################## 2: Pubmed #############################
        ################################################################
        if keep.pubmed == 1:
            source                  = 2#"Pubmed"
            ############################################################
            from pubmed_plugins import extract_bib_from_pubmed

            # Progress things
            show_string             = "Searching Pubmed (NCBI)"
            start_time              = datetime.datetime.now()
            printProgressBar(0, len(study_ids), prefix=show_string, suffix="remaining: 0:00:00:00", length=50)

            for i in range(0, len(study_ids)):
                try:
                    pmids               = search_pubmed_for_pmids("AllFields", study_ids[i], http ,max_pmids=10000)
                    for j in range(0, len(pmids)):

                        new_bib_info    = extract_bib_from_pubmed(http, pmids[j])

                        # adding results to collection
                        if is_doi(new_bib_info[0]):
                            add_single_result(results, i, new_bib_info[0], new_bib_info[15], source)
                        else:
                            add_single_result(results, i, new_bib_info[2], new_bib_info[15], source)
                except:
                    failed_message[0].append(source)
                    failed_message[1].append(study_ids[i])

                printProgressBar(i + 1, len(study_ids), prefix=show_string,
                                 suffix=remaining_time(start_time=start_time, step=i, max=len(study_ids)),
                                 length=50)

        ################################################################
        #################### 3: Cochrane Library #######################
        ################################################################
        if keep.cochrane_lib == 1:
            source                  = 3#"Cochrane_Library"
            ############################################################
            from plugin_cochrane_library import search_in_cochrane_library, wiley_doi_from_link_text, cl_get_id_from_frame
            from definitions             import is_doi
            from plugin_google_scholar   import gs_identify_dois_on_html

            show_string             = "Searching Cochrane Library"
            start_time              = datetime.datetime.now()
            printProgressBar(0, len(study_ids), prefix=show_string, suffix="remaining: 0:00:00:00", length=50)

            for i in range(0, len(study_ids)):
                try:
                    #print(study_ids[i])
                    # get urls from cochrane library(wiley)
                    urls, browser           = search_in_cochrane_library(browser, study_ids[i])

                    for j in range(0, len(urls)):

                        try:
                            if is_doi(wiley_doi_from_link_text(urls[j])):          # check if doi directly available
                                doi         = wiley_doi_from_link_text(urls[j])
                            else:
                                doi         = cl_get_id_from_frame(http, urls[j])
                        except:
                            doi = " "
                        add_single_result(results, i, doi, urls[j], source)
                        #print(i, doi, urls[j])
                except:
                    failed_message[0].append(source)
                    failed_message[1].append(study_ids[i])

                printProgressBar(i + 1, len(study_ids), prefix=show_string,
                             suffix=remaining_time(start_time=start_time, step=i, max=len(study_ids)),
                             length=50)

        ################################################################
        ########################## 5: Livivo ###########################
        ################################################################
        if keep.livivo == 1:
            source                  = 5#"Livivo"
            ############################################################
            from plugin_livivo  import general_search_livivo

            # Progress things
            show_string             = "Searching Livivo"
            start_time              = datetime.datetime.now()
            printProgressBar(0, len(study_ids), prefix=show_string, suffix="remaining: 0:00:00:00", length=50)

            for i in range(0, len(study_ids)):
                try:
                    # print(i, study_ids[i])
                    dois, browser       = general_search_livivo(browser, study_ids[i], max_results=1000)

                    for j in range(0, len(dois)):
                        #print(dois[j])
                        if is_doi(dois[j]):             # add doi
                            add_single_result(results, i, dois[j], "", source)
                        else:                           # no doi, so loop up title in pubmed and add
                            pmids       = search_pubmed_for_pmids("title", dois[j], http)
                            bib_info    = identify_correct_pmid(http, pmids, dois[j], "title")
                            if bib_info != list():   # was exactly one match found
                                add_single_result(results, i, bib_info[0], " ", source)
                            else:                       # multiple matches --> take title
                                add_single_result(results, i, dois[j], " ", source)

                except:
                    failed_message[0].append(source)
                    failed_message[1].append(study_ids[i])

                printProgressBar(i + 1, len(study_ids), prefix=show_string,
                             suffix=remaining_time(start_time=start_time, step=i, max=len(study_ids)),
                             length=50)

        ################################################################
        ######################## 6: TripDatabase #######################
        ################################################################
        if keep.trip_db == 1:
            source                  = 6#"TripDatabase"
            ############################################################
            from plugin_tripdb         import general_search_tripdb

            # Progress things
            show_string                 = "Searching Trip Database"
            start_time                  = datetime.datetime.now()
            printProgressBar(0, len(study_ids), prefix=show_string, suffix="remaining: 0:00:00:00", length=50)

            for i in range(0, len(study_ids)):
                try:
                    #print(i, study_ids[i])

                    # search Trip Database
                    dois, urls, browser = general_search_tripdb(browser, study_ids[i])

                    for j in range(0, len(dois)):
                        ## look it up in pubmed
                        pmids           = search_pubmed_for_pmids('title', dois[j], http, max_pmids=100)
                        #print(pmids)
                        bib_info        = identify_correct_pmid(http, pmids, dois[j], "title")
                        if bib_info != list():  # found in pubmed
                            if is_doi(bib_info[0]):
                                ## add with doi
                                add_single_result(results, i, bib_info[0], urls[j], source)
                            else:
                                ## add with title
                                add_single_result(results, i, dois[j],     urls[j], source)
                        else:                   # not found in pubmed
                            add_single_result(    results, i, dois[j],     urls[j], source)

                except:
                    failed_message[0].append(source)
                    failed_message[1].append(study_ids[i])

                printProgressBar(i + 1, len(study_ids), prefix=show_string,
                                 suffix=remaining_time(start_time=start_time, step=i, max=len(study_ids)),
                                 length=50)


        ################################################################
        ######################## 7: base-search ########################
        ################################################################
        if keep.base_search == 1:
            source                  = 7#"base-search"
            ############################################################
            from plugin_basesearch import general_search_base_search
            from definitions       import clearer_text

            # Progress things
            show_string             = "Searching base-search.net"
            start_time              = datetime.datetime.now()
            printProgressBar(0, len(study_ids), prefix=show_string, suffix="remaining: 0:00:00:00", length=50)

            for i in range(0, len(study_ids)):
                try:
                    #print(i, study_ids[i])

                    # get search results
                    dois, urls, browser = general_search_base_search(http, study_ids[i], max_results=500)

                    for j in range(0, len(dois)):
                        #print(dois[j], urls[j])
                        if is_doi(dois[j]): # found doi
                            add_single_result(results, i, dois[j], urls[j], source)
                        else:               # doi not found
                            dois[j]     = clearer_text(dois[j])
                            pmids       = search_pubmed_for_pmids("title", dois[j], http, max_pmids=20)
                            bib_info    = identify_correct_pmid(http, pmids, dois[j], "title")
                            if bib_info != list(): # found something in Pubmed
                                if is_doi(bib_info[0]):
                                    add_single_result(results, i, bib_info[0], urls[j], source)
                                else:
                                    add_single_result(results, i, dois[j], urls[j], source)
                            else:
                                add_single_result(results, i, dois[j], urls[j], source)

                except:
                    failed_message[0].append(source)
                    failed_message[1].append(study_ids[i])

                printProgressBar(i + 1, len(study_ids), prefix=show_string,
                                 suffix=remaining_time(start_time=start_time, step=i, max=len(study_ids)),
                                 length=50)



        ################################################################
        ######################## 8: UB-Freiburg ########################
        ################################################################
        if keep.ub_fr == 1:
            source                  = 8#"UB-Freiburg"
            ############################################################
            from plugin_ubfr import general_search_ub_fr

            # Progress things
            show_string     = "Searching UB Freiburg"
            start_time      = datetime.datetime.now()
            printProgressBar(0, len(study_ids), prefix=show_string, suffix="remaining: 0:00:00:00", length=50)

            for i in range(0, len(study_ids)):
                try:
                    #print(i, study_ids[i])

                    dois, urls  = general_search_ub_fr(http, study_ids[i], max_results=100)

                    for j in range(0, len(dois)):
                        if is_doi(dois[j]):
                            add_single_result(results, i, dois[j], urls[j], source)
                        else:
                            pmids       = search_pubmed_for_pmids("title", dois[j], http, max_pmids=100)
                            bib_info    = identify_correct_pmid(http, pmids, dois[j], "title")
                            if bib_info != list():  # found something in Pubmed
                                if is_doi(bib_info[0]):
                                    add_single_result(results, i, bib_info[0], urls[j], source)
                                else:
                                    add_single_result(results, i, dois[j], urls[j], source)
                            else:                   # found nothing in Pubmed
                                add_single_result(results, i, dois[j], urls[j], source)
                except:
                    failed_message[0].append(source)
                    failed_message[1].append(study_ids[i])

                printProgressBar(i + 1, len(study_ids), prefix=show_string,
                                 suffix=remaining_time(start_time=start_time, step=i, max=len(study_ids)),
                                 length=50)

        ################################################################
        ###################### 9: Web of Science #######################
        ################################################################
        if keep.wos == 1:
            source                  = 9#"WebOfScience"
            ############################################################
            from plugins_webofscience import general_search_wos

            # Progress things
            show_string             = "Searching Web of Science"
            start_time              = datetime.datetime.now()
            printProgressBar(0, len(study_ids), prefix=show_string, suffix="remaining: 0:00:00:00", length=50)

            for i in range(0, len(study_ids)):
                try:
                    #print(i, study_ids[i])

                    dois, browser   = general_search_wos(browser, http, study_ids[i], max_results=50)

                    for j in range(0, len(dois)):
                        add_single_result(results, i, dois[j], " ", source)

                except:
                    failed_message[0].append(source)
                    failed_message[1].append(study_ids[i])

                printProgressBar(i + 1, len(study_ids), prefix=show_string,
                                 suffix=remaining_time(start_time=start_time, step=i, max=len(study_ids)),
                                 length=50)

        ################################################################
        ########################## FINALIZE ############################
        ################################################################

    except:
        mode                = 2

    wrapped, header, no_results, browser \
                            = wrap_up_results(browser, http, results, study_ids, keep)
    transform_failed_searches(failed_message)

    return mode, wrapped, header, no_results, failed_message, browser, stud_reg_res


###########################################################
################### Results wrap up #######################
###########################################################
def wrap_up_results(browser, http, results, study_ids, keep):
    # wraps up all the search results and excludes duplicates
    from definitions    import compare_title, printProgressBar, remaining_time, decapitalize
    from pubmed_plugins import add_headers_bib_info, empty_bib
    import datetime
    output, preheader, sourceheader, subheader \
                                        = empty_output(keep)

    no_output                           = list()

    # Progress things
    show_string                         = "Merging Results"
    start_time                          = datetime.datetime.now()
    printProgressBar(0, len(study_ids), prefix=show_string, suffix="remaining: 0:00:00:00", length=50)

    # sort for better performance in matching samples
    sort_list_pub_wos_first_gs_last(results)
    sort_list_dois_first(results)

    for ID in range(0, len(study_ids)):
        #print(study_ids[ID])
        # find all entries from same StudyID
        idxs                            = [i for i, x in enumerate(results[0]) if x == ID]
        # no result found at all?
        if idxs == list():
            no_output.append(study_ids[ID])

        else:
            # get new list for all current ids
            cleared, weg, weg, weg      = empty_output(keep)

            # Go through all
            for row in idxs:
                # find if doi already in list
                try: inlist             = decapitalize(cleared[1]).index(decapitalize(results[1][row]))
                except: inlist          = -1

                if inlist > -1: # doi already in list
                    #update_row(cleared, inlist, results[row][3], keep)
                    update_source(cleared, inlist, results[3][row], results[2][row], keep)
                else:           # doi not in list
                    # search whether at least title is already in list
                    stat = 0
                    for vgl in range(0, len(cleared[len(preheader)])):
                        if compare_title(results[1][row], cleared[3][vgl]) & (cleared[3][vgl] != ' '):
                            # found the title in the database
                            stat        = 1
                            update_source(cleared, vgl, results[3][row], results[2][row], keep)
                            break

                    if stat == 0:
                        # so: no doi, no title in list, hence add
                        browser         = add_row(browser, http, results, cleared, study_ids[ID], row, keep)

            # add everything in cleared to final list
            for col in range(0, len(cleared)):
                for row in range(0, len(cleared[col])):
                    output[col].append(cleared[col][row])

        printProgressBar(ID + 1, len(study_ids), prefix=show_string,
                         suffix=remaining_time(start_time=start_time, step=ID, max=len(study_ids)),
                         length=50)

    # header things
    cont_header                         = list()
    bib_header                          = add_headers_bib_info(empty_bib())
    for i in range(0, len(bib_header)): cont_header.append(bib_header[i][0])
    header                              = preheader + cont_header + sourceheader + subheader

    # replace empty entries by " "
    for col in range(0, len(output)):
        for row in range(0, len(output[col])):
            if output[col][row] == list():
                output[col][row]        = " "

    return output, header, no_output, browser

#def update_row(cleared, inlist, source keep):


def add_row(browser, http, results, cleared, studyID, row, keep):
    from definitions import is_doi, is_link, collect_bib_info_different_sources
    from pubmed_plugins import identify_correct_pmid, search_pubmed_for_pmids, empty_bib
    from plugins_webofscience import general_search_wos, identify_correct_wos_entry

    bib_info, attention, browser    = collect_bib_info_different_sources(browser, http, results[1][row], results[2][row])

    # add origin search term / study id
    cleared[0].append(studyID)

    # add bibliography information
    weg, pre, weg, weg              = empty_output(keep)
    pre                             = len(pre)
    if  bib_info != list():
        for i in range(0, len(bib_info)):
            cleared[pre + i].append(bib_info[i])

    else:
        bib_info                    = empty_bib()
        for i in range(0, len(bib_info)):
            cleared[pre + i].append(" ")
        if is_doi(results[1][row]):
            cleared[pre][-1]        = results[1][row]
        else:
            cleared[pre+2][-1]      = results[1][row]

    # check of no title --> then attention
    if cleared[pre + 2] == ' ':
        attention                   = 1

    # add source where found
    ## how many search sources
    weg, pre, sour, sub             = empty_output(keep)
    pre                             = len(pre)
    sour                            = len(sour)
    sub                             = len(sub)
    cont                            = len(empty_bib())
    ## add 0 on all sources
    for i in range(pre + cont, pre + cont + sour):
        cleared[i].append('0')
    ## update source
    update_source(cleared, len(cleared[0])-1, results[3][row], results[2][row], keep)

    # add attention
    cleared[pre + cont + sour + sub - 1].append(str(attention))

    return browser

def update_source(cleared, row, source, url, keep):
    from pubmed_plugins import empty_bib
    ## how many infos of pubmed
    ### add source
    weg, pre, allsource, weg        = empty_output(keep)
    cont                            = len(empty_bib())
    pre                             = len(pre)
    allsource                       = len(allsource)
    col                             = source_number(keep, source) - 1
    cleared[pre + cont + col][row]  = '1'
    ### add url
    pointer                         = pre + cont + allsource
    try:
        cleared[pointer][row]       = cleared[pointer][row] + ', ' + url
    except:
        cleared[pointer].append(url)

def source_number(keep, source):
    # find the right column for the present source
    if      source == 1: return keep.study_reg
    elif    source == 2: return keep.study_reg + keep.pubmed
    elif    source == 3: return keep.study_reg + keep.pubmed + keep.cochrane_lib
    elif    source == 4: return keep.study_reg + keep.pubmed + keep.cochrane_lib + keep.google_scholar
    elif    source == 5: return keep.study_reg + keep.pubmed + keep.cochrane_lib + keep.google_scholar + keep.livivo
    elif    source == 6: return keep.study_reg + keep.pubmed + keep.cochrane_lib + keep.google_scholar + keep.livivo + keep.trip_db
    elif    source == 7: return keep.study_reg + keep.pubmed + keep.cochrane_lib + keep.google_scholar + keep.livivo + keep.trip_db + keep.base_search
    elif    source == 8: return keep.study_reg + keep.pubmed + keep.cochrane_lib + keep.google_scholar + keep.livivo + keep.trip_db + keep.base_search + keep.ub_fr
    elif    source == 9: return keep.study_reg + keep.pubmed + keep.cochrane_lib + keep.google_scholar + keep.livivo + keep.trip_db + keep.base_search + keep.ub_fr + keep.wos

def sort_list_pub_wos_first_gs_last(results):
    # sorts the results list, pubmed and wos first, google scholar last, then the PDF aquisition works better because of capital letters in dois

    if len(results[0]) > 1:
        from operator import itemgetter
        first               = list()
        mid                 = list()
        last                = list()
        for i in range(0, len(results[3])):
            if results[3][i] == 4:                              # is google scholar
                last.append(i)
            elif (results[3][i] == 2) | (results[3][i] == 8):   # is pubmed or wos
                first.append(i)
            else:                                               # everything else
                mid.append(i)
        keys                = first + mid + last

        for i in range(0, len(results)):
            results[i]      = list(itemgetter(*keys)(results[i]))

def sort_list_dois_first(results):
    # sorts the results list, dois first. helps later, because then titles are always behind dois

    if len(results[0]) > 1:
        from definitions import is_doi
        from operator    import itemgetter
        dois            = list()
        no_dois         = list()
        for i in range(0, len(results[1])):
            if is_doi(results[1][i]):
                dois.append(i)
            else:
                no_dois.append(i)

        keys            = dois + no_dois

        for i in range(0, len(results)):
            results[i]  = list(itemgetter(*keys)(results[i]))

def transform_failed_searches(failed_message):
    # exchanges the numbers of the failed_message with the actual words
    for i in range(0, len(failed_message[0])):
        if failed_message[0][i] == 1: failed_message[0][i] = "Study_Register"
        if failed_message[0][i] == 2: failed_message[0][i] = "Pubmed"
        if failed_message[0][i] == 3: failed_message[0][i] = "Cochrane_Library"
        if failed_message[0][i] == 4: failed_message[0][i] = "Google_Scholar"
        if failed_message[0][i] == 5: failed_message[0][i] = "Livivo"
        if failed_message[0][i] == 6: failed_message[0][i] = "Trip_Database"
        if failed_message[0][i] == 7: failed_message[0][i] = "base-search.net"
        if failed_message[0][i] == 8: failed_message[0][i] = "UB_Freiburg"
        if failed_message[0][i] == 9: failed_message[0][i] = "WebOfKnowledge"

def empty_output(keep):
    # creates the empty output with the correct number of columns
    # as well as the later header for the source where everything was found
    from pubmed_plugins import empty_bib
    output      = empty_bib()
    preheader   = list()
    sourceheader= list()
    subheader   = list()

    # for original study id
    output.append(list())
    preheader.append("SearchTerm")

    if keep.study_reg == 1:
        output.append(list())
        sourceheader.append("FV_Study_Registers")
    if keep.pubmed == 1:
        output.append(list())
        sourceheader.append("FV_Pubmed")
    if keep.cochrane_lib == 1:
        output.append(list())
        sourceheader.append("FV_Cochrane_Library")
    if keep.google_scholar == 1:
        output.append(list())
        sourceheader.append("FV_Google_Scholar")
    if keep.livivo == 1:
        output.append(list())
        sourceheader.append("FV_Livivo")
    if keep.trip_db == 1:
        output.append(list())
        sourceheader.append("FV_Trip_Database")
    if keep.base_search == 1:
        output.append(list())
        sourceheader.append("FV_base-search")
    if keep.ub_fr == 1:
        output.append(list())
        sourceheader.append("FV_UB_Freiburg")
    if keep.wos == 1:
        output.append(list())
        sourceheader.append("FV_WebOfKnowledge")

    # for urls
    output.append(list())
    subheader.append('source_urls')

    # for attention required
    output.append(list())
    subheader.append('attention_required')

    return output, preheader, sourceheader, subheader

###########################################################
###########################################################
########### check for results of study registers ##########
###########################################################
###########################################################

def check_for_available_results(ch_study_ids, org_source, folders):
    ## function that checks whether there were results posted in the different study registers
    from definitions import simplify_text
    from study_registers_plugins import check_for_study_reg_results_NCT, check_for_study_reg_results_EudraCT, check_for_study_reg_results_DRKS, check_for_study_reg_results_ISRCTN

    stud_res            = [list(), list()]

    for i in range(0, len(ch_study_ids)):
        asource         = identify_source(ch_study_ids[i], org_source)

        stud_res[0].append(ch_study_ids[i])

        if simplify_text(org_source[0][asource]) == simplify_text("NCT"):
            stud_res[1].append(check_for_study_reg_results_NCT(ch_study_ids[i], folders))

        elif simplify_text(org_source[0][asource]) == simplify_text("DRKS"):
            stud_res[1].append(check_for_study_reg_results_DRKS(ch_study_ids[i], folders))

        elif simplify_text(org_source[0][asource]) == simplify_text("ISRCTN"):
            stud_res[1].append(check_for_study_reg_results_ISRCTN(ch_study_ids[i], folders))

        elif simplify_text(org_source[0][asource]) == simplify_text("EudraCT"):
            stud_res[1].append(check_for_study_reg_results_EudraCT(ch_study_ids[i], folders))

    return stud_res

###########################################################
###########################################################
########### download results of study registers ###########
###########################################################
###########################################################

def download_study_register_results(browser, ch_study_ids, folders, org_sources, stud_reg_res, http):
    import datetime
    from definitions import simplify_text, remaining_time, printProgressBar
    from study_registers_plugins import download_results_nct, download_results_eudract

    show_string         = 'Downloading Stud.Reg. Results'
    start_time          = datetime.datetime.now()
    runner              = 0
    printProgressBar(runner, len(ch_study_ids), prefix=show_string, suffix="remaining: 0:00:00:00", length=50)

    for id in ch_study_ids:

        # check if there are results to download
        idx             = stud_reg_res[0].index(id)
        if stud_reg_res[1][idx] == 1:

            asource     = identify_source(id, org_sources)
            url         = org_sources[2][asource].replace("???", id)

            if simplify_text(org_sources[0][asource]) == simplify_text("NCT"):
                download_results_nct(id, url, folders)

            elif simplify_text(org_sources[0][asource]) == simplify_text("DRKS"):
                a = 1

            elif simplify_text(org_sources[0][asource]) == simplify_text("ISRCTN"):
                a = 1

            elif simplify_text(org_sources[0][asource]) == simplify_text("EudraCT"):
                download_results_eudract(id, url, folders, http)

        runner          = runner + 1
        printProgressBar(runner, len(ch_study_ids), prefix=show_string,
                         suffix=remaining_time(start_time=start_time, step=runner, max=len(ch_study_ids)),
                         length=50)

###########################################################
###########################################################
##################### other Defs ##########################
###########################################################
###########################################################

def identify_dois(ch_study_ids, study_ids, sources, http, folder):
    import datetime
    from study_registers_plugins    import extract_dois_NCT, extract_dois_DRKS, extract_dois_ISRCTN, extract_dois_EudraCT
    from definitions                import printProgressBar, remaining_time

    show_string         = 'Searching Study Registers'
    result              = list([list(), list()])
    missings            = list()
    failed_dois         = list([list(), list()])
    total_fails         = list()

    start_time          = datetime.datetime.now()

    for i in range(0, len(ch_study_ids)):
        # print(i, study_ids[i])
        id              = identify_source(study_ids[i], sources)  # check which parser to use

        f               = open(folder.html + ch_study_ids[i] + ".html")  # open html file
        cont            = f.read()
        f.close()

        tmp             = list()
        fds             = list()

        if sources[0][id] == "NCT":
            tmp, fds    = extract_dois_NCT(cont, http)

        elif sources[0][id] == "DRKS":
            tmp, fds    = extract_dois_DRKS(cont, http)

        elif sources[0][id] == "ISRCTN":
            tmp, fds    = extract_dois_ISRCTN(cont, http)

        #elif sources[0][id] == "EudraCT":
        #    tmp, fds    = extract_dois_EudraCT(cont, http)

        else:
            total_fails.append(i)

        tmp             = sorted(set(tmp), key=tmp.index)  # removes dublicates; keeps order sequence
        for j in range(0, len(tmp)):
            result[0].append(i)
        result[1]       = result[1] + tmp

        for j in range(0, len(fds)):
            failed_dois[0].append(i)
        failed_dois[1]  = failed_dois[1] + fds

        if (len(tmp) == 0) & (len(fds) == 0):
            missings.append(study_ids[i])

        # print(len(tmp), len(fds))

        printProgressBar(i + 1, len(ch_study_ids), prefix=show_string,
                         suffix=remaining_time(start_time=start_time, step=i, max=len(study_ids)),
                         length=50)

    return result, missings, failed_dois, total_fails

##################################################################

def identify_source(id, sources):
    from definitions import simplify_text
    for vgl in range(0, len(sources[0])):
        if simplify_text(id).find(simplify_text(sources[0][vgl])) > -1:
            return vgl
    ## try to find EUDRACT. is set when input is only number
    clear_id    = simplify_text(id, ausnahmen=["0","1","2","3","4","5","6","7","8","9"])
    try:
        m       = int(clear_id)
        vgl     = sources[0].index("EudraCT")
        return vgl
    except:
        return -1

##################################################################

def prepare_study_reg_names_for_study_reg_search(study_ids):
    # replaces Study_ids so that they are directly accessable in the study registers
    # forbidden_words is a list of lists; inner lists consist of #1: to replace, #2: replace with
    forbidden_words         = [["EudraCT", ""], ["EUDRACT",""], ["eudract",""], [chr(32), ""]]
    for i in range(0, len(study_ids)):
        for j in range(0,len(forbidden_words)):
            study_ids[i]    = study_ids[i].replace(forbidden_words[j][0],forbidden_words[j][1])
    return study_ids

##################################################################

def add_multiple_results(results, study_ids, dois, failed_dois, urls, method):
    # alters result list directly in memory; so no return
    # adds multiple entries, that are tangled within each other (i.e. doi=[[0,0,1],[10.d, 10.id, [10.kds]])
    # was written for the study register search
    for i in range(0, len(dois[1])):
        results[0].append(dois[0][i])           # add study_id_nr
        results[1].append(dois[1][i])           # add doi
        results[2].append(urls[dois[0][i]])     # add url
        results[3].append(method)               # method that found the ref (e.g. Pubmed, google scholar, aso.)
    for i in range(0, len(failed_dois[1])):
        results[0].append(dois[0][i])           # add study_id_nr
        results[1].append(dois[1][i])           # add "title" (where no doi was found)
        results[2].append(urls[dois[0][i]])     # add url
        results[3].append(method)               # method that found the ref (e.g. Pubmed, google scholar, aso.)

def add_single_result(results, studyID, input, url, method):
    from definitions import string_2_html
    results[0].append(studyID)                  # add study_id_nr
    results[1].append(string_2_html(input, direction="from_html"))                    # add doi or title or other
    results[2].append(url)                      # add url
    results[3].append(method)                   # method that found the ref (e.g. Pubmed, google scholar, aso.)