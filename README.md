# doiscout

_Please see the manual (manual.pdf) for more information._


The DoiScout – an automatic tool for gathering information about registered clinical trials and resulting publications

**Description**
The DoiScout is a tool that facilitates large-scale literature reviews and citation 
analyses. It was developed as part of the IIT project, “Impact of therapeutic
investigator initiated trials on medical practice“ (DFG grant number BL 1395/2-
1), in order to make the process of extensive literature searches more time
effective.

The DoiScout offers two primary features. The first main feature is the
automatic identification of publications that reference a particular study number
(e.g. NCT02179424) as their source. Information about relevant publications
is extracted and presented in a list that is formatted so that information can
be passed on to other software programs for further processing. Note that the
DoiScout does not automatically assess the relevance or validity of the search
results.

The second primary feature of the DoiScout is the identification of citations.
Databases behind such platforms as PubMed and Web of Science can be used
to identify articles, systematic reviews and clinical guidelines in which a given
article has been cited. The DoiScout extracts information about these texts and
provides it to the user in a workable format. In addition, the DoiScout can be
used to identify publications that go on to cite texts citing the original source,
thus providing a comprehensive insight into the extent of a project’s academic
impact.

In addition to these two primary features, the DoiScout includes several
secondary features, which focus on facilitating workflow.

**Python and Packages**

The DoiScout was written in Python 3.6. To run, it requires that the following software is installed (note that all required software is available free of charge):

• Python 3. Any software version newer or equal to Python 3.6 should work. Older version might work. You can get more information on as well as download Python 3 on https://www.python.org/

• Mozilla Firefox is the most common free and open source web browser.

• The geckodriver is needed so the DoiScout is able to automatically operate Mozilla Firefox. It can be downloaded for free here: https://github.com/mozilla/geckodriver/releases. Download the file geckodriver and store it in the same folder that you have extracted the DoiScout to.

• In order to use the optional feature of the notification mails, SSMTP must be installed on your system. This feature has only been tested on a linux system.



The Python libraries that are required to run the DoiScout are: 

_datetime, numbers, operator, os, pandas, pdfkit, random, re, selenium, sys, time, tkinter, urllib3, weasyprint, webbrowser, xlrd_



**Starting the DoiScout**

Start the ***DoiScout.py*** script with the _Python3_ distribution of your computer. The exact process for this depends on your computer's operation system (OS). 
For most OS this works via commandline/terminal with the command:

_python3 /PATH/TO/YOUR/DOISCOUTFOLDER/DoiScout.py_
