#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

#DB classes
db_url = 'mysql+pymysql://root:123456@192.168.1.128:3306/MYSQL57'
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = db_url
db = SQLAlchemy(app)
import uuid

class PatientTable(db.Model):
    __tablename__ = "Patient"
    def __init__(self, patient_info):
        self.PatientID = patient_info.PatientID
        self.PatientName = patient_info.PatientName
        self.DePatientID = patient_info.DePatientID
        self.DePatientName = patient_info.DePatientName
        self.PatientBirthDate = patient_info.PatientBirthDate
        self.PatientBirthTime = patient_info.PatientBirthTime
        self.PatientSex = patient_info.PatientSex
        self.PatientUID = ""
        # self.NumberOfPatientRelatedStudies = patient_info.NumberOfPatientRelatedStudies
        # self.NumberOfPatientRelatedSeries = patient_info.NumberOfPatientRelatedSeries
        # self.NumberOfPatientRelatedInstances = patient_info.NumberOfPatientRelatedInstances

    PatientUID = db.Column(db.String(64), primary_key=True)
    PatientID = db.Column(db.String(64), unique=False, nullable=True, index = True)
    PatientName = db.Column(db.String(64), unique=False, nullable=True)
    DePatientID = db.Column(db.String(64), unique=False, nullable=True)
    DePatientName = db.Column(db.String(64), unique=False, nullable=True)
    PatientBirthDate = db.Column(db.String(64), unique=False, nullable=True)
    PatientBirthTime = db.Column(db.String(64), unique=False, nullable=True)
    PatientSex = db.Column(db.String(64), unique=False, nullable=True)


    def Insert(self, puidlist):
        if(self.IsNewPatient()):
            self.PatientUID = str(uuid.uuid4())
            db.session.add(self)
            db.session.commit()
            puidlist.append(self.PatientUID)
            return True
        else:
            puidlist.append(self.PatientUID)
        return True


    def IsNewPatient(self):
        exist_patient = self.query.filter_by(PatientID=self.PatientID).first()

        if exist_patient is None:
            return True
        #有一个不一样即为新病人
        result =    (exist_patient.PatientName == self.PatientName) and \
                    (exist_patient.PatientBirthDate == self.PatientBirthDate) and \
                    (exist_patient.PatientSex == self.PatientSex)
        if result == False:
            return True
        else:
            self.PatientUID = exist_patient.PatientUID
            return False

class StudyTable(db.Model):
    __tablename__ = "Study"
    def __init__(self):
        self.StudyInstanceUID = None
        self.PatientUID = None
        self.DeStudyUID = None
        self.StudyDate = None
        self.StudyTime = None
        self.AccessionNumber = None
        self.StudyID = None
        self.ReferringPhysicianName = None
        self.StudyDescription = None
        self.PatientAge = None
        self.PatientSize = None
        self.PatientWeight = None
        self.StudyBuildTime = None
        # NumberOfStudyRelatedSeries,
        # NumberOfStudyRelatedInstances
        return

    StudyInstanceUID = db.Column(db.String(128), primary_key=True, unique=True, nullable=False, index = True)
    PatientUID = db.Column(db.String(64), unique=False, nullable=False)
    DeStudyUID = db.Column(db.String(128), unique=False, nullable=True)
    StudyDate = db.Column(db.String(64), unique=False, nullable=True)
    StudyTime = db.Column(db.String(64), unique=False, nullable=True)
    AccessionNumber = db.Column(db.String(64), unique=False, nullable=True)
    StudyID = db.Column(db.String(64), unique=False, nullable=True)
    ReferringPhysicianName = db.Column(db.String(64), unique=False, nullable=True)
    StudyDescription = db.Column(db.String(64), unique=False, nullable=True)
    PatientAge = db.Column(db.String(64), unique=False, nullable=True)
    PatientSize = db.Column(db.String(64), unique=False, nullable=True)
    PatientWeight = db.Column(db.String(64), unique=False, nullable=True)
    StudyBuildTime = db.Column(db.String(64), unique=False, nullable=True)


    def Insert(self, study_info, patient_uid):

        self.StudyInstanceUID = study_info.StudyInstanceUID
        self.PatientUID = patient_uid
        self.DeStudyUID = study_info.DeStudyUID
        self.StudyDate = study_info.StudyDate
        self.StudyTime = study_info.StudyTime
        self.AccessionNumber = study_info.AccessionNumber
        self.StudyID = study_info.StudyID
        self.ReferringPhysicianName = study_info.ReferringPhysicianName
        self.StudyDescription = study_info.StudyDescription
        self.PatientAge = study_info.PatientAge
        self.PatientSize = study_info.PatientSize
        self.PatientWeight = study_info.PatientWeight
        self.StudyBuildTime = study_info.StudyBuildTime

        result = self.query.filter_by(StudyInstanceUID=self.StudyInstanceUID).first()
        if result is None:          #is new study
            db.session.add(self)
            db.session.commit()
            return True
        else:
            return False

class SeriesTable(db.Model):
    __tablename__ = "Series"
    def __init__(self, series_info):
        self.SeriesInstanceUID = series_info.SeriesInstanceUID
        self.StudyInstanceUID = series_info.StudyInstanceUID
        self.DeSeriesUID = series_info.DeSeriesUID
        self.Modality = series_info.Modality
        self.SeiresNumber = series_info.SeiresNumber
        self.SeriesDate = series_info.SeriesDate
        self.SeriesTime = series_info.SeriesTime
        self.PerformingPhysicianName = series_info.PerformingPhysicianName
        self.ProtocolName = series_info.ProtocolName
        self.SeriesDescription = series_info.SeriesDescription
        self.OperatorsName = series_info.OperatorsName
        self.BodyPartExamined = series_info.BodyPartExamined
        self.PatientPosition = series_info.PatientPosition
        self.Laterality = series_info.Laterality
        # self.NumberOfSeriesRelatedInstances = series_info.NumberOfSeriesRelatedInstances
        return

    SeriesInstanceUID = db.Column(db.String(128), primary_key=True, unique=True, nullable=False, index=True)
    StudyInstanceUID = db.Column(db.String(128), unique=False, nullable=True)
    DeSeriesUID = db.Column(db.String(128), unique=False, nullable=True)
    Modality = db.Column(db.String(64), unique=False, nullable=True)
    SeiresNumber = db.Column(db.String(64), unique=False, nullable=True)
    SeriesDate = db.Column(db.String(64), unique=False, nullable=True)
    SeriesTime = db.Column(db.String(64), unique=False, nullable=True)
    PerformingPhysicianName = db.Column(db.String(64), unique=False, nullable=True)
    ProtocolName = db.Column(db.String(64), unique=False, nullable=True)
    SeriesDescription = db.Column(db.String(64), unique=False, nullable=True)
    OperatorsName = db.Column(db.String(64), unique=False, nullable=True)
    BodyPartExamined = db.Column(db.String(64), unique=False, nullable=True)
    PatientPosition = db.Column(db.String(64), unique=False, nullable=True)
    Laterality = db.Column(db.String(64), unique=False, nullable=True)

    def Insert(self):
        result = self.query.filter_by(SeriesInstanceUID=self.SeriesInstanceUID).first()
        if result is None:          #is new study
            db.session.add(self)
            db.session.commit()
            return True
        else:
            return False

class ImageTable(db.Model):
    __tablename__ = "Image"
    def __init__(self, image_info):
        self.SOPInstanceUID = image_info.SOPInstanceUID
        self.SeriesInstanceUID = image_info.SeriesInstanceUID
        self.DeSOPInstanceUID = image_info.DeSOPInstanceUID
        self.InstanceNumber = image_info.InstanceNumber
        self.SOPClassUID = image_info.SOPClassUID
        self.PatientOrientation = image_info.PatientOrientation
        self.ContentDate = image_info.ContentDate
        self.ContentTime = image_info.ContentTime
        self.ImageType = image_info.ImageType
        self.AcquisitionNumber = image_info.AcquisitionNumber
        self.AcquisitionDate = image_info.AcquisitionDate
        self.AcquisitionTime = image_info.AcquisitionTime
        self.ImagesinAcquisition = image_info.ImagesinAcquisition
        self.ImageComments = image_info.ImageComments
        self.PresentationLUTShape = image_info.PresentationLUTShape
        self.SourcePath = image_info.SourcePath
        self.AnonymizedPath = image_info.AnonymizedPath
        self.ImageThumbnailPath = image_info.ThumbnailPath
        return

    SOPInstanceUID = db.Column(db.String(128), primary_key=True, unique=True, nullable=False, index=True)
    SeriesInstanceUID = db.Column(db.String(128), unique=False, nullable=True)
    DeSOPInstanceUID = db.Column(db.String(128), unique=False, nullable=True)
    InstanceNumber = db.Column(db.String(64), unique=False, nullable=True)
    SOPClassUID = db.Column(db.String(128), unique=False, nullable=True)
    PatientOrientation = db.Column(db.String(64), unique=False, nullable=True)
    ContentDate = db.Column(db.String(64), unique=False, nullable=True)
    ContentTime = db.Column(db.String(64), unique=False, nullable=True)
    ImageType = db.Column(db.String(64), unique=False, nullable=True)
    AcquisitionNumber = db.Column(db.String(64), unique=False, nullable=True)
    AcquisitionDate = db.Column(db.String(64), unique=False, nullable=True)
    AcquisitionTime = db.Column(db.String(64), unique=False, nullable=True)
    ImagesinAcquisition = db.Column(db.String(64), unique=False, nullable=True)
    ImageComments = db.Column(db.String(64), unique=False, nullable=True)
    PresentationLUTShape = db.Column(db.String(64), unique=False, nullable=True)
    SourcePath = db.Column(db.String(1024), unique=False, nullable=True)
    AnonymizedPath = db.Column(db.String(1024), unique=False, nullable=True)
    ImageThumbnailPath = db.Column(db.String(1024), unique=False, nullable=True)

    def Insert(self):
        result = self.query.filter_by(SOPInstanceUID=self.SOPInstanceUID).first()
        if result is None:          #is new study
            db.session.add(self)
            db.session.commit()
            return True
        else:
            return False

#in: DcmInfo
class CuckooDB:
    def __init__(self):
        # self.Patient = PatientTable()
        # self.Study = StudyTable()
        # self.Series = SeriesTable()
        # self.Image = ImageTable()
        self.dcm_info = None

    def Connect(self):
        try:
            db.engine.execute('SELECT 1')
        except Exception as e:
            print 'Failed to connect db! \n' + str(e)
            return False
        return True


    def InsertDcmInfor(self, dcm_info):
        self.dcm_info = dcm_info
        #check is avaliable to insert
        puidlist = []
        self.InsertPatient(self.dcm_info.PatientInfo, puidlist)
        self.InsertStudy(self.dcm_info.StudyInfo, puidlist)
        self.InsertSeries(self.dcm_info.SeriesInfo)
        self.InsertImage(self.dcm_info.ImageInfo)

    def InsertPatient(self, pInfo, puidlist):
        patient = PatientTable(pInfo)
        return patient.Insert(puidlist)

    def InsertStudy(self, pInfo, puidlist):
        study = StudyTable()
        return study.Insert(pInfo, puidlist.pop())

    def InsertSeries(self, pInfo):
        series = SeriesTable(pInfo)
        return series.Insert()

    def InsertImage(self, pInfo):
        image = ImageTable(pInfo)
        return image.Insert()

    def GetStudyList(self):
        studyList = ['PatientName',	'PatientSex', 'PatientID','PatientAge',	'AccessionNumber',
                     'StudyDescritpion',	'StudyDate',	'StudyTime']
        study = StudyTable()
        resList = study.query.all()
        return resList

    def GetPatientStudyView(self):

        result = self.ExcuteSQL('select * from Patient_Study')
        i = result.rowcount
        names = []
        # for row in result:
        #     for i in range(result.rowcount):
        #         print row[i]

        return result

    def ExcuteSQL(self, sqlstr):
        result = None
        try:
            result = db.engine.execute(sqlstr)
        except Exception as e:
            print 'ExcuteSQL() Failed: ' + sqlstr + '\n' + str(e)
        return result

    def GetThumbsByStudyUID(self, studyUID):
        sql = 'select ImageThumbnailPath from image '
        sql1 = "select ImageThumbnailPath from image where SeriesInstanceUID = " \
               "(select SeriesInstanceUID from series where StudyInstanceUID = '" + studyUID + "')"
        results = self.ExcuteSQL(sql)
        imageNames  = []
        for res in results:
            imageNames.append(os.path.basename(res[0]))     #将文件名取出来
        return imageNames

    def GetSeriesUIDFromStudyUID(self, studyUID):
        seriesUIDs = []
        result = SeriesTable.query.filter_by(StudyInstanceUID = studyUID)
        for res in result:
            seriesUIDs.append(res.SeriesInstanceUID)
        return seriesUIDs

    def GetImageNameFromSeiresUID(self, seriesUID):
        imageList = []
        result = ImageTable.query.filter_by(SeriesInstanceUID = seriesUID)
        for res in result:
            imageName = os.path.basename(res.ImageThumbnailPath)
            imageList.append(imageName)
        return imageList

    # 返回一个dict<key(seriesUID), list[(imageName)]>
    def GetStudyPanelThumbsByStudyUID(self, studyUID):
        seriesDict = {}
        seriesUIDs = self.GetSeriesUIDFromStudyUID(studyUID)
        for seriesUID in seriesUIDs:
            imageList = []
            imageList = self.GetImageNameFromSeiresUID(seriesUID)
            seriesDict[seriesUID] = imageList
        return seriesDict



