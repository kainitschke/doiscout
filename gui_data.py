def start_gui():
    from tkinter import mainloop
    keep    = create_keep
    gui     = create_gui("main", keep)
    mainloop()                              # wait for input

def create_gui(mode, keep):
    import tkinter
    import platform
    gui             = tkinter.Tk()          # initialize GUI
    gui_sett        = gui_data(gui)         # get settings for position and size
    elements        = initialize_elements() # set all buttons empty

    
    if mode == "main":                      # Main Window
        title                            = "DOI Scout"
        draw_gui(gui, gui_sett, keep)

        elements.buttons.extract_bib_info= tkinter.Button(master=gui, text="Extract Bib Info",                  command=lambda: gui_extract_bib_info(gui, keep))      # lambda that command is not executed right away
        elements.buttons.pdf_download    = tkinter.Button(master=gui, text="Download PDFs from DOIs",           command=lambda: gui_download_pdfs(gui, keep))         # lambda that command is not executed right away
        elements.buttons.study_registers = tkinter.Button(master=gui, text="Extract DOIs from Study Registers", command=lambda: gui_study_registers_dois(gui, keep))
        elements.buttons.cited_by        = tkinter.Button(master=gui, text="Cited By",                          command=lambda: gui_cited_by(gui, keep))
        elements.buttons.guidelines      = tkinter.Button(master=gui, text="Cited in Guidelines",               command=lambda: gui_guidelines(gui, keep))
        elements.buttons.is_in_cochrane  = tkinter.Button(master=gui, text="Is in Cochrane Lib",                command=lambda: gui_is_in_cochrane(gui, keep))
        elements.buttons.to_endnote      = tkinter.Button(master=gui, text="Convert to Endnote",                command=lambda: gui_to_endnote(gui, keep))
        elements.buttons.manual          = tkinter.Button(master=gui, text="Manual",                            command=lambda: gui_action_help())
        elements.buttons.quit            = tkinter.Button(master=gui, text="Quit",                              command=lambda: gui_quit(gui, elements, keep))

    elif (mode=="extract_bib_info")|(mode=="pdf_download")|(mode=="study_registers")|(mode=="cited_by")|(mode=="guidelines")|(mode=="is_in_cochrane"): # other windows but not options
        draw_gui(gui, gui_sett, keep)

        elements.buttons.back            = tkinter.Button(master=gui, text="Back",                              command=lambda: gui_action_back(gui,elements, keep))
        elements.buttons.help            = tkinter.Button(master=gui, text="?",                                 command=lambda: gui_action_help())
        elements.buttons.resultdir       = tkinter.Button(master=gui, text="Result Folder",                     command=lambda: gui_action_resultdir(elements))
        elements.edits.resultdir         = tkinter.Entry( master=gui)
        if platform.system() == "Linux":
            elements.labels.email        = tkinter.Label( master=gui, text="e-mail address:")
        elements.edits.email             = tkinter.Entry( master=gui)
        elements.edits.dois              = tkinter.Text(  master=gui)
        elements.labels.status           = tkinter.Label( master=gui, text="Info: ")

    if (mode=="extract_bib_info")|(mode=="pdf_download")|(mode=="study_registers")|(mode=="cited_by")|(mode=="is_in_cochrane"): # other windows but not options
        elements.buttons.read_raw = tkinter.Button(master=gui, text="Read RAW File",                            command=lambda: gui_action_read_raw(elements))

    if mode == "extract_bib_info":
        title = "DOI Scout: Extract Bib Info"
        elements.labels.title       = tkinter.Label(master=gui, text="Enter DOIs or publication titles:")
        elements.buttons.run        = tkinter.Button(master=gui, text="Run",            command=lambda: gui_action_extract_bib_info(elements))
        elements.buttons.read_wos   = tkinter.Button(master=gui, text="Read WoS File",  command=lambda: gui_action_read_wos(elements))
        elements.buttons.read_ncbi  = tkinter.Button(master=gui, text="Read ncbi File", command=lambda: gui_action_read_ncbi(elements))
        elements.checks.download    = tkinter.Checkbutton(master=gui, text="Download PDFs")

    if mode == "pdf_download":
        title                       = "DOI Scout: Download PDFs"
        elements.labels.title       = tkinter.Label( master=gui, text="Enter DOIs or publication titles:")
        elements.buttons.run        = tkinter.Button(master=gui, text="Run",            command=lambda: gui_action_pdfs_download(elements))
        elements.buttons.read_wos   = tkinter.Button(master=gui, text="Read WoS File",  command=lambda: gui_action_read_wos(elements))
        elements.buttons.read_ncbi  = tkinter.Button(master=gui, text="Read ncbi File", command=lambda: gui_action_read_ncbi(elements))
        elements.checks.extract_bib = tkinter.Checkbutton(master=gui, text="Extract Bib Info")

    if mode == "study_registers":
        title                       = "DOI Scout: Study Registers"
        elements.labels.title       = tkinter.Label( master=gui, text="Enter Study Register Numbers:")
        elements.buttons.run        = tkinter.Button(master=gui, text="Run",            command=lambda: gui_action_study_register(elements, keep))
        elements.checks.download    = tkinter.Checkbutton(master=gui, text="Download PDFs")
        if keep.study_reg == 1:
            elements.checks.study_res   = tkinter.Checkbutton(master=gui, text="Downl. Regist. Results")
        #elements.checks.extract_bib = tkinter.Checkbutton(master=gui, text="Extract Bib Info")

    if mode == "cited_by":
        title                       = "DOI Scout: Cited By"
        elements.labels.title       = tkinter.Label( master=gui, text="Enter DOIs or publication titles:")
        elements.buttons.run        = tkinter.Button(master=gui, text="Run",            command=lambda: gui_action_cited_by(elements))
        elements.buttons.read_wos   = tkinter.Button(master=gui, text="Read WoS File",  command=lambda: gui_action_read_wos(elements))
        elements.buttons.read_ncbi  = tkinter.Button(master=gui, text="Read ncbi File", command=lambda: gui_action_read_ncbi(elements))
        elements.labels.depth       = tkinter.Label( master=gui, text="Depth")
        elements.edits.depth        = tkinter.Entry( master=gui)
        elements.checks.download    = tkinter.Checkbutton(master=gui, text="Download PDFs")
        #elements.checks.extract_bib = tkinter.Checkbutton(master=gui, text="Extract Bib Info")

    if mode == "guidelines":
        title                           = "DOI Scout: Cited in Guidelines"
        if keep.guide_mode == "studreg":
            elements.labels.title           = tkinter.Label(master=gui, text="Enter Study Register Numbers:")
            elements.buttons.read_raw       = tkinter.Button(master=gui, text="Read RAW File",      command=lambda: gui_action_read_raw(elements))
        elif keep.guide_mode == "doi":
            elements.labels.title           = tkinter.Label(master=gui, text="Set path to DoiScout-File below:")
            elements.buttons.read_doi_scout = tkinter.Button(master=gui, text="Read DoiScout File", command=lambda: gui_action_read_doi_scout(elements, keep))

        elements.buttons.run            = tkinter.Button(master=gui, text="Run",                    command=lambda: gui_action_guidelines(elements, keep))

        elements.checks.extract_bib     = tkinter.Checkbutton(master=gui, text="Extract Bib Info")
        #elements.buttons.read_wos      = tkinter.Button(master=gui, text="Read WoS File",  command=lambda: gui_action_read_wos(elements))
        #elements.buttons.read_ncbi     = tkinter.Button(master=gui, text="Read ncbi File", command=lambda: gui_action_read_ncbi(elements))
        #elements.checks.download       = tkinter.Checkbutton(master=gui, text="Download PDFs")

    if mode == "is_in_cochrane":
        title                       = "DOI Scout: Is in Cochrane Lib"
        elements.labels.title       = tkinter.Label( master=gui, text="Enter DOIs:")
        elements.buttons.run        = tkinter.Button(master=gui, text="Run",             command=lambda: gui_action_is_in_cochrane(elements))
        elements.buttons.read_wos   = tkinter.Button(master=gui, text="Read WoS File",   command=lambda: gui_action_read_wos(elements))
        elements.buttons.read_ncbi  = tkinter.Button(master=gui, text="Read ncbi File",  command=lambda: gui_action_read_ncbi(elements))

    if mode == "register_options":  # options for
        draw_gui(gui, gui_sett, keep, type="options_reg")
        gui_sett.height             = gui_sett.subregheight
        gui_sett.width              = gui_sett.subregwidth
        gui_sett.xpos               = gui_sett.subregxpos
        gui_sett.ypos               = gui_sett.subregypos


        title                       = "DOI Scout: Study Register Search Options"
        elements.buttons.register_options_okay  = tkinter.Button(master=gui, text="Next",          command=lambda: gui_register_options_apply(gui, elements))
        elements.labels.title       = tkinter.Label(master=gui, text="Choose where to search:")
        elements.checks.study_reg   = tkinter.Checkbutton(master=gui, text="Study Registers")
        elements.checks.pubmed      = tkinter.Checkbutton(master=gui, text="Pubmed")
        elements.checks.cochrane_lib    = tkinter.Checkbutton(master=gui, text="Cochrane Library")
        elements.checks.google_scholar  = tkinter.Checkbutton(master=gui, text="Google Scholar")
        elements.checks.livivo      = tkinter.Checkbutton(master=gui, text="Livivo")
        elements.checks.trip_db     = tkinter.Checkbutton(master=gui, text="Trip Database")
        elements.checks.base_search = tkinter.Checkbutton(master=gui, text="base-search.net")
        elements.checks.ub_fr       = tkinter.Checkbutton(master=gui, text="University Library Freiburg")
        elements.checks.wos         = tkinter.Checkbutton(master=gui, text="Web of Science")

    if mode == "guidelines_options":
        draw_gui(gui, gui_sett, keep, type="options_guidelines")
        gui_sett.height             = gui_sett.subguideheight
        gui_sett.width              = gui_sett.subguidewidth
        gui_sett.xpos               = gui_sett.subguidexpos
        gui_sett.ypos               = gui_sett.subguideypos

        title                       = "DOI Scout: Cited in Guidelines Options"
        elements.buttons.guidelines_options_okay = tkinter.Button(master=gui, text="Next",          command=lambda: gui_guidelines_options_apply(gui, elements))
        elements.labels.title       = tkinter.Label(master=gui, text="Choose where to search:")
        elements.checks.awmf        = tkinter.Checkbutton(master=gui, text="AWMF")
        elements.checks.nice        = tkinter.Checkbutton(master=gui, text="NICE")
        elements.checks.tripdb      = tkinter.Checkbutton(master=gui, text="Trip DB")

    if mode == "guidelines_mode":
        draw_gui(gui, gui_sett, keep, type="mode_guidelines")
        gui_sett.height             = gui_sett.subguideheight
        gui_sett.width              = gui_sett.subguidewidth
        gui_sett.xpos               = gui_sett.subguidexpos
        gui_sett.ypos               = gui_sett.subguideypos

        title                       = "DOI Scout: Cited in Guidelines Mode"
        elements.labels.title       = tkinter.Label(master=gui, text="Choose what to search:")
        elements.buttons.guidelines_studreg = tkinter.Button(master=gui, text="Study Register Number",          command=lambda: gui_guidelines_mode_studreg(gui, elements))
        elements.buttons.guidelines_doi     = tkinter.Button(master=gui, text="with Bibliographic Info",              command=lambda: gui_guidelines_mode_doi(gui, elements))

    gui.configure(background="black")  # Background Color as Black

    gui.title(title)
    display_elements(elements, gui_sett, keep)
    #gui.mainloop()
    return gui

def display_elements(elements, gui_sett, keep = list()):
    from tkinter import IntVar
    import platform

    rand                        = 20
    abstand                     = rand

    main_lines                  =  8 + 0
    subs_lines                  = 37 + 1
    study_reg_options_lines     =  9 + 1
    guidelines_options_lines    =  5 + 1
    guidelines_mode_lines       =  1.8 + 1

    try:    # main
        main_display_elements(elements.buttons.extract_bib_info,    0, gui_sett, rand, abstand, main_lines)
    except: pass
    try:    # main
        main_display_elements(elements.buttons.pdf_download,        1, gui_sett, rand, abstand, main_lines)
    except: pass
    try:    # main
        main_display_elements(elements.buttons.study_registers,     2, gui_sett, rand, abstand, main_lines)
    except: pass
    try:    # main
        main_display_elements(elements.buttons.cited_by,            3, gui_sett, rand, abstand, main_lines)
    except: pass
    try:    # main
        main_display_elements(elements.buttons.guidelines,          4, gui_sett, rand, abstand, main_lines)
    except: pass
    #try:    # main
    #    main_display_elements(elements.buttons.is_in_cochrane,      5, gui_sett, rand, abstand, main_lines)
    #except: pass
    try:    # main
        main_display_elements(elements.buttons.to_endnote,          5, gui_sett, rand, abstand, main_lines)
    except: pass
    try:  # main
        main_display_elements(elements.buttons.manual,              6, gui_sett, rand, abstand, main_lines)
    except: pass
    try:    # main
        main_display_elements(elements.buttons.quit,                7, gui_sett, rand, abstand, main_lines)
    except: pass

    try:    # Back Button
        aline   = 37
        sub_display_elements(element=elements.buttons.back, aline=aline, column_start=0,   column_end=0.5, rand=rand, subs_lines=subs_lines, abstand=abstand, gui_sett=gui_sett)
    except: pass
    try:    # Run Button
        aline   = 37
        sub_display_elements(element=elements.buttons.run,  aline=aline, column_start=0.5, column_end=1,   rand=rand, subs_lines=subs_lines, abstand=abstand, gui_sett=gui_sett)
    except: pass
    try:    # Read txt/raw file
        aline   = 27
        sub_display_elements(element=elements.buttons.read_raw,  aline=aline, column_start=0,  column_end=.333,   rand=rand, subs_lines=subs_lines, abstand=abstand, gui_sett=gui_sett)
    except: pass
    try:    # Read Wos (web of Science) file
        aline   = 27
        sub_display_elements(element=elements.buttons.read_wos,  aline=aline, column_start=0.333, column_end=.666,   rand=rand, subs_lines=subs_lines, abstand=abstand, gui_sett=gui_sett)
    except: pass
    try:    # Read Doi_scout_File
        aline   = 27
        sub_display_elements(element=elements.buttons.read_doi_scout,  aline=aline, column_start=0.0, column_end=.333,   rand=rand, subs_lines=subs_lines, abstand=abstand, gui_sett=gui_sett)
    except: pass
    try:    # Read Pubmed/NCBI (web of Science) file
        aline   = 27
        sub_display_elements(element=elements.buttons.read_ncbi, aline=aline, column_start=0.666, column_end=1,   rand=rand, subs_lines=subs_lines, abstand=abstand, gui_sett=gui_sett)
    except: pass
    try:    # e-mail Label
        aline   = 35
        if platform.system() == "Linux":
            sub_display_elements(element=elements.labels.email,  aline=aline, column_start=0, column_end=.3,   rand=rand, subs_lines=subs_lines, abstand=abstand, gui_sett=gui_sett, background="black", foreground="white", align="w")
    except: pass
    try:    # e-mail Entry
        aline   = 35
        #elements.edits.email.delete(0, len(elements.edits.email.get()))
        #elements.edits.email.insert(0, elements.keeps.email)
        if platform.system() == "Linux":
            sub_display_elements(element=elements.edits.email, aline=aline, column_start=.3, column_end=1,   rand=rand, subs_lines=subs_lines, abstand=abstand, gui_sett=gui_sett)
    except: pass
    try:    # DOIs / Main Entry
        aline   = [1,25]
        sub_display_elements(element=elements.edits.dois, aline=aline, column_start=0, column_end=1,   rand=rand, subs_lines=subs_lines, abstand=abstand, gui_sett=gui_sett)
    except: pass
    try:    # Depth - Label
        aline = 31
        sub_display_elements(element=elements.labels.depth, aline=aline, column_start=0, column_end=.15, rand = rand, subs_lines = subs_lines, abstand = abstand, gui_sett = gui_sett, background="black", foreground="white", align="w")
    except: pass
    try:    # Depth - Edit/Entry
        aline   = 31
        #elements.edits.depth.delete(0, len(elements.edits.depth.get()))
        elements.edits.depth.insert(0, "1")
        sub_display_elements(element=elements.edits.depth, aline=aline, column_start=.15,  column_end=.4,   rand=rand, subs_lines=subs_lines, abstand=abstand, gui_sett=gui_sett)
    except: pass
    try:    # Download PDFs - Check
        aline = 31
        sub_display_elements(element=elements.checks.download, aline=aline, column_start=.666, column_end=1, rand = rand, subs_lines = subs_lines, abstand = abstand, gui_sett = gui_sett, background="black", foreground="white")
        elements.checks.download.config(selectcolor="gray", activebackground="black",activeforeground="white")
        elements.checks.download.value      = IntVar()
        elements.checks.download.config(variable=elements.checks.download.value)
    except: pass
    try:    # Download the results stored in the study registers
        aline = 31
        sub_display_elements(element=elements.checks.study_res, aline=aline, column_start=.3, column_end=.666, rand = rand, subs_lines = subs_lines, abstand = abstand, gui_sett = gui_sett, background="black", foreground="white")
        elements.checks.study_res.config(selectcolor="gray", activebackground="black",activeforeground="white")
        elements.checks.study_res.value      = IntVar()
        elements.checks.study_res.config(variable=elements.checks.study_res.value)
    except: pass
    try:    # Extract Bibliography information (from pubmed)
        aline = 31
        sub_display_elements(element=elements.checks.extract_bib, aline=aline, column_start=.3, column_end=.666, rand = rand, subs_lines = subs_lines, abstand = abstand, gui_sett = gui_sett, background="black", foreground="white")
        elements.checks.extract_bib.config(selectcolor="gray", activebackground="black",activeforeground="white")

        elements.checks.extract_bib.value   = IntVar()
        elements.checks.extract_bib.config(variable=elements.checks.extract_bib.value)
    except: pass
    try:    # Label Main / Title
        aline = 0
        sub_display_elements(element=elements.labels.title, aline=aline, column_start=0, column_end=.8, rand=rand, subs_lines = subs_lines, abstand = abstand, gui_sett = gui_sett, background="black", foreground="white", align="w")
    except: pass
    try:    # Help (open Help PDF)
        aline = -.5
        sub_display_elements(element=elements.buttons.help, aline=aline, column_start=.8, column_end=1, rand=rand, subs_lines=subs_lines, abstand=abstand, gui_sett=gui_sett)
    except: pass
    try:    # Label - Info / Status
        aline = 29
        sub_display_elements(element=elements.labels.status, aline=aline, column_start=0, column_end=1, rand=rand, subs_lines=subs_lines, abstand=abstand, gui_sett=gui_sett, background="black", foreground="white", align="w")
    except: pass
    try:    # Choose Folder Entry
        aline = 33
        sub_display_elements(element=elements.edits.resultdir, aline=aline, column_start=.3, column_end=1, rand=rand, subs_lines=subs_lines, abstand=abstand, gui_sett=gui_sett)
        fill_result_dir(elements)
    except: pass
    try:    # Choose Folder Button
        aline = 33
        sub_display_elements(element=elements.buttons.resultdir, aline=aline, column_start=0, column_end=.3, rand=rand, subs_lines=subs_lines, abstand=abstand, gui_sett=gui_sett)
    except: pass

    ###################### sub register options ##############################
    try:    # option: Study Register
        aline = 1
        sub_display_elements(element=elements.checks.study_reg, aline=aline, column_start=0, column_end=1, rand = rand, subs_lines = study_reg_options_lines, abstand = abstand, gui_sett = gui_sett, background="black", foreground="white")
        elements.checks.study_reg.config(selectcolor="gray", activebackground="black",activeforeground="white")
        elements.checks.study_reg.value = IntVar()
        elements.checks.study_reg.config(variable=elements.checks.study_reg.value)
        elements.checks.study_reg.select() # pre-checked
    except: pass
    try:    # option: Pubmed
        aline = 2
        sub_display_elements(element=elements.checks.pubmed, aline=aline, column_start=0, column_end=1, rand = rand, subs_lines = study_reg_options_lines, abstand = abstand, gui_sett = gui_sett, background="black", foreground="white")
        elements.checks.pubmed.value = IntVar()
        elements.checks.pubmed.config(variable=elements.checks.pubmed.value, selectcolor="gray", activebackground="black",activeforeground="white")
        #elements.checks.pubmed.select() # pre-checked
    except: pass
    try:    # option: Cochrane Library
    #    aline = 3
    #    sub_display_elements(element=elements.checks.cochrane_lib, aline=aline, column_start=0, column_end=1, rand = rand, subs_lines = study_reg_options_lines, abstand = abstand, gui_sett = gui_sett, background="black", foreground="white")
        elements.checks.cochrane_lib.value = IntVar()
        elements.checks.cochrane_lib.config(variable=elements.checks.cochrane_lib.value, selectcolor="gray", activebackground="black",activeforeground="white")
        #elements.checks.cochrane_lib.select() # pre-checked
    except: pass
    try:    # option: Google Scholar
        aline = 3
        sub_display_elements(element=elements.checks.google_scholar, aline=aline, column_start=0, column_end=1, rand = rand, subs_lines = study_reg_options_lines, abstand = abstand, gui_sett = gui_sett, background="black", foreground="white")
        elements.checks.google_scholar.value = IntVar()
        elements.checks.google_scholar.config(variable=elements.checks.google_scholar.value, selectcolor="gray", activebackground="black",activeforeground="white")
        #elements.checks.google_scholar.select() # pre-checked
    except: pass
    try:    # option: Livio
        aline = 4
        sub_display_elements(element=elements.checks.livivo, aline=aline, column_start=0, column_end=1, rand = rand, subs_lines = study_reg_options_lines, abstand = abstand, gui_sett = gui_sett, background="black", foreground="white")
        elements.checks.livivo.value = IntVar()
        elements.checks.livivo.config(variable=elements.checks.livivo.value, selectcolor="gray", activebackground="black",activeforeground="white")
        #elements.checks.livivo.select() # pre-checked
    except: pass
    try:    # option: Trip Database
        aline = 5
        sub_display_elements(element=elements.checks.trip_db, aline=aline, column_start=0, column_end=1, rand = rand, subs_lines = study_reg_options_lines, abstand = abstand, gui_sett = gui_sett, background="black", foreground="white")
        elements.checks.trip_db.value = IntVar()
        elements.checks.trip_db.config(variable=elements.checks.trip_db.value, selectcolor="gray", activebackground="black",activeforeground="white")
        #elements.checks.trip_db.select() # pre-checked
    except: pass
    try:    # option: base-search.net
        aline = 6
        sub_display_elements(element=elements.checks.base_search, aline=aline, column_start=0, column_end=1, rand = rand, subs_lines = study_reg_options_lines, abstand = abstand, gui_sett = gui_sett, background="black", foreground="white")
        elements.checks.base_search.value = IntVar()
        elements.checks.base_search.config(variable=elements.checks.base_search.value, selectcolor="gray", activebackground="black",activeforeground="white")
        #elements.checks.base_search.select() # pre-checked
    except: pass
    try:    # option: UB Freiburg
        #aline = 7
        #sub_display_elements(element=elements.checks.ub_fr, aline=aline, column_start=0, column_end=1, rand = rand, subs_lines = study_reg_options_lines, abstand = abstand, gui_sett = gui_sett, background="black", foreground="white")
        elements.checks.ub_fr.value = IntVar()
        elements.checks.ub_fr.config(variable=elements.checks.ub_fr.value, selectcolor="gray", activebackground="black",activeforeground="white")
        #elements.checks.ub_fr.select() # pre-checked
    except: pass
    try:    # option: Web of Science
        aline = 7
        sub_display_elements(element=elements.checks.wos, aline=aline, column_start=0, column_end=1, rand = rand, subs_lines = study_reg_options_lines, abstand = abstand, gui_sett = gui_sett, background="black", foreground="white")
        elements.checks.wos.value = IntVar()
        elements.checks.wos.config(variable=elements.checks.wos.value, selectcolor="gray", activebackground="black",activeforeground="white")
        #elements.checks.wos.select() # pre-checked
    except: pass
    try:    # Apply button
        aline = 9
        sub_display_elements(element=elements.buttons.register_options_okay, aline=aline, column_start=.33, column_end=.66, rand = rand, subs_lines = study_reg_options_lines, abstand = abstand, gui_sett = gui_sett)
    except: pass

    ###################### guidelines options ##############################
    try:  # option: AWMF
        aline = 1
        sub_display_elements(element=elements.checks.awmf, aline=aline, column_start=0, column_end=1, rand=rand, subs_lines=guidelines_options_lines, abstand=abstand, gui_sett=gui_sett, background="black", foreground="white")
        elements.checks.awmf.config(selectcolor="gray", activebackground="black", activeforeground="white")
        elements.checks.awmf.value = IntVar()
        elements.checks.awmf.config(variable=elements.checks.awmf.value)
        elements.checks.awmf.select()  # pre-checked
    except: pass
    try:  # option: NICE
        aline = 2
        sub_display_elements(element=elements.checks.nice, aline=aline, column_start=0, column_end=1, rand=rand, subs_lines=guidelines_options_lines, abstand=abstand, gui_sett=gui_sett, background="black", foreground="white")
        elements.checks.nice.value = IntVar()
        elements.checks.nice.config(variable=elements.checks.nice.value, selectcolor="gray", activebackground="black", activeforeground="white")
        elements.checks.nice.select() # pre-checked
    except: pass
    try:  # option: Trip Database
        aline = 3
        sub_display_elements(element=elements.checks.tripdb, aline=aline, column_start=0, column_end=1, rand=rand, subs_lines=guidelines_options_lines, abstand=abstand, gui_sett=gui_sett, background="black", foreground="white")
        elements.checks.tripdb.value = IntVar()
        elements.checks.tripdb.config(variable=elements.checks.tripdb.value, selectcolor="gray", activebackground="black", activeforeground="white")
        elements.checks.tripdb.select() # pre-checked
    except: pass
    try:    # Apply button
        aline = 5
        sub_display_elements(element=elements.buttons.guidelines_options_okay, aline=aline, column_start=.33, column_end=.66, rand = rand, subs_lines = guidelines_options_lines, abstand = abstand, gui_sett = gui_sett)
    except: pass

    ###################### guidelines mode ##############################
    try:  # option: Study Register Numbers (StudReg)
        aline = 0.4
        sub_display_elements(element=elements.buttons.guidelines_studreg, aline=aline, column_start=0, column_end=1, rand=rand, subs_lines=guidelines_mode_lines, abstand=abstand, gui_sett=gui_sett)
    except: pass
    try:  # option: Study Register Numbers (StudReg)
        aline = 1.6
        sub_display_elements(element=elements.buttons.guidelines_doi, aline=aline, column_start=0, column_end=1, rand=rand, subs_lines=guidelines_mode_lines, abstand=abstand, gui_sett=gui_sett)
    except: pass

def main_display_elements(button, line, gui_sett, rand, abstand, main_lines, fontsize = 12):
    button.place(  x=rand, y=rand + ((gui_sett.height - rand) / main_lines) * line , width=gui_sett.width - rand * 2, height=((gui_sett.height - rand) / main_lines)- abstand)
    button.config(bg="white", fg="black", font=("helvetica", fontsize))

def sub_display_elements(element, aline, rand, subs_lines, abstand, gui_sett, column_start=0, column_end=1, font_size=9, background="white", foreground="black", align="center"):
    # aline [start, end]
    # column in percent

    from numbers import Number
    if isinstance(aline, Number) == True:
        aline         = [aline, aline]
    if column_start > 0:
        column_start  = column_start + (abstand / gui_sett.width)/4
    if column_end   < 1:
        column_end    = column_end   - (abstand / gui_sett.width)/4

    element.place(   x= rand + (gui_sett.width - rand*2)*column_start, y= rand + (gui_sett.height - rand * 2) / subs_lines * aline[0], width= (gui_sett.width - rand*2)*(column_end - column_start), height=(gui_sett.height - rand * 2) / subs_lines * (aline[1] - aline[0] + 1))
    element.config( bg= background, fg=foreground, font=("helvetica", font_size))
    try: element.config(anchor = align)   # anchor is alignment
    except: pass

def write_to_edit(edit, astring):
    edit.delete(0, len(edit.get()))
    edit.insert(0, astring)
    edit.update()

def write_to_label(label, astring):
    label.config(text=astring)
    label.update()

def feedback_both(elements, msg):
    print("\n" + msg)
    write_to_label(elements.labels.status, msg)

def write_to_textbox(edit, astring):
    edit.delete("1.0", "end")
    edit.insert("1.0", astring)
    edit.update()

def pre_write_to_textbox(elements, old_dois, new_dois):

    if len(new_dois) > 0:
        if len(old_dois) > 0:
            atext = old_dois[0]
            for i in range(1, len(old_dois)):
                atext = atext + '\n' + old_dois[i]
            atext = atext + '\n' + new_dois[0]
        else:
            atext = new_dois[0]

        for i in range(1, len(new_dois)):
            atext = atext + '\n' + new_dois[i]

        write_to_textbox(elements.edits.dois, atext)


########################################################
################## Actions #############################
########################################################

########################################################
################## Actions Main GUI ####################
########################################################

def gui_extract_bib_info(gui_old, keep=list()):
    save_gui_position(gui_old, keep)
    gui_old.destroy()
    gui     = create_gui("extract_bib_info", keep)

def gui_download_pdfs(gui_old, keep=list()):
    save_gui_position(gui_old, keep)
    gui_old.destroy()
    gui     = create_gui("pdf_download", keep)

def gui_study_registers_dois(gui_old, keep=list()):
    save_gui_position(gui_old, keep)
    gui_old.destroy()
    #gui     = create_gui("study_registers")
    gui = create_gui("register_options", keep)

def gui_cited_by(gui_old, keep=list()):
    save_gui_position(gui_old, keep)
    gui_old.destroy()
    gui     = create_gui("cited_by", keep)

def gui_guidelines(gui_old, keep=list()):
    save_gui_position(gui_old, keep)
    gui_old.destroy()
    gui     = create_gui("guidelines_mode", keep)
    #gui     = create_gui("guidelines_options", keep)

def gui_is_in_cochrane(gui_old, keep=list()):
    save_gui_position(gui_old, keep)
    gui_old.destroy()
    gui     = create_gui("is_in_cochrane", keep)

def gui_to_endnote(gui_old, keep=list()):
    save_gui_position(gui_old, keep)
    gui_action_to_endnote(gui_old)

def gui_action_back(gui_old, elements, keep=list()):
    save_gui_position(gui_old, keep)
    #elements.keeps.email    = elements.edits.email.get()
    gui_old.destroy()
    gui     = create_gui("main", keep)
    return elements

def gui_quit(gui_old, elements, keep=list()):
    gui_old.destroy()

########################################################
############# Action Extract Bib Info ##################
########################################################

def gui_action_extract_bib_info(elements):
    from definitions import preprocess_ids, create_timestamp, initialize_browser, initialize_http, remove_dublicates
    # save configs for next time
    save_config(elements)

    #if elements.checks.download.value.get() == 1:
    gecko_path      = check_geckodriver(elements)
    #else:
    #    gecko_path  = ""
    folders         = check_download_folder(elements)
    timestamp       = create_timestamp()

    http            = initialize_http()
    browser         = initialize_browser(gecko_path, folders)

    input           = elements.edits.dois.get("1.0", "end")
    input           = preprocess_ids(input, [chr(32), ":", '"', ";", ","])  # do not strip those away, because titles are included

    dois, failed, browser    = sub_action_extract_bib_info(elements, browser, http, input, folders, timestamp)

    # Download PDFs
    if (elements.checks.download.value.get() == 1):
        write_to_label(elements.labels.status, "Info: Downloading PDFs")

        dois = remove_dublicates(dois)
        try: dois.remove("")
        except: pass
        try: dois.remove(" ")
        except: pass
        try: dois.remove("DOI")
        except: pass

        sub_action_pdfs_download(elements, dois, folders, timestamp, browser, failed)

    try: browser.close()
    except: pass

    write_to_label(elements.labels.status, "Info: Finished")

def sub_action_extract_bib_info(elements, browser, http, input, folders, timestamp):
    from definitions import extract_bib_info
    from output_defs import write_output_extract_bib_info
    from mail_defs   import mail_extract_bib_info

    mode            = 1
    dois            = list()
    failed          = list()
    bib_info        = list()

    # perform bib extraction
    try:
        write_to_label(elements.labels.status, "Info: Extracting Bib. Information")
        bib_info, failed, dois, browser  = extract_bib_info(input, browser, http)
    except:
        mode        = 2  # bib extraction failed

    # writing output files
    if mode == 1:
        try:
            write_to_label(elements.labels.status, "Info: Writing Results to File")
            write_output_extract_bib_info(bib_info, failed, folders, timestamp)
        except:
            mode    = 3  # file writing failed

    # Sending Mail
    try:
        mail_add        = elements.edits.email.get()
        if mail_add != "":
            write_to_label(elements.labels.status, "Info: Sending Email")
            mail_extract_bib_info(mode, mail_add, bib_info, failed, folders, timestamp)
    except:
        feedback_both(elements, "Error during sending mail")

    return dois, failed, browser

########################################################
############## Action Download PDFs ####################
########################################################

def gui_action_pdfs_download(elements):
    from definitions import preprocess_ids, remove_dublicates, create_timestamp, titles_2_dois, initialize_browser, initialize_http
    # save configs for next time
    save_config(elements)

    gecko_path      = check_geckodriver(elements)
    folders         = check_download_folder(elements)
    timestamp       = create_timestamp()

    browser         = initialize_browser(gecko_path, folders)
    http            = initialize_http()

    # Read DOIs
    dois            = elements.edits.dois.get("1.0", "end")
    dois            = preprocess_ids(dois, [chr(32), ":", '"', ";", "(", ")", ","]) # do not strip those away, because titles are included

    #if elements.checks.extract_bib.value.get() == 1:
    #    weg, weg, dois  = sub_action_extract_bib_info(elements, dois, folders, timestamp)

    write_to_label(elements.labels.status, "Info: Looking up the DOIs for the titles")
    dois            = titles_2_dois(dois)
    dois            = remove_dublicates(dois)
    write_to_label(elements.labels.status, "Info: %d unique DOIs in total" % len(dois))

    browser         = sub_action_pdfs_download(elements, dois, folders, timestamp, browser)

    if elements.checks.extract_bib.value.get() == 1:
        write_to_label(elements.labels.status, "Info: Extracting Bib. Info")
        browser     = sub_action_extract_bib_info(elements, browser, http, dois, folders, timestamp)

    try: browser.close()
    except: pass

    feedback_both(elements, "Finished")

def sub_action_pdfs_download(elements, dois, folders, timestamp, browser, failed_dois=list()):
    from definitions import download_pdfs_from_dois
    from output_defs import write_output_download_pdfs
    from mail_defs   import mail_download_pdf

    # Perform
    mode            = 1
    try:
        missing_pdfs, browser    = download_pdfs_from_dois(dois, folders, browser)
    except:
        mode        = 2
        missing_pdfs= list()
        feedback_both(elements, "An Error occurred during the downloading of the PDFs")

    # Write Output
    try:
        write_to_label(elements.labels.status, "writing result files")
        write_output_download_pdfs(missing_pdfs, failed_dois, timestamp, folders)
    except:
        mode        = 3
        feedback_both(elements, "An Error occurred during the writing of the result files")

    # Mail Part
    mail_add        = elements.edits.email.get()
    if mail_add != "":
        try:
            mail_download_pdf(dois, missing_pdfs, timestamp, mail_add, folders, mode)
            write_to_label(elements.labels.status, "Finished")
        except:
            feedback_both(elements, "Something went wrong during sending the mail. The rest is fine")

    return browser

########################################################
############## Study Register Search ###################
########################################################

def gui_action_study_register(elements, keep):
    from mail_defs          import mail_study_register
    from register_search    import register_search_main
    from definitions        import initialize_http, initialize_browser, preprocess_ids, remove_dublicates, create_timestamp
    from output_defs        import write_output_register_search, write_study_register_results

    # save configs for next time
    save_config(elements)

    gecko_path      = check_geckodriver(elements)

    folders         = check_download_folder(elements)
    timestamp       = create_timestamp()

    study_ids       = preprocess_ids(elements.edits.dois.get("1.0", "end"))
    study_ids       = remove_dublicates(study_ids)
    write_to_label(elements.labels.status, "Info: %d unique IDs in total" % len(study_ids))

    # initializing webtools
    http            = initialize_http()
    browser         = initialize_browser(gecko_path, folders)   # start selenium

    mail_add        = elements.edits.email.get()

    # the search itself
    mode, results, header, no_results, failed_message, browser, stud_reg_res   \
                    = register_search_main(elements, study_ids, browser, http, mail_add, folders, timestamp, keep)

    # write outputs
    write_output_register_search(results, header, no_results, failed_message, folders, timestamp)
    if keep.study_reg == 1:
        write_study_register_results(stud_reg_res, folders, timestamp)


    feedback_both(elements, "Finished")

    dois            = remove_dublicates(results[1][1:len(results[1])])
    # remove empty "dois"
    try: dois.remove(' ')
    except: pass
    try: dois.remove('')
    except: pass

    # Mail Part
    if mail_add != "":
        try:
            mail_study_register(mail_add, study_ids, results[1][1:len(results[1])], sum(list(map(int,results[-1][1:len(results[-1])]))), no_results, failed_message, folders, timestamp, mode)
            write_to_label(elements.labels.status, "Finished")
        except:
            feedback_both(elements, "Something went wrong during sending the mail. The rest is fine")


    # Download PDFs
    if mode == 1:
        if (elements.checks.download.value.get() == 1):
            sub_action_pdfs_download(elements, dois, folders, timestamp, browser)

    # finalize webtools
    try: browser.close()
    except: pass



########################################################
######## Study Register Search - Options ###############
########################################################

def gui_open_gui_register_options(elements, gui_sett):
    from tkinter import mainloop
    sub_gui     = create_gui("register_options")
    #mainloop()

def change_background_value(element):
    element.value.set(abs(element.value.get() - 1))

def gui_register_options_apply(gui, elements):
    gui.destroy()
    keep                = create_keep
    keep.study_reg      = elements.checks.study_reg.value.get()
    keep.pubmed         = elements.checks.pubmed.value.get()
    keep.cochrane_lib   = elements.checks.cochrane_lib.value.get()
    keep.google_scholar = elements.checks.google_scholar.value.get()
    keep.livivo         = elements.checks.livivo.value.get()
    keep.trip_db        = elements.checks.trip_db.value.get()
    keep.base_search    = elements.checks.base_search.value.get()
    keep.ub_fr          = elements.checks.ub_fr.value.get()
    keep.wos            = elements.checks.wos.value.get()
    gui                 = create_gui("study_registers", keep)

########################################################
############## Action Cited By #########################
########################################################

def gui_action_cited_by(elements):
    from definitions          import initialize_http, initialize_browser, preprocess_ids, remove_dublicates, create_timestamp, extract_cited_by
    #from plugins_webofscience import extract_cited_by
    from output_defs          import write_output_cited_by
    from mail_defs            import mail_cited_by

    # save configs for next time
    save_config(elements)

    gecko_path              = check_geckodriver(elements)
    folders                 = check_download_folder(elements)
    timestamp               = create_timestamp()

    depth                   = int(elements.edits.depth.get())

    dois                    = preprocess_ids(elements.edits.dois.get("1.0", "end"))
    dois                    = remove_dublicates(dois)
    write_to_label(elements.labels.status, "Info: %d unique IDs in total" % len(dois))

    # initializing webtools
    http                    = initialize_http()
    browser                 = initialize_browser(gecko_path, folders)  # start selenium

    mail_add                = elements.edits.email.get()
    mode                    = 1

    #try:
        # perform search
    bib_info, header, browser \
                            = extract_cited_by(elements, browser, http, dois, 0, depth, max_results = 5000)

        # write output
    write_output_cited_by(bib_info, header, folders, timestamp)
    #except:
    #    mode                = 2

    try: browser.close()
    except: pass

    # Mail Part
    if mail_add != "":
        if mode == 1:
            mail_cited_by(mode, mail_add, timestamp, folders, dois, bib_info, depth)
        else:
            mail_cited_by(mode, mail_add, timestamp, folders, dois, list(), depth)

    # Download PDFs
    if mode == 1:
        if (elements.checks.download.value.get() == 1):
            dois            = bib_info[3]
            dois            = remove_dublicates(dois)
            # remove empty "dois"
            try: dois.remove(' ')
            except: pass
            try: dois.remove('')
            except: pass
            sub_action_pdfs_download(elements, dois, folders, timestamp, browser)


########################################################
######## Action Is in Cochrane Library  ################
########################################################

def gui_action_is_in_cochrane(elements):
    from definitions import initialize_browser, preprocess_ids, remove_dublicates, create_timestamp
    from plugin_cochrane_library import is_in_cochrane_library
    from output_defs import write_output_is_in_cochrane

    # save configs for next time
    save_config(elements)

    gecko_path      = check_geckodriver(elements)
    folders         = check_download_folder(elements)
    timestamp       = create_timestamp()

    dois            = preprocess_ids(elements.edits.dois.get("1.0", "end"))
    dois            = remove_dublicates(dois)
    write_to_label(elements.labels.status, "Info: %d unique IDs in total" % len(dois))

    # initializing webtools
    browser         = initialize_browser(gecko_path, folders)  # start selenium

    results         = is_in_cochrane_library(browser, dois, timestamp)

    try: browser.close()
    except: pass

    header          = ["DOI", "Cochrane"]

    write_output_is_in_cochrane(results, header, folders, timestamp)

########################################################
################### Guidelines #########################
########################################################

def gui_action_guidelines(elements, keep):
    from definitions import create_timestamp, read_info_doi_scout_file, initialize_http, initialize_browser, search_citations_in_guidelines, search_study_reg_ids_in_guidelines, only_first_author, preprocess_ids
    from output_defs import write_output_guideline

    # save configs for next time
    save_config(elements)

    timestamp       = create_timestamp()

    if elements.checks.extract_bib.value.get() == 0:
        keep.extract_bib  = 0
    else:
        keep.extract_bib  = 1

    http            = initialize_http()

    gecko_path      = check_geckodriver(elements)
    folders         = check_download_folder(elements)
    browser         = initialize_browser(gecko_path, folders)

    if keep.guide_mode == "studreg":
        stud_ids    = elements.edits.dois.get("1.0", "end")
        stud_ids    = preprocess_ids(stud_ids, ["-"])

        result, browser = search_study_reg_ids_in_guidelines(stud_ids, http, browser, keep)

    elif keep.guide_mode == "doi":
        try: # ifkeep.afile == 1:     # read if there is a file or other information
            afile   = elements.edits.dois.get("1.0", "end").replace("\n","")
            idxs    = ["DOI", "Title", "Author"]
            data, header    = read_info_doi_scout_file(afile, idxs)
        except:
            print("ERROR. DoiScout File not found or malformed.")
            return

        data[2]     = only_first_author(data[2])

        result, browser = search_citations_in_guidelines(data, http, browser, keep)


    try: browser.close()
    except: pass

    write_output_guideline(result, folders, timestamp, keep)

    print("Finished")

########################################################
############### Guidelines - Options ###################
########################################################

def gui_open_gui_guidelines(elements, gui_sett):
    from tkinter import mainloop
    sub_gui     = create_gui("guidelines_options")
    #mainloop()

def gui_guidelines_options_apply(gui, elements):
    gui.destroy()
    keep                = create_keep
    keep.awmf           = elements.checks.awmf.value.get()
    keep.nice           = elements.checks.nice.value.get()
    keep.tripdb         = elements.checks.tripdb.value.get()
    gui                 = create_gui("guidelines", keep)

########################################################
################# Guidelines - Mode ####################
########################################################

def gui_guidelines_mode_studreg(gui, elements):
    gui.destroy()
    keep                = create_keep
    keep.guide_mode     = "studreg"
    gui                 = create_gui("guidelines_options", keep)

def gui_guidelines_mode_doi(gui, elements):
    gui.destroy()
    keep                = create_keep
    keep.guide_mode     = "doi"
    gui                 = create_gui("guidelines_options", keep)

########################################################
################### to endnote #########################
########################################################
def gui_action_to_endnote(elements):
    from definitions import transform_to_endnote
    from tkinter.filedialog import askopenfilename
    import os

    ## open file without errors
    import sys
    hold = sys.stderr
    class DevNull:
        def write(self, msg):   pass
    sys.stderr = DevNull()
    afile      = askopenfilename(title="Select the Exported Bib Info File", filetypes=[("Excel files", ".xlsx .xls")])
    sys.stderr = hold


    apath = os.path.dirname(afile); apath = apath + afile[len(apath)]
    afile = afile[len(apath) : len(afile)]

    transform_to_endnote(afile, apath)

########################################################
########### Performance sub processes ##################
########################################################

def check_download_folder(elements):
    from definitions import folder_structure
    #from os.path import sep
    download_folder     = elements.edits.resultdir.get()
    if download_folder == "":
        from tkinter.filedialog import askdirectory
        ## open file without errors
        import sys
        hold = sys.stderr
        class DevNull:
            def write(self, msg):   pass
        sys.stderr      = DevNull()
        download_folder = askdirectory(parent=None, title="Select a Result Folder")
        sys.stderr      = hold

    #if download_folder[len(download_folder) - 1] != '/':
    #    download_folder = download_folder + "/"
    write_to_edit(elements.edits.resultdir, download_folder)
    folders             = folder_structure(download_folder, "/") #"sep)
    return folders

def check_geckodriver(elements):
    # Geckodriver
    import os
    import platform
    there   = False
    if (platform.system() == "Linux") | (platform.system() == "Darwin"):
        if os.path.exists(os.path.join(os.getcwd(), "geckodriver")) == True:
            gecko_path  = os.path.join(os.getcwd(), "geckodriver")
            there       = True
    if platform.system() == "Windows":
        if os.path.exists(os.path.join(os.getcwd(), "geckodriver.exe")) == True:
            gecko_path = os.path.join(os.getcwd(), "geckodriver.exe")
            there      = True

    if there == False:
        from tkinter.filedialog import askopenfilename
        ## open file without errors
        import sys
        hold = sys.stderr
        class DevNull:
            def write(self, msg):   pass
        sys.stderr = DevNull()
        gecko_path  = askopenfilename(parent=None, title="Select geckodriver")
        sys.stderr = hold

    return gecko_path

########################################################
############# Actions sub processes ####################
########################################################
def gui_action_help():
    import webbrowser
    import os
    # opens pdf
    try:
        webbrowser.open_new(os.getcwd() + "/manual.pdf")
    except: pass

def gui_action_resultdir(elements):
    from tkinter.filedialog import askdirectory

    ## open file without errors
    import sys
    hold = sys.stderr
    class DevNull:
        def write(self, msg):   pass
    sys.stderr = DevNull()
    adir       = askdirectory(title="Choose Result Directory", initialdir = elements.edits.resultdir.get())
    sys.stderr = hold


    elements.edits.resultdir.delete(0, len(elements.edits.resultdir.get()))
    elements.edits.resultdir.insert(0, adir)

def gui_action_read_raw(elements):
    from tkinter.filedialog import askopenfilenames
    from definitions   import preprocess_ids

    ## open file without errors
    import sys
    hold            = sys.stderr
    class DevNull:
        def write(self, msg):   pass
    sys.stderr      = DevNull()
    afiles          = askopenfilenames(parent=None, title="Choose Txt/Raw-File", filetypes=[("Text-File",".txt .csv"),("all files","*.*")], initialdir = elements.edits.resultdir.get())
    sys.stderr      = hold

    new_ids         = list()
    for i in range(0, len(afiles)):
        file_obj    = open(afiles[i],'r')
        atext       = file_obj.read()
        file_obj.close()

        new_ids     = new_ids + preprocess_ids(atext)

    old_ids         = preprocess_ids(elements.edits.dois.get("1.0","end"))

    write_to_label(elements.labels.status, "Info: %d IDs detected | %d IDs in total" % (len(new_ids), len(old_ids) + len(new_ids)))

    pre_write_to_textbox(elements, old_ids, new_ids)

def gui_action_read_wos(elements):
    from tkinter.filedialog import askopenfilenames
    from definitions import preprocess_ids, read_dois_from_wos_search

    ## open file without errors
    import sys
    hold            = sys.stderr
    class DevNull:
        def write(self, msg):   pass
    sys.stderr      = DevNull()
    afiles          = askopenfilenames(parent=None, title="Choose Txt/Raw-File", filetypes=[("Text-File", ".txt .html"), ("all files", "*.*")], initialdir = elements.edits.resultdir.get())
    sys.stderr      = hold

    new_dois        = list()
    for i in range(0, len(afiles)):
        file_obj    = open(afiles[i], 'r')
        atext       = file_obj.read()
        file_obj.close()

        new_dois    = new_dois + read_dois_from_wos_search(atext)

    old_dois        = preprocess_ids(elements.edits.dois.get("1.0","end"))

    write_to_label(elements.labels.status, "Info: %d IDs detected | %d IDs in total" % (len(new_dois), len(old_dois) + len(new_dois)))

    pre_write_to_textbox(elements, old_dois, new_dois)

def gui_action_read_ncbi(elements):
    from tkinter.filedialog import askopenfilenames
    from definitions import preprocess_ids, read_dois_from_ncbi_search

    ## open file without errors
    import sys
    hold            = sys.stderr
    class DevNull:
        def write(self, msg):   pass
    sys.stderr      = DevNull()
    afiles          = askopenfilenames(parent=None, title="Choose Pubmed-File", filetypes=[("csv-File", ".csv"), ("all files", "*.*")], initialdir = elements.edits.resultdir.get())
    sys.stderr      = hold

    new_dois        = list()
    for i in range(0, len(afiles)):
        file_obj    = open(afiles[i], 'r')
        atext       = file_obj.read()
        file_obj.close()

        new_dois    = new_dois + read_dois_from_ncbi_search(atext)

    old_dois        = preprocess_ids(elements.edits.dois.get("1.0", "end"))

    write_to_label(elements.labels.status, "Info: %d IDs detected | %d IDs in total" % (len(new_dois), len(old_dois) + len(new_dois)))

    pre_write_to_textbox(elements, old_dois, new_dois)

def gui_action_read_doi_scout(elements, keep):
    from tkinter.filedialog import askopenfilename

    ## open file without errors
    import sys
    hold       = sys.stderr
    class DevNull:
        def write(self, msg):   pass
    sys.stderr = DevNull()
    afiles     = askopenfilename(parent=None, title="Choose Doi-Scout-Result-File", filetypes=[("xlsx-File", ".xlsx .xls"), ("all files", "*.*")], initialdir = elements.edits.resultdir.get())
    sys.stderr = hold


    write_to_label(elements.labels.status,"DS-file is processed in next step")

    pre_write_to_textbox(elements, [], [afiles])

    keep.afile  = 1

########################################################
################## Auto result dir #####################
########################################################

def fill_result_dir(elements):
    from os import path
    configfile    = "stan.cfg"
    apath         = path.dirname(path.realpath(__file__))
    if path.exists(path.join(apath, configfile)):
        f = open(path.join(apath, configfile), "r")
        resultdir = f.readline()
        resultdir = resultdir[0:(len(resultdir)-1)]
        mail      = f.readline()
        f.close()
    else:
        resultdir = ""
        mail      = ""
    elements.keeps.configfile = path.join(apath, configfile)
    elements.edits.resultdir.insert(0, resultdir)
    elements.edits.email.insert(0, mail)

def save_config(elements):
    try:
        f = open(elements.keeps.configfile, "w")
        f.write(elements.edits.resultdir.get())
        f.write("\n")
        f.write(elements.edits.email.get())
        f.close()
    except:
        pass

########################################################
################# Keep gui position ####################
########################################################

def save_gui_position(gui, keep):
    keep.xpos       = gui.winfo_x()
    keep.ypos       = gui.winfo_y()

def draw_gui(gui, gui_sett, keep, type="main"):
    if type == "main":
        try:
            keep.xpos
            keep.ypos
            gui.geometry("%1.0fx%1.0f+%1.0f+%1.0f" % (gui_sett.width, gui_sett.height, keep.xpos, keep.ypos))
        except:
            gui.geometry("%1.0fx%1.0f+%1.0f+%1.0f" % (gui_sett.width, gui_sett.height, gui_sett.xpos, gui_sett.ypos))

    elif type == "options_reg":
        try:
            keep.xpos
            keep.ypos
            gui.geometry("%1.0fx%1.0f+%1.0f+%1.0f" % (gui_sett.subregwidth, gui_sett.subregheight, keep.xpos, keep.ypos))
        except:
            gui.geometry("%1.0fx%1.0f+%1.0f+%1.0f" % (gui_sett.subregwidth, gui_sett.subregheight, gui_sett.subregxpos, gui_sett.subregypos))

    elif type == "options_guidelines":
        try:
            keep.xpos
            keep.ypos
            gui.geometry("%1.0fx%1.0f+%1.0f+%1.0f" % (gui_sett.subguidewidth, gui_sett.subguideheight, keep.xpos, keep.ypos))
        except:
            gui.geometry("%1.0fx%1.0f+%1.0f+%1.0f" % (gui_sett.subguidewidth, gui_sett.subguideheight, gui_sett.subguidexpos, gui_sett.subguideypos))

    elif type == "mode_guidelines":
        try:
            keep.xpos
            keep.ypos
            gui.geometry("%1.0fx%1.0f+%1.0f+%1.0f" % (gui_sett.subguidewidth, gui_sett.subguideheight, keep.xpos, keep.ypos))
        except:
            gui.geometry("%1.0fx%1.0f+%1.0f+%1.0f" % (gui_sett.subguidewidth, gui_sett.subguideheight, gui_sett.subguidexpos, gui_sett.subguideypos))



########################################################
################## Classes #############################
########################################################

class gui_data:
    def __init__(self, gui):
        self.width          = 600
        self.height         = 720
        self.xpos           = gui.winfo_screenwidth()  / 2 - self.width  / 2
        self.ypos           = gui.winfo_screenheight() / 2 - self.height / 2
        self.subregwidth    = 400
        self.subregheight   = 400
        self.subregxpos     = gui.winfo_screenwidth()  / 2 - self.subregwidth  / 2
        self.subregypos     = gui.winfo_screenheight() / 2 - self.subregheight / 2
        self.subguidewidth  = 400
        self.subguideheight = 220
        self.subguidexpos   = gui.winfo_screenwidth() / 2 - self.subguidewidth / 2
        self.subguideypos   = gui.winfo_screenheight() / 2 - self.subguideheight / 2

class initialize_elements:
    def __init__(self):
        self.buttons                = initialize_buttons()
        self.edits                  = initialize_edits()
        self.checks                 = initialize_checks()
        self.labels                 = initialize_labels()
        self.keeps                  = initialize_keeps()

class initialize_buttons:
    def __init__(self):
        self.extract_bib_info       = list()
        self.pdf_download           = list()
        self.study_registers        = list()
        self.cited_by               = list()
        self.guidelines             = list()
        self.is_in_cochrane         = list()
        self.quit                   = list()
        self.manual                 = list()
        self.back                   = list()
        self.run                    = list()
        self.read_raw               = list()
        self.read_wos               = list()
        self.read_ncbi              = list()
        self.help                   = list()
        self.resultdir              = list()
        self.register_options       = list()
        self.register_options_okay  = list()
        self.guidelines             = list()
        self.guidelines_options_okay= list()
        self.read_doi_scout         = list()
        self.guidelines_studreg     = list()
        self.guidelines_doi         = list()

class initialize_edits:
    def __init__(self):
        self.email                  = list()
        self.depth                  = list()
        self.dois                   = list()
        self.resultdir              = list()

class initialize_checks:
    def __init__(self):
        self.download               = list()
        self.study_res              = list()
        self.extract_bib            = list()
        ## sub gui study registers
        self.study_reg              = list()
        self.pubmed                 = list()
        self.cochrane_lib           = list()
        self.google_scholar         = list()
        self.livovo                 = list()
        self.trip_db                = list()
        self.base_search            = list()
        self.ub_fr                  = list()
        self.wos                    = list()
        ## sub gui guidelines
        self.awmf                   = list()
        self.nice                   = list()
        self.trip_db                = list()

class initialize_labels:
    def __init__(self):
        self.title                  = list()
        self.status                 = list()
        self.email                  = list()
        self.dois                   = list()
        self.depth                  = list()

class initialize_keeps:
    def __init__(self):
        self.email                  = ""

class create_keep:
    def __init__(self):
        self.study_reg              = 1
        self.pubmed                 = 1
        self.cochrane_lib           = 1
        self.google_scholar         = 1
        self.livivo                 = 1
        self.trip_db                = 1
        self.base_search            = 1
        self.ub_fr                  = 1
        self.wos                    = 1
        self.awmf                   = 1
        self.nice                   = 1
        self.tripdb                 = 1
        self.afile                  = 0
        self.extract_bib            = 0
        self.configfile             = ""
        self.guide_mode             = ""