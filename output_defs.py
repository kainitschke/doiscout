##################################################################

def writing_file(file, folder=list(), mode=1):
    if   mode == 1:
        import os.path
        if os.path.isfile(folder.main + file) == True: # create random stamp if file already exists
            import random
            file = file[0:-4] + '_' + ''.join([random.choice('abcdefghijklmnopqrstuvwxyz') for _ in range(8)]) + '.txt'
        f = open(folder.main + file, 'w')
        return f

    elif mode == 2:
        file.close()

def reading_file(file, path, mode=1):
    if   mode == 1:
        import os.path
        f = open(path + file, 'r')
        return f

    elif mode == 2:
        file.close()

def write_output_extract_bib_info(bib_info, failed, folders, timestamp):
    from pubmed_plugins import add_headers_bib_info, empty_bib
    from pandas import DataFrame

    # bib info
    filename            = folders.main + "%s_Extracted_Bib_Info.xlsx" % timestamp
    # afile       = writing_file(filename, folders, 1)
    # bib_info    = add_headers_bib_info(bib_info)
    # write_linewise_goofy(afile, bib_info)
    # writing_file(afile, folders, 2)

    header              = [item[0] for item in add_headers_bib_info(empty_bib())]
    data                = DataFrame(bib_info).transpose()
    data.columns        = header
    data.to_excel(filename, sheet_name="Bib_Info", index=False)

    # failed info retrieval
    if len(failed) > 0:
        filename        = folders.main + "%s_Failed_Bib_Info.xlsx" % timestamp
        #afile       = writing_file(filename, folders, 1)
        #write_linewise_goofy(afile, [failed])
        #writing_file(afile, folders, 2)
        fail            = DataFrame(failed)
        fail.columns    = ["Failed Retrieval"]
        fail.to_excel(filename, sheet_name="Bib_Info", index=False)

def write_output_register_search_old(dois, no_dois, failed_dois, total_fails, study_ids, timestamp, folders):
    from definitions    import printProgressBar
    
    show_string = 'Writing Text Files'
    printProgressBar(0, 5, prefix=show_string, suffix="remaining: 0:00:00:00", length=50)

    write_output_register_fails(total_fails, study_ids, timestamp, folders)
    printProgressBar(1, 5, prefix=show_string, suffix="remaining: 0:00:00:00", length=50)

    write_output_file_dois(dois, timestamp, folders)
    printProgressBar(2, 5, prefix=show_string, suffix="remaining: 0:00:00:00", length=50)

    write_output_file_no_dois(no_dois, timestamp, folders)
    printProgressBar(3, 5, prefix=show_string, suffix="remaining: 0:00:00:00", length=50)

    write_output_results_lines(  dois, failed_dois, study_ids, timestamp, folders)
    printProgressBar(4, 5, prefix=show_string, suffix="remaining: 0:00:00:00", length=50)

    write_output_results_columns(dois, failed_dois, study_ids, timestamp, folders)
    printProgressBar(5, 5, prefix=show_string, suffix="remaining: 0:00:00:00", length=50)

def write_output_register_fails(total_fails, study_ids, timestamp, folder):
    filename        = "%s_1_Study_Register_Failed_Registers.txt" % timestamp
    afile           = writing_file(filename, folder)
    writing_fails   = list()
    for i in range(0, len(total_fails)):
        writing_fails.append(study_ids[total_fails[i]])
    write_linewise(afile, [writing_fails])
    writing_file(afile, mode=2)

def write_output_file_dois(dois, timestamp, folder):
    from definitions import remove_dublicates
    filename        = "%s_1_Study_Register_Recognized_dois.txt" % timestamp
    afile           = writing_file(filename, folder)
    to_write_dois   = remove_dublicates(dois[1])
    write_linewise(afile, [to_write_dois])
    writing_file(afile, mode=2)

def write_output_file_no_dois(register_ids, timestamp, folder):
    filename        = "%s_1_Study_Register_No_Results.txt" % timestamp
    afile           = writing_file(filename, folder)
    write_linewise(afile, [register_ids])
    writing_file(afile, mode=2)

def write_output_results_lines(dois, failed_dois, study_ids, timestamp, folder):
    filename = "%s_1_Study_Register_Results_in_Lines.txt" % timestamp
    afile = writing_file(filename, folder)
    lin = list([list(), list()])
    for i in range(0, len(dois[0])):
        lin[0].append(study_ids[dois[0][i]])
        lin[1].append(dois[1][i])
    for i in range(0,len(failed_dois[0])):
        lin[0].append(study_ids[failed_dois[0][i]])
        lin[1].append(failed_dois[1][i])
    ## sorting
    lin[0],lin[1] = zip(*sorted(zip(lin[0], lin[1])))

    write_linewise(afile, lin)
    writing_file(afile, mode=2)

def write_output_results_columns(dois, failed_dois, study_ids, timestamp, folder):
    filename        = "%s_1_Study_Register_Results_in_Columns.txt" % timestamp
    afile           = writing_file(filename, folder)
    for ids in range(0,len(study_ids)):
        astring     = ""
        idx_dois    = [i for i, x in enumerate(dois[0])        if x == ids]
        idx_faildois= [i for i, x in enumerate(failed_dois[0]) if x == ids]
        for i in idx_dois:
            astring = astring + dois[1][i] + "\t"
        for i in idx_faildois:
            astring = astring + failed_dois[1][i] + "\t"
        if (idx_dois != list())|(idx_faildois != list()):
            astring = study_ids[ids] + "\t" + astring[0 : len(astring)-1] + "\n"
            afile.write(astring)
    writing_file(afile, mode=2)

def write_output_download_pdfs(dois, others, timestamp, folder):
    from pandas import DataFrame
    filename        = folder.main + "%s_PDFs_not_obtained.xlsx" % timestamp
    #afile           = writing_file(filename, folder)
    #write_linewise(afile, [dois + others])
    #writing_file(afile, mode=2)
    fail            = DataFrame([dois + others]).transpose()
    fail.columns    = ["Failed PDF Downloads"]
    fail.to_excel(filename, sheet_name="Failed_PDF_Downloads", index=False)

def write_linewise(afile, text):
    import platform
    for row in range(0, len(text[0])):
        astring     = ""
        for column in range(0, len(text)):
            if platform.system() == "Windows":
                astring = astring + '"' + text[column][row].replace('"', "'").encode('ascii', 'ignore').decode('ascii') + '"' + "\t"
            else:
                astring = astring + '"' + text[column][row].replace('"', "'").encode('utf-8', 'ignore').decode('utf-8') + '"' + "\t"
        astring     = astring[0:len(astring)-1] + "\n"
        #astring     = astring.replace('"', "'")
        afile.write(astring)

def write_linewise_goofy(afile, text, no_quotation=False):
    # changes if the input is organized otherwise. for example for "extract bib info"
    # where all dois are stored in same list but not all information for the single doi
    import platform
    for row in range(0, len(text[0])):
        astring     = ""
        for column in range(0, len(text)):
            if no_quotation==False: astring = astring + '"'
            if type(text[column][row]) is str:
                if platform.system() == "Windows":
                    astring = astring + text[column][row].replace('"', "'").encode('ascii', 'ignore').decode('ascii')
                else:
                    astring = astring + text[column][row].replace('"', "'").encode('utf-8', 'ignore').decode('utf-8')
            else:
                astring = astring + '%d' % text[column][row]
            if no_quotation == False: astring = astring + '"'
            astring     = astring + "\t"
        astring     = astring[0:len(astring) - 1] + "\n"
        #astring     = astring.replace('"', "'")
        afile.write(astring)

def write_output_guideline(bib_info, folders, timestamp, keep = False):
    #import xlwt
    from pubmed_plugins import add_headers_bib_info, empty_bib
    from definitions import empty_guidelines
    from pandas import DataFrame

    afile           = folders.main + timestamp + "_Guideline_Search" + ".xlsx"

    header          = [item[0] for item in add_headers_bib_info(empty_bib())]
    header[0:0]     = empty_guidelines(title="alternative", keep=keep)

    data            = DataFrame(bib_info).transpose()
    data.columns    = header

    data.to_excel(afile, sheet_name="Guidelines", index=False)



##################################################################
##################################################################

def write_output_register_search(wrapped, header, no_results, failed_message, folders, timestamp):
    from pandas import DataFrame
    from pubmed_plugins import add_headers_bib_info, empty_bib
    ##### MAIN RESULTS
    filename        = folders.main + "%s_Results_Register_Search.xlsx" % timestamp
    #afile       = writing_file(filename, folders, 1)
    # insert header
    #for i in range(0, len(wrapped)):
    #    wrapped[i].insert(0, header[i])
    #write_linewise(afile, wrapped)
    #writing_file(afile, mode=2)
    if wrapped != []:
        data            = DataFrame(wrapped).transpose()
        data.columns    = header
        data.to_excel(filename, sheet_name="StudyReg_Search", index=False)

    ##### NO RESULTS
    filename        = folders.main + "%s_NoResults_Register_Search.xlsx" % timestamp
    #afile       = writing_file(filename, folders, 1)
    #for i in range(0, len(no_results)):
    #    afile.write(no_results[i] + "\n")
    #writing_file(afile, mode=2)
    if no_results != []:
        data            = DataFrame(no_results)
        data.columns    = ["No_Results_Register_Search"]
        data.to_excel(filename, sheet_name="StudyReg_Search", index=False)

    ##### ERRORS
    filename        = folders.main + "%s_Errors_Register_Search.xlsx" % timestamp
    #afile           = writing_file(filename, folders, 1)
    #write_linewise(afile, failed_message)
    #writing_file(afile, mode=2)
    if failed_message[1] != []:
        data            = DataFrame(failed_message[1])
        data.columns    = ["Errors_in_Register_Search"]
        data.to_excel(filename, sheet_name="StudyReg_Search", index=False)


##################################################################
##################################################################
def write_output_cited_by(bib_info, header, folders, timestamp):
    from pandas import DataFrame
    filename        = folders.main + "%s_Results_Cited_By.xlsx" % timestamp
    #afile       = writing_file(filename, folders, 1)
    #for i in range(0, len(bib_info)):
    #    bib_info[i].insert(0, header[i][0])
    #write_linewise(afile, bib_info)
    #writing_file(afile, mode = 2)
    data            = DataFrame(bib_info).transpose()
    data.columns    = [item[0] for item in header]
    data.to_excel(filename, sheet_name="CitedBy_Search", index=False)

##################################################################
##################################################################
def write_output_is_in_cochrane(results, header, folders, timestamp):
    filename    = "%s_Is_In_Cochrane.txt" % timestamp
    afile       = writing_file(filename, folders, 1)
    for i in range(0, len(results)):
        results[i].insert(0, header[i])
    write_linewise(afile, results)
    writing_file(afile, mode=2)

##################################################################
##################################################################
def write_study_register_results(stud_reg_res, folders, timestamp):
    from pandas import DataFrame
    filename        = folders.main + "%s_Results_Provided_in_Study_Registers.xlsx" % timestamp
    #afile           = writing_file(filename, folders, 1)
    #stud_reg_res[1] = [str(x) for x in stud_reg_res[1]] # change integers to strings
    #stud_reg_res[0].insert(0, "SearchTerm")
    #stud_reg_res[1].insert(0, "Study_Results_Provided")
    #write_linewise(afile, stud_reg_res)
    #writing_file(afile, mode=2)
    data            = DataFrame(stud_reg_res).transpose()
    data.columns    = ["SearchTerm", "Study_Results_Provided"]
    data.to_excel(filename, sheet_name="StudyReg_Search", index=False)

##################################################################
##################################################################
#### Endnote #####################################################
##################################################################
def read_bib_info_file(apath, afile):
    from pubmed_plugins import empty_bib
    f           = reading_file(afile, apath, mode = 1)

    header      = f.readline().split(sep="\t")
    header[-1]  = header[-1].replace("\n","")
    bib_info    = empty_bib()
    string      = f.readline().split(sep="\t")
    while string != ['']:
        for i in range(0, len(string)):
            bib_info[i].append(string[i].replace("\n", ""))
        string  = f.readline().split(sep="\t")

    reading_file(f, "", mode = 2)
    return bib_info, header

def correct_for_endnote(bib_info, header, folder):
    #from pubmed_plugins import empty_bib, add_headers_bib_info
    from os import path
    from definitions import folder_structure, doi_2_filename

    print("Start Conversion")
    org         = ["DOI", "Title", "Number of Authors", "Author",
                   "Country",  "Year", "Journal",         "Volume", "Issue",
                   "Pages", "Cited_By_Pubmed", "Cited_By_WoS",
                   "URL", "Abstract",
                   "evidence-level", "society",
                   "Parent-DOI", "Original_DOI"]
    repl        = ["DOI", "Title", "Custom 1", "Author",
                   "Custom 2", "Year", "Secondary Title", "Volume", "Number",
                   "Pages", "Custom 3", "Custom 4",
                   "URL", "Abstract",
                   "Custom 5", "Custom 6",
                   "Custom 7", "Custom 8"]

    raus                = list()
    for i in range(0, len(header)):
        try:
            h           = org.index(header[i])
            header[i]   = repl[h]

        except:
            raus.append(i)

    for i in range(len(raus), 0 , -1):
        header.pop(raus[i-1])
        bib_info.pop(raus[i-1])

    ## add reference type (necessary for endnote; just ignore
    header.append("Reference Type")
    bib_info.append([])
    for i in range(0,len(bib_info[0])):
        bib_info[len(bib_info) - 1].append("Journal Article")

    ## add path to file attachments
    header.append("File Attachments")
    bib_info.append([])
    idx                 = header.index("DOI")
    for i in range(0, len(bib_info[0])):
        if path.isfile(folder.pdf + doi_2_filename(bib_info[idx][i]) + ".pdf") == True:
            bib_info[len(bib_info) - 1].append(folder.pdf + doi_2_filename(bib_info[idx][i]) + ".pdf")
        else:
            bib_info[len(bib_info) - 1].append(" ")

    print("Finished Conversion")

def write_output_endnote(bib_info, folders, filename):
    afile       = writing_file(filename, folders, 1)
    write_linewise_goofy(afile, bib_info, no_quotation=True)
    writing_file(afile, folders, 2)