#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask import Flask, render_template
from flask_script import Manager
from flask_bootstrap import Bootstrap
from flask import send_file
from flask import send_from_directory
from flask_cors import CORS
from flask import url_for
import json
import os
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, request, redirect, url_for
from werkzeug.utils import secure_filename
import random, string
from CuckooDB import CuckooDB, create_app, db

app = create_app()
manager = Manager(app)
bootstrap = Bootstrap(app)
CORS(app)


def get_db():
    dbc = CuckooDB()
    if not dbc.Connect():
        print 'Faild to connect DB.'
        return None
    else:
        print 'DB Connect success!'
        return dbc


@app.route('/')
def index2():
    return render_template('index.html')


@app.route('/view/<imageName>')
def index(imageName):
    imageurl = "http://127.0.0.1:5000/" + imageName
    return render_template('index.html', imageurl=imageurl)

@app.route('/view/series/<seriesNo>')
def indexSeries(seriesNo):
    # seriesNo = 1
    
    urlroot = 'http://127.0.0.1:5000/'
    #get filename from db

    #serve file on web

    files = []
    files.append('1.dcm')
    files.append('2.dcm') 
    #print(imageurl)
    return render_template('index.html', urlroot=urlroot, files=files)

############### Server files ###############
#Serve Specific dcmfiles
@app.route('/dcmfiles/<path:filepath>')
def serveDir(filepath):
    return send_from_directory('dcmfiles', filepath)

#Serve thumbnails
@app.route('/thumbnails/<path:filepath>')
def serveThumbnails(filepath):
    return send_from_directory('thumbnails', filepath)

#Serve translation.json, may have better way?
@app.route('/locales/zh/translation.json')
def transzh():
    return send_file('static/locales/zh/translation.json', attachment_filename='translation.json')

@app.route('/locales/en/translation.json')
def transen():
    return send_file('static/locales/en/translation.json', attachment_filename='translation.json')

@app.route('/user/<name>')
def user(name):
    return render_template('user.html', name=name)

############### All Web URL###############

#for test
@app.route('/view/seriesdir/<seriesNo>')
def indexSeriesDir(seriesNo):
    urlroot = 'http://127.0.0.1:5000/dcmfiles/'
    #get filename from db
    files = []
    files.append('1.dcm')
    files.append('2.dcm')
    files.append('3.dcm') 
    files.append('4.dcm') 
    files.append('5.dcm') 
    files.append('6.dcm')
    files.append('7.dcm')    
    #serve file on web
    return render_template('index.html', urlroot=urlroot, files=files)

#real dwv series panel
@app.route('/seriespanel/<seriesNo>')
def showSeriesPanel(seriesNo):
    urlroot = 'http://127.0.0.1:5000/dcmfiles/'
    #get filepath from db
    dbc = get_db()
    if dbc is None:
        return None
    
    files = dbc.GetSeriesDcmsName(seriesNo)
    # files.append('1.dcm')
    # files.append('2.dcm')
    # files.append('3.dcm') 
    # files.append('4.dcm') 
    # files.append('5.dcm') 
    # files.append('6.dcm')
    # files.append('7.dcm')    
    #serve file on web
    return render_template('SeriesPanel.html', urlroot=urlroot, files=files)

@app.route('/studyList')
def getStudyList():
    dbc = get_db()
    if dbc is None:
        return None
    result = dbc.GetPatientStudyView()        
    # for row in result:
    #     for i in range(result.rowcount):
    #         print row[i]
    return render_template('StudyList.html', studies = result)

@app.route('/studypanel/<studyUID>')
def showStudyPanel(studyUID):
    dbc = get_db()
    if dbc is None:
        return None
    # imageStudyPaths = dbc.GetThumbsByStudyUID(studyUID)
    result = dbc.GetStudyPanelThumbsByStudyUID(studyUID)
    
    #region
    # paths = []
    # for row in imageStudyPaths:
    #     for i in range(imageStudyPaths.rowcount):
    #         try:
    #             path.append(row[i])
    #             print row[i]
    #         except Exception as e:
    #             continue
    #endregion

    # get thumbmail path from studyUID, 
    # relationship between series thumbs and image thumbs design later
    # construct by served path:
    
    # absPaths = []
    # for name in imageStudyPaths[:6]:
    #     p1 =  '../thumbnails/' + name
    #     absPaths.append(p1)
    #     print p1
    
    #先只从dict中导出series的一张缩略图给template
    seriesDict = {}
    for seriesUID in result.keys():
        seriesDict[seriesUID] = '../thumbnails/' + result[seriesUID].pop()
        print seriesDict[seriesUID]

    # transfer paths to template
    return render_template('StudyPanel.html', seriesDict = seriesDict)

def _random_string(self, length = 16):
    return ''.join(random.choice(string.ascii_letters) for m in range(length))
    
uploadDir = '/uploadDir'

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'dcmfile' not in request.files:
            # flash('No file part')
            return redirect(request.url)
        f = request.files['dcmfile']
        filename = _random_string(8) + '.dcm'
        dirPath = os.path.dirname(os.path.abspath(__file__)) 
        filePath = os.path.join(dirPath + uploadDir, filename)
        res = f.save(filePath)
        return redirect(url_for('getStudyList'))

if __name__ == '__main__':
    # manager.run()

    app.run(debug=True)

#region comment
# @app.route('/1.dcm')
# def return_files_tut1():
# 	try:
# 		return send_file('D:/dcms/test_files/1_2_840_113619_2_98_6140_1425970638_0_12_64.dcm', attachment_filename='1_2_840_113619_2_98_6140_1425970638_0_12_64.dcm')
# 	except Exception as e:
# 		return str(e)

# @app.route('/2.dcm')
# def return_files_tut2():
# 	try:
# 		return send_file('D:/dcms/test_files/1_2_840_113619_2_98_6140_1425970638_0_13_64.dcm', attachment_filename='1_2_840_113619_2_98_6140_1425970638_0_13_64.dcm')
# 	except Exception as e:
# 		return str(e)

# @app.route('/file/<filepath>')
# def return_files(filepath):
#     fiename = os.path.basename(filepath)
#     try:
# 		return send_file(filepath, attachment_filename=fiename)
# 	except Exception as e:
# 		return str(e)

# @app.rout('/test/<path>')
# def test(path):
#     retrun url_for('return_files', filepath=path)
#endregion

    