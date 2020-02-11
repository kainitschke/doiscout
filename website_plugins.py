def open_pdf_url(browser, http, doi, folder):
    from time import sleep
    from definitions import looping, open_page
    loop_cont       = ["linkinghub.elsevier.com"]
    while looping(browser.current_url, loop_cont): sleep(.05)   # looping to wait for final page
    url             = browser.current_url
    toclick         = True

    ########### ScienceDirect / Elsevier

    if   url.find("sciencedirect") > -1:
        site        = http.request('GET', url)
        start       = site.data.decode("utf-8").find("https://www.sciencedirect.com/science/article/pii")
        end         = site.data.decode("utf-8").find(".pdf", start) + len(".pdf")
        if site.data.decode("utf-8")[start:end].find("\n") == -1:
            sublink     = site.data.decode("utf-8")[start:end]
            sublink     = sublink.replace("amp;", "")                             # aus welchem Grund auch immer ausschneiden
            browser     = open_page(browser, sublink)
        else:
            return False

    ########### Wiley
    elif url.find("wiley.com") > -1:
        mainlink    = "http://onlinelibrary.wiley.com/doi/"
        #sublink     = mainlink + doi + "/pdf"
        sublink     = mainlink + "pdf/" + doi
        browser     = open_page(browser, sublink)
        browser.switch_to_frame(browser.find_element_by_xpath("/html/body/iframe[1]"))
        sleep(.8)
        #browser.switch_to_frame(browser.find_element_by_id("pdfDocument"))

    ########### Springer
    elif url.find("link.springer") > -1:
        mainlink    = "https://link.springer.com/content/pdf/"
        sublink     = mainlink + doi + ".pdf"
        # browser     = open_page(browser, sublink)
        f = open(folder.tmp + "tmp.pdf", "wb")
        f.write(http.request("GET", sublink).data)
        f.close()
        toclick = False
        sleep(.05)

    elif url.find("springeropen.com") > -1:
        id          = browser.find_element_by_id("articlePdf")
        id.click()
        sleep(.5)
        windows     = browser.window_handles
        browser.switch_to_window(windows[1])
        sublink     = browser.current_url
        browser.close()
        browser.switch_to_window(windows[0])
        browser     = open_page(browser, sublink)

    ########### ieeexplore
    elif url.find("ieeexplore.ieee.org") > -1:
        start       = url.find('document/') + len('document/')
        end         = url.find("/", start + 1)
        id          = url[start:end]
        sublink     = 'http://ieeexplore.ieee.org/stamp/stamp.jsp?arnumber=' + id
        # get into iframe to download PDF
        browser     = open_page(browser, sublink)
        sleep(.2)
        browser.switch_to_frame(browser.find_element_by_xpath("/html/body/iframe[2]"))

    ########### New England Journal of Medicine
    elif url.find("nejm.org") > -1:
        sublink     = "http://www.nejm.org/doi/pdf/" + doi
        browser     = open_page(browser, sublink, n_runner=1)

    ########### Haematologica
    elif url.find("haematologica.org") > -1:
        mainlink    = "http://www.haematologica.org/sites/all/libraries/pdfjs/web/viewer.html?file=/"
        start       = url.find("content")
        end         = len(url)
        sublink     = mainlink + url[start:end] + ".full.pdf"
        browser     = open_page(browser, sublink, n_runner=1)

    ########### Jama Network
    elif url.find("jamanetwork.com") > -1:
        mainlink    = "https://jamanetwork.com"
        site        = http.request('GET', url)
        start       = site.data.decode("utf-8").find("pdfaccess")
        start       = site.data.decode("utf-8").find("url", start)
        start       = site.data.decode("utf-8").find('"', start) + 1
        end         = site.data.decode("utf-8").find('"', start + 1)
        sublink     = mainlink + site.data.decode("utf-8")[start : end]
        f           = open(folder.tmp + "tmp.pdf", "wb")
        f.write(http.request("GET", sublink).data)
        f.close()
        toclick     = False
        sleep(.05)

    elif url.find("nature.com") > -1:
        sublink     = url + ".pdf"
        browser     = open_page(browser, sublink, n_runner=1)

    ########### BMJ Journals
    elif url.find("bmj.com") > -1:
        end         = url.find(".com/") + len(".com/")
        mainlink    = url[0:end]
        start       = url.find('content/')
        end         = len(url)
        sublink     = mainlink + url[start:end] + ".full.pdf"
        browser     = open_page(browser, sublink, n_runner=1)

    elif url.find("bloodjournal") > -1:
        mainlink    = "http://www.bloodjournal.org/"
        start       = url.find('content/')
        end         = url.find('?',start)
        if end == -1: end = len(url)
        sublink     = mainlink + url[start:end] + ".full.pdf"
        browser     = open_page(browser, sublink, n_runner=1)

    elif url.find("academic.oup.com") > -1:
        mainlink    = "https://academic.oup.com/"
        site        = http.request('GET', url)
        start       = site.data.decode("utf-8").find("pdfLink")
        start       = site.data.decode("utf-8").find('href="',start) + len('href="')
        end         = site.data.decode("utf-8").find('"', start + 1)
        sublink     = mainlink + site.data.decode("utf-8")[start:end]
        browser     = open_page(browser, sublink)
        sleep(2)

    elif url.find("http://ascopubs.org") > -1:
        mainlink    = "http://ascopubs.org/doi/pdfdirect/"
        start       = url.find('10')
        end         = len(url)
        sublink     = mainlink + url[start:end]
        browser     = open_page(browser, sublink, n_runner=1)

    elif url.find("biomedcentral.com") > -1:
        mainlink    = "https://bmcpsychiatry.biomedcentral.com/track/pdf/"
        sublink     = mainlink + doi
        browser     = open_page(browser, sublink, n_runner=1)

    elif url.find("annals.org") > -1:
        browser.find_element_by_id("pdfLink").click()
        toclick     = False
        sleep(.08)

    elif url.find("ovid.com") > -1:
        try:
            browser.find_element_by_id("pdf").click()
            sleep(6)
            id      = browser.find_element_by_xpath("/html/body/div[3]/div[1]/iframe[1]")
            browser.switch_to_frame(id)
        except:
            try:
                browser.find_element_by_css_selector("a.render-form:nth-child(2)").click()
                sleep(1)
                browser.switch_to_frame(browser.find_element_by_xpath("/html/body/div[3]/div[1]/iframe[1]"))
            except:
                try:
                    sleep(4)
                    browser.find_element_by_css_selector('.btn-top-viewonovid').click()
                    sleep(4)
                    open_pdf_url(browser, http, doi, folder)
                except:
                    return -3

    elif url.find("sagepub.com") > -1:
        #id          = browser.find_element_by_css_selector('td.PDFTool > a:nth-child(1)')
        #sublink     = id.get_attribute("href")
        sublink     = url.replace("/doi/", "/doi/pdf/")
        browser     = open_page(browser, sublink, n_runner=1)
        toclick     = False
        sleep(.05)

    elif url.find("stroke") > -1:
        id          = browser.find_element_by_css_selector(".highwire-citation-pdf-download-link > span:nth-child(2)")
        id.click()
        toclick     = False
        sleep(.5)

    elif url.find("apa.org") > -1:
        sleep(1)
        sublink     = url.replace(".html", ".pdf")
        browser     = open_page(browser, sublink, n_runner=1)
        try: browser.switch_to_frame(browser.find_element_by_xpath("/html/body/iframe[1]"))
        except: pass
        sleep(1)

    elif url.find("tandfonline.com") > -1:
        mainlink    = "http://www.tandfonline.com/doi/pdf/"
        sublink     = mainlink + doi
        browser     = open_page(browser, sublink, n_runner=1)

    elif url.find("ebscohost.com") > -1:
        sleep(2)
        browser.find_element_by_id("pdfft1").click()
        sleep(3.5)
        site        = http.request("GET", browser.current_url)
        start       = site.data.decode("utf-8").find("http://content.ebscohost")
        end         = site.data.decode("utf-8").find('"', start)
        sublink     = site.data.decode("utf-8")[start:end]
        sublink     = sublink.replace("amp;","")
        browser     = open_page(browser, sublink)
        sleep(.5)

    elif url.find("tidsskriftet.no") > -1:
        browser.find_element_by_css_selector('div.custom-button-wrapper:nth-child(2) > a:nth-child(1)').click()
        toclick     = False

    elif url.find("hindawi.com") > -1:
        id          = browser.find_element_by_css_selector('.full_text_pdf')
        new_url     = id.get_attribute("href")
        site        = http.request("GET", new_url)
        f           = open(folder.tmp + "tmp.pdf", 'wb')
        f.write(site.data)
        f.close()
        sleep(.2)
        toclick     = False

    elif url.find("http://www.psychiatrist.com") > -1:
        id          = browser.find_element_by_css_selector('p.link:nth-child(1) > a:nth-child(2)')
        sublink     = id.get_attribute("href")
        browser     = open_page(browser, sublink, n_runner=1)

    elif url.find("scielo") > -1:
        browser.find_element_by_css_selector("div.box:nth-child(5) > ul:nth-child(1) > li:nth-child(2) > a:nth-child(1)").click()

    ########### multiple sources; choose OVID; call self
    elif url.find("wkhealth.com") > -1:
        ## search and open ovid
        site        = http.request("GET", url)
        left        = site.data.decode("utf-8").find("site-left")
        right       = site.data.decode("utf-8").find("site-right")
        ovid        = site.data.decode("utf-8").find("ovid", left)
        if site.data.decode("utf-8").find("Ovid", left) < ovid: ovid    = site.data.decode("utf-8").find("Ovid", left)

        if ovid < right:
            browser.find_element_by_css_selector("#site-left > a:nth-child(1) > img:nth-child(1)").click()
        else:
            browser.find_element_by_css_selector("#site-right > a:nth-child(3) > img:nth-child(1)").click()
        sleep(15)
        ## call self recursively
        toclick     = open_pdf_url(browser, http, doi, folder)
        return toclick

    elif url.find("jopdentonline.org") > -1:
        id = browser.find_element_by_css_selector('#articleToolsFormats > li:nth-child(2) > a:nth-child(1)')
        sublink = id.get_attribute("href")
        browser     = open_page(browser, sublink, n_runner=1)

    elif url.find("arvojournals.org") > -1:
        browser.find_element_by_css_selector('#pdfLink').click()
        sleep(.4)
        toclick     = False

    elif url.find("aappublications.org") > -1:
        id          = browser.find_element_by_xpath('/html/body/div[3]/div[2]/div[2]/div/section[2]/div/div/div/div/div/div/div/div[2]/div[1]/div/div/div[1]/div/div/div[2]/div/div/div/div[1]/div/a')
        sublink     = id.get_attribute("href")
        browser     = open_page(browser, sublink, n_runner=1)

    elif url.find("ersjournals.com") > -1:
        id          = browser.find_element_by_css_selector('.tabs > li:nth-child(4) > a:nth-child(1)')
        sublink     = id.get_attribute("href")
        browser     = open_page(browser, sublink, n_runner=1)

    elif url.find("ahajournals.org") > -1:
        sleep(2)
        browser.find_element_by_css_selector('.highwire-citation-pdf-download-link').click()
        toclick = False

    elif url.find("psychiatryonline.org") > -1:
        mainlink    = "https://ajp.psychiatryonline.org/doi/pdf/"
        sublink     = mainlink + doi
        browser     = open_page(browser, sublink, n_runner=1)

    elif url.find("atsjournals.org") > -1:
        mainlink    = "http://www.atsjournals.org/doi/pdf/"
        sublink     = mainlink + doi
        browser     = open_page(browser, sublink, n_runner=1)

    elif url.find("diabetesjournals.org") > -1:
        try:
            sublink     = url + ".full.pdf"
            browser     = open_page(browser, sublink, n_runner=1)
        except:
            id          = browser.find_element_by_css_selector('.tabs > li:nth-child(4) > a:nth-child(1)')
            sublink     = id.get_attribute("href")
            browser     = open_page(browser, sublink, n_runner=1)

    #elif url.find("plos.org") > -1:

    elif url.find("degruyter.com") > -1:
        id          = browser.find_element_by_css_selector('.pdf-link')
        sublink     = id.get_attribute("href")
        browser     = open_page(browser, sublink, n_runner=1)

    elif url.find("frontiersin") > -1:
        sublink     = "https://www.frontiersin.org/articles/" + doi + "/pdf"
        f           = open(folder.tmp + "tmp.pdf", 'wb')
        f.write(http.request("GET", sublink).data)
        f.close()
        toclick     = False

    elif url.find("pagepressjournals.org") > -1:
        for i in range(1, 30):
            browser.execute_script("window.scrollTo(0, %s);" % (i*300))   # runter scrollen, sonst wird Element nicht aktiv
            browser.find_element_by_css_selector('.icon_galleys > img:nth-child(1)').click()
            try:
                browser.find_element_by_css_selector('#pdfDownloadLink').click()
                return False
            except:
                sleep(.05)
        toclick     = False

    elif url.find("asm.org") > -1:
        sublink     = url + ".full.pdf"
        browser     = open_page(browser, sublink, n_runner=1)

    elif url.find("lww.com") > -1:
        id          = browser.find_element_by_css_selector('#ctl00_ctl47_g_176ef1b5_d523_4cd9_bc3c_040e23e56098__4000834b041037_pdfListItem > a:nth-child(2)')
        sublink     = id.get_attribute("href")
        f = open(folder.tmp + "tmp.pdf", 'wb')
        f.write(http.request("GET", sublink).data)
        f.close()
        toclick     = False

    elif url.find("plos.org") > -1:
        sublink     = url.replace("article?id", "article/file?id") + "&type=printable"
        browser     = open_page(browser, sublink, n_runner=1)

    elif url.find("amsus.org") > -1:
        browser.find_element_by_css_selector('.show-pdf').click()

    elif url.find("aacrjournals.org") > -1:
        sublink     = url + ".full.pdf"
        browser     = open_page(browser, sublink, n_runner=1)

    elif url.find("researchprotocols.org") > -1:
        browser.find_element_by_css_selector('.icon-pdf').click()
        sleep(1)

    elif url.find("ingentaconnect") > -1:
        browser.find_element_by_css_selector('a.fulltext:nth-child(4) > i:nth-child(1)').click()
        sleep(8)
        browser.switch_to_window(browser.window_handles[1])
        sublink     = browser.current_url
        browser.close()
        browser.switch_to_window(browser.window_handles[0])
        browser     = open_page(browser, sublink, n_runner=1)

    elif url.find("iospress.com") > -1:
        id          = browser.find_element_by_css_selector("a.btn")
        sublink     = id.get_attribute("href")
        browser     = open_page(browser, sublink, n_runner=1)

    elif url.find("cambridge") > -1:
        id          = browser.find_element_by_css_selector("ul.grey > li:nth-child(1) > a:nth-child(1)")
        sublink     = id.get_attribute("href")
        browser     = open_page(browser, sublink, n_runner=1)

    elif url.find("karger.com") > -1:
        if url.find("Abstract") > -1:
            sublink     = url.replace("Abstract","Pdf")
        elif url.find("FullText") > -1:
            sublink = url.replace("FullText", "Pdf")
            browser     = open_page(browser, sublink, n_runner=1)

    elif url.find("liebertpub.com") > -1:
        sublink     = url.replace("/doi/abs/", "/doi/pdf/")
        browser     = open_page(browser, sublink, n_runner=1)

    elif url.find("dovepress.com") > -1:
        browser.find_element_by_id("download-pdf").click()
        toclick     = False

    elif url.find("hogrefe") > -1:
        sublink     = url.replace("/abs/", "/pdf/")
        browser     = open_page(browser, sublink, n_runner=1)

    elif url.find("angle.org") > -1:
        sublink     = url.replace("/doi/", "/doi/pdf/")
        browser     = open_page(browser, sublink, n_runner=1)

    elif url.find("boneandjoint.org") > -1:
        sleep(1)
        browser.find_element_by_xpath("/html/body/div[3]/section/div/div/div/div/div/div/div/div[2]/div[1]/div/div/div[1]/div/div/ul/li[5]/a[1]").click()
        sleep(2)
        windows     = browser.window_handles
        browser.switch_to_window(windows[1])
        sublink     = browser.current_url
        browser.close()
        browser.switch_to_window(windows[0])
        browser     = open_page(browser, sublink)
        sleep(1)

    elif url.find("neurology.org") > -1:
        sublink     = url + ".full.pdf"
        browser     = open_page(browser, sublink, n_runner=1)

    elif url.find("jbc.org") > -1:
        sublink     = url + ".full.pdf"
        browser     = open_page(browser, sublink, n_runner=1)

    elif url.find("pnas.org") > -1:
        sublink     = url + ".full.pdf"
        browser     = open_page(browser, sublink, n_runner=1)

    elif url.find("acs.org") > -1:
        sublink     = url.replace("/abs/", "/pdf/")
        browser     = open_page(browser, sublink, n_runner=1)

    elif url.find("physiology.org") > -1:
        sublink     = url.replace("/doi/", "/doi/pdf/")
        browser     = open_page(browser, sublink, n_runner=1)

    elif url.find("jneurosci.org") > -1:
        sublink     = url.replace("/content/", "/content/jneuro/") + ".full.pdf"
        browser     = open_page(browser, sublink, n_runner=1)

    elif url.find("mitpressjournals.org") > -1:
        sublink     = url.replace("/doi/", "/doi/pdf/")
        browser     = open_page(browser, sublink, n_runner=1)
        toclick     = False
        
    else:
        if url.find("dx.doi.org") > -1:
            pass
        elif url.find("regensburg") > -1:
            pass
        elif url.find("oadoi.org/faq") > -1:
            pass
        else:
                a = 1
            #pass
        return False


    return toclick, url, browser

##################################################################
#########################  OVID   ################################
##################################################################

def try_ovid(browser, http, doi, folder, old_url):
    initialize_ovid(browser)
    try:
        succ    = search_in_ovid(browser, doi)
        if succ == 0:
            follow_Freiburg_Link(browser, http, doi, folder, old_url)
        else:
            from definitions import save_pdf_with_loop
            save_pdf_with_loop(browser, folder, 20)
    except:
        pass

def initialize_ovid(browser):
    from time import sleep
    from definitions import open_page
    ## open Ovid
    mainlink        = "http://rzblx10.uni-regensburg.de/dbinfo/warpto.php?bib_id=ubfre&color=2&titel_id=288&url=http%3A%2F%2Fwww.redi-fr.belwue.de%2Fdb%2Fstart.php%3Fdatabase%3DMedline-ovid"
    open_page(browser, mainlink)
    sleep(2)

def search_in_ovid(browser, doi):
    from time import sleep
    from selenium.webdriver.common.keys import Keys
    ## switch to multi field tab
    browser.find_element_by_css_selector(".msp-modes-container > ul:nth-child(1) > li:nth-child(6) > span:nth-child(1) > a:nth-child(1) > h2:nth-child(1)").click()
    sleep(1)
    ## Enter Doi into Field
    input_field     = browser.find_element_by_css_selector("tr.msp-multifield-search-rows:nth-child(1) > td:nth-child(2) > input:nth-child(1)")
    input_field.send_keys(doi)
    ## Select the entered as DOI
    browser.find_element_by_css_selector("tr.msp-multifield-search-rows:nth-child(1) > td:nth-child(3) > select:nth-child(1) > option:nth-child(27)").click()
    sleep(.2)
    ## click search
    browser.find_element_by_css_selector(".msp-multifield-search-button").click()
    sleep(1)
    ## direkt PDF available
    id              = "a.render-form:nth-child(2)"
    succ            = 0
    try:
        if browser.find_element_by_css_selector(id).get_attribute("href").find("PDFLink"):
            browser.find_element_by_css_selector(id).click()
            succ    = 1
            sleep(0.5)
            id      = browser.find_element_by_xpath("/html/body/div[3]/div[1]/iframe[1]")
            browser.switch_to_frame(id)
            
    except:
        pass
    if succ == 0:
    ## Button for Links find and press
        from definitions import open_page
        browser.find_element_by_css_selector(".gbutton").click()
        sleep(1.4)
        ## catch new window as active; close old one
        windows         = browser.window_handles
        #browser.close()
        browser.switch_to_window(windows[1])
        new_url         = browser.current_url
        browser.close()
        browser.switch_to_window(windows[0])
        open_page(browser, new_url)
        sleep(0.5)
    return succ

##################################################################
###################### FREIBURG LINK #############################
##################################################################

def follow_Freiburg_Link(browser, http, doi, folder, old_url):
    from time import sleep
    from definitions import save_pdf_with_loop, open_page
    url             = browser.current_url
    site            = http.request("GET", url)
    start           = site.data.decode("utf-8").find("Elektronischer Volltext")
    ende            = site.data.decode("utf-8").find("Lokale Verfügbarkeit")
    part            = site.data[start:ende].decode("utf-8")
    part            = part.replace("amp;", "")
    link_start      = part.find("http")
    link_ende       = part.find('"', link_start + 1)
    while (link_start > -1):
        try:
            open_page(browser, part[link_start:link_ende])
            sleep(.6)
            if browser.current_url.find(".pdf") > -1:
                success     = save_pdf_with_loop(browser, folder, 10)
            elif browser.current_url == old_url:
                success     = False
            else:
                success     = open_pdf_url(browser,http, doi, folder)
                if success == True:
                    ovid_loop  = save_pdf_with_loop(browser, folder, 40)
                    if ovid_loop == -3:
                        success  = False
            if success == True:
                return True
        except:
            pass
        link_start  = part.find("http", link_start + 5)
        link_ende   = part.find('"',    link_start + 1)
    return False