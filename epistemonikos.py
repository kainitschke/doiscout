
def abgleich():
    results, references, res_idx, ref_idx, resfile = read_files()
    make_abgleich(results, references, res_idx, ref_idx)
    write_output(results, res_idx, resfile)


##################################################################
def make_abgleich(results, references, res_idx, ref_idx):
    from definitions import simplify_text

    ref_type_idx        = ref_idx.index("CLASSIFICATION")

    ref_doi_idx         = ref_idx.index("DOI")
    ref_dois            = []
    for i in range(0, len(references)):
        ref_dois.append(references[i][ref_doi_idx])
    ref_title_idx       = ref_idx.index("TITLE")
    ref_title           = []
    for i in range(0, len(references)):
        try:
            ref_title.append(simplify_text(references[i][ref_title_idx]))
        except:
            ref_title.append("zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz")
    ref_pmid_idx        = ref_idx.index("PUBMED_ID")
    ref_pmid            = []
    for i in range(0, len(references)):
        ref_pmid.append(references[i][ref_pmid_idx])

    res_doi_idx         = res_idx.index("DOI")
    res_pmid_idx        = res_idx.index("PubmedID")
    res_title_idx       = res_idx.index("Title")
    for i in range(0, len(results)):
        ## check if doi
        try:
            if results[i][res_doi_idx].strip() == "":
                lalala
            l           = ref_dois.index(results[i][res_doi_idx])
            t           = references[l][ref_type_idx]

        except:
            ## check in Pubmed ID
            try:
                if results[i][res_pmid_idx].strip() == "":
                    lalala
                l       = ref_pmid.index(results[i][res_pmid_idx])
                t       = references[l][ref_type_idx]

            except:
                ## check if title
                try:
                    if results[i][res_title_idx].strip() == "":
                        lalala
                    l   = ref_title.index(simplify_text(results[i][res_title_idx]))
                    t   = references[l][ref_type_idx]
                except:
                    t   = "not in epi"
        results[i].append(t)
        ## check if title





##################################################################
def read_files():
    from os import path
    from tkfilebrowser import askopenfilename
    import xlrd

    resfile = path.split(askopenfilename(parent=None, title="Select Result-File", filetypes=(("Excel files", "*.xls*"), ("all files", "*.*")))) # path.split("/media/GCC/bluemle/Projekte/DFG/IIT/Zitierung/20190614_All_Results_Cited_By.xlsx") #
    reffile = path.split(askopenfilename(parent=None, title="Select Epistemonikos-File", initialdir= resfile[0],filetypes=(("Excel files", "*.xls*"), ("all files", "*.*")))) # path.split("/media/GCC/bluemle/Projekte/DFG/IIT/Zitierung/epistemonikos_alt.xlsx") #

    valfile = xlrd.open_workbook(resfile[0] + path.sep + resfile[1])
    sheet = valfile.sheet_by_index(0)
    results = []
    res_idx = []
    for i in range(0, sheet.ncols):
        res_idx.append(sheet.cell_value(0, i))
    for i in range(1, sheet.nrows):
        results.append([])
        for j in range(0, sheet.ncols):
            results[i - 1].append(str(sheet.cell_value(i, j)))

    valfile = xlrd.open_workbook(reffile[0] + path.sep + reffile[1])
    sheet = valfile.sheet_by_index(0)
    references = []
    ref_idx = []
    for i in range(0, sheet.ncols):
        ref_idx.append(sheet.cell_value(0, i))
    for i in range(1, sheet.nrows):
        references.append([])
        for j in range(0, sheet.ncols):
            references[i - 1].append(str(sheet.cell_value(i, j)))

    return results, references, res_idx, ref_idx, resfile

##################################################################
def write_output(results, res_idx, resfile):
    from output_defs import write_linewise
    from os import path

    results.insert(0,[])
    for i in range(0, len(res_idx)):
        results[0].append(res_idx[i])
    results[0].append("Epistemonikos")

    afile       = open(resfile[0] + path.sep + "epi_" + resfile[1][0:len(resfile[1])-5] + ".txt", "w")

    for row in range(0, len(results)):
        astring     = ""
        for column in range(0, len(results[0])):
            astring = astring + '"' + results[row][column].replace('"', "'") + '"' + "\t"
        astring     = astring[0:len(astring)-1] + "\n"
        afile.write(astring)

    afile.close()