# doiscout
The DoiScout – an automatic tool for accumulating information about registered clinical trials and resulting publications

Please see the manual (manual.pdf) for all information.


**Python and Packages**

The DoiScout was written in Python 3.6. To run, it requires that the following software is installed (note that alls required software is available free of charge):

• Python 3. Any software version newer or equal to Python 3.6 should work. Older version might work. You can get more information on as well as download Python 3 on https://www.python.org/

• Mozilla Firefox is the most common free and open source web browser.

• The geckodriver is needed so the DoiScout is able to automatically operate Mozilla Firefox. It can be downloaded for free here: https: //github.com/mozilla/geckodriver/releases . Download the file geckodriver and store it in the same folder that you have extracted the DoiScout to.

• In order to use the optional feature of the notification mails, SSMTP must be installed on your system. This feature has only been tested on a linux system.



If SSMTP is not available on your operating system, the DoiScout will still function properly despite the loss of the email feature (E-mails). Do not select the respective options if SSMTP is not installed on your OS. The Python libraries that are required to run the DoiScout are: 
datetime, numbers, operator, os, pandas, pdfkit, random, re, selenium, sys, time, tkinter, urllib3, weasyprint, webbrowser, xlrd
