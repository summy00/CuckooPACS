#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pydicom
from pydicom.uid import UID, generate_uid, PYDICOM_ROOT_UID, JPEGLSLossy
from pydicom.errors import InvalidDicomError
import datetime
from datetime import datetime
import copy
from CuckooImage import CuckooImage
from pydicom import uid

class CuckooParser:
    # path = 123
    # def __init__(self, in_path):
    #     self.file_path = in_path
    #     self.anonymize_out_path = 0
    #     self.dcm_dataset = pydicom.read_file(self.file_path)
    #     # self.dcm_info = DcmInfo()

    def __init__(self, in_path):
        self.file_path = in_path
        self.thumbnail_path = ""
        self.anonymize_out_path = ""
        self.DeStudyUID = ""
        self.DeSeriesUID = ""
        self.DeImageUID = ""
        self.DePatientID = ""
        self.DePatientName = ""
        self.AccessionNumber = ""
        self.transferSyntax = None
        self.intercept = None
        self.slope = None
        self.wWidth = None
        self.wCenter = None
        self.PhotometricInterpretation = None
        self.dcm_dataset = None

    def Parse(self):
        try:
            self.dcm_dataset = pydicom.read_file(self.file_path)
        except InvalidDicomError:
            print("Invalid dicom file: " + self.file_path)

        self.transferSyntax = self.dcm_dataset.file_meta.TransferSyntaxUID
        self.PhotometricInterpretation = self.dcm_dataset.PhotometricInterpretation

        if self.PhotometricInterpretation == 'MONOCHROME1' or self.PhotometricInterpretation == 'MONOCHROME2':
            if ('RescaleIntercept' in self.dcm_dataset and 'RescaleSlope' in self.dcm_dataset):
                self.intercept = self.dcm_dataset.RescaleIntercept
                self.slope = self.dcm_dataset.RescaleSlope

            if ('WindowWidth' in self.dcm_dataset and 'WindowCenter' in self.dcm_dataset):
                from pydicom import dataelem
                if dataelem.isMultiValue(self.dcm_dataset.WindowWidth):
                    self.wWidth = self.dcm_dataset.WindowWidth[0]
                    self.wCenter = self.dcm_dataset.WindowCenter[0]
                else:
                    self.wWidth = self.dcm_dataset.WindowWidth
                    self.wCenter = self.dcm_dataset.WindowCenter
        # elif self.PhotometricInterpretation == 'RGB':
        #     pass
        # else

    def ParseInfo(self):
        # patient level
        self.patient_info = PatientInfo(self.dcm_dataset, self.DePatientID, self.DePatientName)

        # study level
        self.study_info = StudyInfo(self.dcm_dataset, self.DeStudyUID)

        # series level
        self.series_info = SeriesInfo(self.dcm_dataset, self.DeSeriesUID)

        # image level
        self.image_info = ImageInfo(self.dcm_dataset, self.DeImageUID, self.file_path, self.anonymize_out_path, self.thumbnail_path)

        self.dcm_info = DcmInfo(self.patient_info, self.study_info, self.series_info, self.image_info)
        return self.dcm_info

    def Convert2Image(self, out_Path):
        self.thumbnail_path = out_Path
        pixel = None
        img = CuckooImage(self)
        pixel = img.GetPixelByTransferSyntax()
        pixelP = img.SetDefaultWindow(pixel)
        img.Convert2Pic(pixelP, out_Path)
        return

    def SetAnonymizeOutPaths(self, out_path):
        self.anonymize_out_path = out_path

    # invoke pydicom to parse dcm, out put DcmInfo
    # def Parse(self):
    #     self.GetDcmInfoFromDataset()
    #     return

    # def LoadDcm(self):
    #     {}

    def SetDeTags(self, subject_id, visit_name):
        self.DePatientID = subject_id
        self.DePatientName = subject_id
        self.AccessionNumber = visit_name
        return

    def GetDcmInfo(self):
        # patient level
        return self.dcm_info

    def Anonymize(self, out_path, remove_tag_list):
        self.modified_dataset = copy.copy(self.dcm_dataset)
        self.anonymize_out_path = out_path
        # create UIDs for De-Identification
        # self.DeStudyUID = generate_uid()
        # self.DeSeriesUID = generate_uid()
        # self.DeImageUID = generate_uid()
        self.DeStudyUID = ""
        self.DeSeriesUID = ""
        self.DeImageUID = ""

        # modify tags & save to out_path
        print("Anonymizing...")

        self.modified_dataset.PatientID = self.DePatientID
        self.modified_dataset.PatientName = self.DePatientName
        self.modified_dataset.AccessionNumber = self.AccessionNumber
        # self.dcm_dataset.StudyDescription = "" #TBD

        # 为防止study和series的关联关系破坏 暂时去掉匿名化UID 以后再看需求是否需要重新生成关联关系
        # self.modified_dataset.StudyInstanceUID = self.DeStudyUID
        # self.modified_dataset.SeriesInstanceUID = self.DeSeriesUID
        # self.modified_dataset.SOPInstanceUID = self.DeImageUID

        for tag in remove_tag_list:
            if tag in self.modified_dataset:
                delattr(self.modified_dataset, tag)

        self.modified_dataset.remove_private_tags()
        # remove all overlay tags: 0x60XX,XXXX
        self.RemoveOverlayTags()

        self.modified_dataset.save_as(out_path)
        # print(self.dcm_info2.PatientInfo.PatientID)
        return True

    def GetTagValue(self, tag_name):
        value = ""
        try:
            value = self.dcm_dataset.data_element(tag_name).value
        except KeyError:
            return value;

        return value;

    def IsOverlayTag(self, tag_group):
        group = tag_group & 0xFF00
        if (group == 0x6000):
            return True
        else:
            return False

    def RemoveOverlayTags(self):
        """Remove all overlay DataElements in the Dataset."""

        def RemoveCallback(dataset, data_element):
            """Internal method to use as callback to walk() method."""
            if (data_element.tag.group & 0xFF00 == 0x6000):
                # if (data_element.tag.group & 0x00FF == 0x0020):   #for test
                # can't del self[tag] - won't be right dataset on recursion
                del dataset[data_element.tag]

        self.modified_dataset.walk(RemoveCallback)


class PatientInfo:
    def __init__(self,
                 PatientID,
                 PatientName,
                 PatientBirthDate,
                 PatientBirthTime,
                 PatientSex,
                 DePatientID,
                 DePatientName,
                 NumberOfPatientRelatedStudies,
                 NumberOfPatientRelatedSeries,
                 NumberOfPatientRelatedInstances
                 ):
        self.PatientID = PatientID
        self.PatientName = PatientName
        self.DePatientID = DePatientID
        self.DePatientName = DePatientName
        self.PatientBirthDate = PatientBirthDate
        self.PatientBirthTime = PatientBirthTime
        self.PatientSex = PatientSex
        self.NumberOfPatientRelatedStudies = NumberOfPatientRelatedStudies
        self.NumberOfPatientRelatedSeries = NumberOfPatientRelatedSeries
        self.NumberOfPatientRelatedInstances = NumberOfPatientRelatedInstances



    def __init__(self, dataset, DePatientID, DePatientName):

        def Decode2PNGB(inName):
            from pydicom.valuerep import PersonNameUnicode
            default_encoding = 'iso8859'
            return PersonNameUnicode(inName, [default_encoding, 'GB18030'])

        def DecodeElement2GB18030(data_element):
            from pydicom import charset
            charset.decode(data_element, ['GB18030'])

        patient_info_list = [
            'PatientID',
            'PatientName',
            'PatientBirthDate',
            'PatientBirthTime',
            'PatientSex']

        list_value = []
        # DecodeElement2GB18030(dataset.data_element(patient_info_list[1]))
        # value = dataset.data_element(patient_info_list[4]).value
        for i, tag in enumerate(patient_info_list):
            try:
                dataValue = dataset.data_element(patient_info_list[i]).value
                # utf8Str = dataValue.encode('utf-8')
                tagStr = str(dataValue)
                list_value.append(tagStr)
            except KeyError:
                list_value.append("")

        self.PatientID = list_value[0]
        self.PatientName = Decode2PNGB(list_value[1])
        self.PatientBirthDate = list_value[2]
        self.PatientBirthTime = list_value[3]
        self.PatientSex = Decode2PNGB(list_value[4])
        self.DePatientID = DePatientID
        self.DePatientName = DePatientName




class StudyInfo:
    def __init__(self,
                 StudyInstanceUID,
                 PatientID,
                 DeStudyUID,
                 StudyDate,
                 StudyTime,
                 AccessionNumber,
                 StudyID,
                 ReferringPhysicianName,
                 StudyDescription,
                 PatientAge,
                 PatientSize,
                 PatientWeight,
                 NumberOfStudyRelatedSeries,
                 NumberOfStudyRelatedInstances,
                 StudyBuildTime
                 ):
        self.StudyInstanceUID = StudyInstanceUID
        self.PatientID = PatientID
        self.DeStudyUID = DeStudyUID
        self.StudyDate = StudyDate
        self.StudyTime = StudyTime
        self.AccessionNumber = AccessionNumber
        self.StudyID = StudyID
        self.ReferringPhysicianName = ReferringPhysicianName
        self.StudyDescription = StudyDescription
        self.PatientAge = PatientAge
        self.PatientSize = PatientSize
        self.PatientWeight = PatientWeight
        self.NumberOfStudyRelatedSeries = NumberOfStudyRelatedSeries
        self.NumberOfStudyRelatedInstances = NumberOfStudyRelatedInstances
        self.StudyBuildTime = StudyBuildTime

    def __init__(self, dataset, DeStudyUID):
        study_info_list = [
            'StudyInstanceUID',
            'StudyDate',
            'StudyTime',
            'AccessionNumber',
            'StudyID',
            'ReferringPhysicianName',
            'StudyDescription',
            'PatientAge',
            'PatientSize',
            'PatientWeight']
        list_value = []
        for i, tag in enumerate(study_info_list):
            try:
                list_value.append(str(dataset.data_element(study_info_list[i]).value))
            except KeyError:
                list_value.append("")

        self.DeStudyUID = DeStudyUID
        self.StudyInstanceUID = list_value[0]
        self.StudyDate = list_value[1]
        self.StudyTime = list_value[2]
        self.AccessionNumber = list_value[3]
        self.StudyID = list_value[4]
        self.ReferringPhysicianName = list_value[5]
        self.StudyDescription = list_value[6]
        self.PatientAge = list_value[7]
        self.PatientSize = list_value[8]
        self.PatientWeight = list_value[9]
        self.StudyBuildTime = str(datetime.now())


class SeriesInfo:
    def __init__(self,
                 SeriesInstanceUID,
                 StudyInstanceUID,
                 DeSeriesUID,
                 Modality,
                 SeiresNumber,
                 SeriesDate,
                 SeriesTime,
                 PerformingPhysicianName,
                 ProtocolName,
                 SeriesDescription,
                 OperatorsName,
                 BodyPartExamined,
                 PatientPosition,
                 Laterality,
                 NumberOfSeriesRelatedInstances
                 ):
        self.SeriesInstanceUID = SeriesInstanceUID
        self.StudyInstanceUID = StudyInstanceUID
        self.DeSeriesUID = DeSeriesUID
        self.Modality = Modality
        self.SeiresNumber = SeiresNumber
        self.SeriesDate = SeriesDate
        self.SeriesTime = SeriesTime
        self.PerformingPhysicianName = PerformingPhysicianName
        self.ProtocolName = ProtocolName
        self.SeriesDescription = SeriesDescription
        self.OperatorsName = OperatorsName
        self.BodyPartExamined = BodyPartExamined
        self.PatientPosition = PatientPosition
        self.Laterality = Laterality
        self.NumberOfSeriesRelatedInstances = NumberOfSeriesRelatedInstances
        return

    def __init__(self, dataset, DeSeriesUID):
        series_info_list = [
            'SeriesInstanceUID',
            'StudyInstanceUID',
            'Modality',
            'SeiresNumber',
            'SeriesDate',
            'SeriesTime',
            'PerformingPhysicianName',
            'ProtocolName',
            'SeriesDescription',
            'OperatorsName',
            'BodyPartExamined',
            'PatientPosition',
            'Laterality']
        list_value = []
        for i, tag in enumerate(series_info_list):
            try:
                list_value.append(str(dataset.data_element(series_info_list[i]).value))
            except:
                list_value.append("")

        self.DeSeriesUID = DeSeriesUID
        self.SeriesInstanceUID = list_value[0]
        self.StudyInstanceUID = list_value[1]
        self.Modality = list_value[2]
        self.SeiresNumber = list_value[3]
        self.SeriesDate = list_value[4]
        self.SeriesTime = list_value[5]
        self.PerformingPhysicianName = list_value[6]
        self.ProtocolName = list_value[7]
        self.SeriesDescription = list_value[8]
        self.OperatorsName = list_value[9]
        self.BodyPartExamined = list_value[10]
        self.PatientPosition = list_value[11]
        self.Laterality = list_value[12]
        self.NumberOfSeriesRelatedInstances = ""


class ImageInfo:
    def __init__(self,
                 SOPInstanceUID,
                 SeriesInstanceUID,
                 DeSOPInstanceUID,
                 InstanceNumber,
                 SOPClassUID,
                 PatientOrientation,
                 ContentDate,
                 ContentTime,
                 ImageType,
                 AcquisitionNumber,
                 AcquisitionDate,
                 AcquisitionTime,
                 ImagesinAcquisition,
                 ImageComments,
                 PresentationLUTShape,
                 SourcePath,
                 AnonymizedPath,
                 ThumbnailPath
                 ):
        self.SOPInstanceUID = SOPInstanceUID
        self.SeriesInstanceUID = SeriesInstanceUID
        self.DeSOPInstanceUID = DeSOPInstanceUID
        self.InstanceNumber = InstanceNumber
        self.SOPClassUID = SOPClassUID
        self.PatientOrientation = PatientOrientation
        self.ContentDate = ContentDate
        self.ContentTime = ContentTime
        self.ImageType = ImageType
        self.AcquisitionNumber = AcquisitionNumber
        self.AcquisitionDate = AcquisitionDate
        self.AcquisitionTime = AcquisitionTime
        self.ImagesinAcquisition = ImagesinAcquisition
        self.ImageComments = ImageComments
        self.PresentationLUTShape = PresentationLUTShape
        self.SourcePath = SourcePath
        self.AnonymizedPath = AnonymizedPath
        self.ThumbnailPath = ThumbnailPath
        return

    def __init__(self, dataset, DeImageUID, source_path, anonymized_path, ThumbnailPath):
        image_info_list = [
            'SOPInstanceUID',
            'SeriesInstanceUID',
            'InstanceNumber',
            'SOPClassUID',
            'PatientOrientation',
            'ContentDate',
            'ContentTime',
            'ImageType',
            'AcquisitionNumber',
            'AcquisitionDate',
            'AcquisitionTime',
            'ImagesinAcquisition',
            'ImageComments',
            'PresentationLUTShape']
        list_value = []
        for i, tag in enumerate(image_info_list):
            try:
                list_value.append(str(dataset.data_element(image_info_list[i]).value))
            except:
                list_value.append("")

        self.DeSOPInstanceUID = DeImageUID
        self.SOPInstanceUID = list_value[0]
        self.SeriesInstanceUID = list_value[1]
        self.InstanceNumber = list_value[2]
        self.SOPClassUID = list_value[3]
        self.PatientOrientation = list_value[4]
        self.ContentDate = list_value[5]
        self.ContentTime = list_value[6]
        self.ImageType = list_value[7]
        self.AcquisitionNumber = list_value[8]
        self.AcquisitionDate = list_value[9]
        self.AcquisitionTime = list_value[10]
        self.ImagesinAcquisition = list_value[11]
        self.ImageComments = list_value[12]
        self.PresentationLUTShape = list_value[13]
        self.SourcePath = source_path
        self.AnonymizedPath = anonymized_path
        self.ThumbnailPath = ThumbnailPath


class DcmInfo:
    # Dicom classes:
    def __init__(self, patient_info, study_info, series_info, image_info):
        self.PatientInfo = patient_info
        self.StudyInfo = study_info
        self.SeriesInfo = series_info
        self.ImageInfo = image_info
        return
