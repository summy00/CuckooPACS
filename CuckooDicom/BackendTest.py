#!/usr/bin/env python
# -*- coding: utf-8 -*-

from CuckooParser import CuckooParser
from CuckooDB import CuckooDB
# from PIL import Image
import os
from CuckooDB import CuckooDB, db
import shutil


def printDBResult(result):
    for row in result:
        # for i in row.count:
            print row[0]
            print len(row)
            # try:
            #     print row[i]
            # except Exception as e:
            #     continue

def iteratorDcmDir(dirpath):
    pass
import string
import random
def random_string(length):
    return ''.join(random.choice(string.ascii_letters) for m in range(length))
def testDcms():
    from os import walk
    mypath = "D:/dcms/webtestdcms"
    db = CuckooDB()
    if not db.Connect():
        return
    thumbsPath = 'D:/Projects/Bootstrap_Test/thumbnails'
    dcmStoragePath = "D:/Projects/Bootstrap_Test/dcmfiles"
    filelist = []
    for root, dirs, files in os.walk(mypath):
        for file in files:
            p = os.path.join(root, file)
            filelist.append(os.path.abspath(p))

    for file in filelist:
        parser = CuckooParser(file)
        parser.Parse()
        parser.Convert2Image(thumbsPath + "/" + random_string(6) + ".jpg")
        pInfo = parser.ParseInfo()
        db.InsertDcmInfor(pInfo)
        shutil.copy2(file, dcmStoragePath + "/" + random_string(6)+ ".dcm" )

def main():
    # fileFolder = os.path.join(os.path.expanduser('~'), 'fkw')
    fileFolder = 'D:/Projects/Bootstrap_Test/thumbnails'
    files = ['dcm_1_2_1_CT.dcm', 'dcm_1_2.dcm', 'dcm_70.dcm', '91_ts.dcm']
    db = CuckooDB()
    if not db.Connect():
        print 'None'
        return

    for file in files:
        filePath = fileFolder + "/" + file

        parser = CuckooParser(filePath)
        parser.Parse()
        parser.Convert2Image(filePath + ".jpg")
        pInfo = parser.ParseInfo()
        db.InsertDcmInfor(pInfo)

    # resList = db.GetPatientStudyView()
    # res = db.GetThumbsByStudyUID("1.2.156.600734.0000936184.20170422.11373968")
    # printDBResult(resList)

    # name = pInfo.PatientInfo.PatientName
    # print name
    #
    # def GetUnicodePName(inName):
    #     from pydicom import compat
    #     from pydicom.valuerep import PersonNameUnicode
    #     default_encoding = 'iso8859'
    #     return PersonNameUnicode(inName, [default_encoding, 'GB18030'])
    #
    # print GetUnicodePName(name)

    # import chardet
    #
    # res = chardet.detect(name)
    #
    # print res
    # print res['encoding']
    # print name
    # name.decode(res['encoding'])
    #
    # print name



    # import mudicom
    #
    # mu = mudicom.load(imagePath)
    # l
    # # returns array of data elements as dicts
    # mu.read()
    #
    # # returns dict of errors and warnings for DICOM
    # # mu.validate()
    #
    # # basic anonymization
    # # mu.anonymize()
    # # save anonymization
    # # mu.save_as("dicom.dcm")
    #
    # # creates image object
    # img = mu.image  # before v0.1.0 this was mu.image()
    # # returns numpy array
    # img.numpy  # before v0.1.0 this was mu.numpy()
    #
    # # using Pillow, saves DICOM image
    # img.save_as_pil(imagePath + "_mu.jpg")
def testStudyQuery():
    db = CuckooDB()
    if not db.Connect():
        print 'db.Connect() failed!'
        return

    studyUID = '1.2.840.113970.3.57.1.52951248.20160509.1101416'
    seriesDict = db.GetStudyPanelThumbsByStudyUID(studyUID)
    outerDict = {}
    for seriesUID in seriesDict.keys():
        outerDict[seriesUID] = seriesDict[seriesUID].pop()

    return outerDict
if __name__ == '__main__':
    # db.create_all()
    # main()
    testDcms()
    # testStudyQuery()