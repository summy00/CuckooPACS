# CuckooPACS
A mini-PACS web system using javascript and python

Front End:
Using DWV & DOM for simple show

Back End:
Using python  flask for web server, pydicom & mudicom for Dicom parse.
Using MySQL database.

---------------
CuckooWeb: web server, using flask & dwv.

CuckooDicom: app server, dicom parser, parse dcm files, update db, create thumbnail for web display

You should use CuckooDicom for parsing dcms and then access CuckooWeb for displaying study & image.

-----------
Thanks for XiaoDong supply 'SetWindow' algorithm.
