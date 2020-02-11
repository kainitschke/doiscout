
import xlrd
from os import path
from tkfilebrowser import askopenfilename
from pandas import DataFrame as df

### create empty Dataframe
result          = df(columns=['ID',                       # ID
                              'Authors',                  # AU
                              'Year',                     # YR
                              'Journal',                  # SO
                              'Volume',                   # VL
                              'Number',                   # NO
                              'Page',                     # PG
                              'DOI',                      # DOI
                              'Pub.Type',                 # PT
                              'PMID',                     # PM
                              'EMBASE',                   # XR
                              'CochGroup',                # CC
                              'url',                      # US
                              'Title',                    # TI
                              'Abstract'])                # AB

#df(columns=['ID', 'Authors','Year','Journal','Volume','Number','Page','DOI','Pub.Type','PMID','EMBASE','CochGroup','url','Title','Abstract'])

### Read
originfile      = path.split(askopenfilename(parent=None, title="Select txt-file", filetypes = (("Text files","*.txt*"),("all files","*.*"))))
origin          = open(path.join(originfile[0], originfile[1]), "r")

aline           = 0
atext           = origin.readline()
while atext != "":
    if atext[0:6] == "Record":
        aline   = aline + 1
        result.loc[aline, 'Authors']    = ""
    elif atext[0:2] == "ID":
        result.loc[aline, 'ID']         = atext[4:len(atext)].replace('\n', '').strip()
    elif atext[0:2] == "AU":
        result.loc[aline, 'Authors']    = result.loc[aline, 'Authors'] + atext[4:len(atext)].replace('\n', '').strip() + ", "
    elif atext[0:2] == "TI":
        result.loc[aline, 'Title']      = atext[4:len(atext)].replace('\n', '').strip()
    elif atext[0:2] == "YR":
        result.loc[aline, 'Year']       = atext[4:len(atext)].replace('\n', '').strip()
    elif atext[0:2] == "VL":
        result.loc[aline, 'Volume']     = atext[4:len(atext)].replace('\n', '').strip()
    elif atext[0:2] == "PG":
        result.loc[aline, 'Page']       = atext[4:len(atext)].replace('\n', '').strip()
    elif atext[0:2] == "PM":
        result.loc[aline, 'PMID']       = atext[4:len(atext)].replace('\n', '').replace("PUBMED", "").strip()
    elif atext[0:2] == "XR":
        result.loc[aline, 'EMBASE']     = atext[4:len(atext)].replace('\n', '').replace("EMBASE", "").strip()
    elif atext[0:3] == "DOI":
        result.loc[aline, 'DOI']        = atext[5:len(atext)].replace('\n', '').strip()
    elif atext[0:2] == "AB":
        result.loc[aline, 'Abstract']   = atext[4:len(atext)].replace('\n', '').strip()
    elif atext[0:2] == "US":
        result.loc[aline, 'url']        = atext[4:len(atext)].replace('\n', '').strip()
    elif atext[0:2] == "CC":
        result.loc[aline, 'CochGroup']  = atext[4:len(atext)].replace('\n', '').strip()
    elif atext[0:2] == "NO":
        result.loc[aline, 'Number']     = atext[4:len(atext)].replace('\n', '').strip()
    elif atext[0:2] == "PT":
        result.loc[aline, 'Pub.Type']   = atext[4:len(atext)].replace('\n', '').strip()
    elif atext[0:2] == "SO":
        result.loc[aline, 'Journal']    = atext[4:len(atext)].replace('\n', '').strip()
    atext       = origin.readline()

origin.close()

### Write
result.to_excel(path.join(originfile[0], "01_processed_results.xlsx"), index=False)