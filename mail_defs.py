##################################################################
def send_mail(mail_add, subject, text):
    # mode 1: finished # mode 2: Error
    import os
    path        = os.getcwd()
    command     = path + "/sending_mail " + ' ' + mail_add + ' "Subject:' + subject + '" "' + text + '"'
    weg         = os.system(command)  # weg remains, so

##################################################################
def mail_extract_bib_info(mode, mail_add, bib_info, failed, folders, timestamp):
    text        = "+++++++++++++++++++++++++++++++++++++++++\n\r"
    text        = text + "Result Folder: %s\n\r" % folders.main

    if mode == 1:
        subject = "SUCCESS: " + timestamp + " - Extracting Bib. Info"
        text    = sub_mail_extract_bib_info(text, bib_info, failed)
    else:
        subject = "FAILURE: " + timestamp + " - Extracting Bib. Info"

    send_mail(mail_add, subject, text)

def sub_mail_extract_bib_info(text, bib_info, failed):
    text        = text + "+++++++++++++++++++++++++++++++++++++++++\n\r"
    text        = text + "For %d of %d Bib. info successfully extracted\n\r" % (len(bib_info[0]) - len(failed) - 1, len(bib_info[0]) - 1)
    if len(failed) > 0:
        text    = text + "+++++++++++++++++++++++++++++++++++++++++\n\r"
        text    = text + "+ No Bib info found for:\n\r"
        for i in range(0, len(failed)):
            text= text + "%s\n\r" % failed[i]
        text    = text + "+++++++++++++++++++++++++++++++++++++++++\n\r"
    return text

##################################################################
def mail_download_pdf(dois, missing_dois, timestamp, mail_add, folders, mode):

    text        =       "+++++++++++++++++++++++++++++++++++++++++\n\r"
    text        =     text + "Result Folder: %s\n\r" % folders.main

    if mode == 1:
        subject = "SUCCESS: " + timestamp + " - Downloading PDFs"
        text    = sub_mail_download_pdf(text, dois, missing_dois)
    else:
        subject = "FAILURE: " + timestamp + " - Downloading PDFs"

    send_mail(mail_add, subject, text)

def sub_mail_download_pdf(text, dois, missing_dois):
    text        = text + "+++++++++++++++++++++++++++++++++++++++++\n\r"
    text        = text + "%d of %d successfully downloaded\n\r" % (len(dois) - len(missing_dois), len(dois))
    if len(missing_dois) > 0:
        text    = text + "+++++++++++++++++++++++++++++++++++++++++\n\r"
        text    = text + "+ No PDFs were downloaded for:\n\r"
        for i in range(0, len(missing_dois)):
            text= text + "%s\n\r" % missing_dois[i]
    text        = text + "+++++++++++++++++++++++++++++++++++++++++\n\r"
    return text

##################################################################
def mail_study_register(mail_add, study_ids, dois, attention, no_results, failed_message, folders, timestamp, mode):

    text        =        "+++++++++++++++++++++++++++++++++++++++++\n\r"
    text        = text + "Result Folder: %s\n\r" % folders.main

    if mode == 1:
        subject = "SUCCESS: " + timestamp + " - Searching Study Registers"
        text    = sub_mail_study_registers(text, study_ids, dois, attention, no_results, failed_message)
    else:
        subject = "FAILURE: " + timestamp + " - Searching Study Registers"

    send_mail(mail_add, subject, text)

def sub_mail_study_registers(text, study_ids, dois, attention, no_results, failed_message):
    text            = text + "+++++++++++++++++++++++++++++++++++++++++\n\r"
    text            = text + "Total number of IDs: %6d\n\r" % len(study_ids)
    text            = text + "Total number of identified resources: %6d\n\r" % len(dois)
    text            = text + "Number of resources that require further attention: %6d\n\r" % attention
    text            = text + "Number of errors occured during searches that require manual search: %6d\n\r" % len(failed_message[1])
    text            = text + "Number of searches that did not yield any result: %6d\n\r" % len(no_results)
    #text        = text + "Total number of DOIs not recognized: %6d\n\r" % len(failed_dois)
    #text        = text + "Total number of studies without any reference: %6d\n\r" % len(no_dois)
    #text        = text + "Total number of studies that were not recognized: %6d\n\r" % len(total_fails)

    if len(failed_message[0]) > 0:
        text        = text + "+++++++++++++++++++++++++++++++++++++++++\n\r"
        text        = text + "+ The following searches ended in errors:\n\r"
        for i in range(0, len(failed_message[0])):
            text    = text + "%s" % failed_message[0][i]
            for n in range(0, 20-len(failed_message[0][i])):
                text= text + " "
            text    = text + "%s\n\r" % failed_message[1][i]

    if len(no_results) > 0:
        text    = text + "+++++++++++++++++++++++++++++++++++++++++\n\r"
        text    = text + "+ No resources at all were found for:\n\r"
        for i in range(0, len(no_results)):
            text= text + "%s\n\r" % no_results[i]

    return text

##################################################################
def mail_captcha(mail_add, timestamp):
    text        =        "+++++++++++++++++++++++++++++++++++++++++\n\r"
    text        = text + "ATTENTION: The doi scout needs your attention\n\r"
    text        = text + "There is a Captcha you need to solve\n\r"
    text        = text + "Process is stopped until Captcha is solved\n\r"
    text        = text + "Switch to the browser and solve it please\n\r"
    subject     = "ATTENTION: " + timestamp + " - Action needed (captcha)"

    try:
        if mail_add != "":
            send_mail(mail_add, subject, text)
    except: pass


##################################################################
def mail_cited_by(mode, mail_add, timestamp, folders, dois, bib_info, max_depth):
    text                    =          "+++++++++++++++++++++++++++++++++++++++++\n\r"
    text                    = text +   "Result Folder: %s\n\r" % folders.main

    if mode == 1:
        subject             = "SUCCESS: " + timestamp + " - Cited By"
        text                = text +   "+++++++++++++++++++++++++++++++++++++++++\n\r"
        text                = text +   "Total number of IDs: %6d\n\r" % len(dois)
        for i in range(1, max_depth+1):
            runner          = 0
            start           = 0
            try:
                while bib_info[2].index(str(i), start):
                    start   = bib_info[2].index(str(i), start) + 1
                    runner  = runner + 1
            except: pass
            text            = text +   "Number of Results in Depth %d: %6d\n\r" %(i, runner)

    else:
        subject             = "FAILURE: " + timestamp + " - Cited By"

    send_mail(mail_add, subject, text)