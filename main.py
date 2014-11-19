#!/usr/bin/env python
# vim:fileencoding=UTF-8:ts=4:sw=4:sta:et:sts=4:ai
from __future__ import (unicode_literals, division, absolute_import,
                        print_function)

__license__   = 'GPL v3'
__copyright__ = '2011, Kovid Goyal <kovid@kovidgoyal.net>'
__docformat__ = 'restructuredtext en'

if False:
    # This is here to keep my python error checker from complaining about
    # the builtin functions that will be defined by the plugin loading system
    # You do not need this code in your plugins
    get_icons = get_resources = None

from PyQt5.Qt import QDialog, QVBoxLayout, QPushButton, QMessageBox, QLabel

from calibre_plugins.interface_demo.config import prefs
import re,json,urllib2,webbrowser, tempfile

class DemoDialog(QDialog):

    def __init__(self, gui, icon, do_user_config):
        QDialog.__init__(self, gui)
        self.gui = gui
        self.do_user_config = do_user_config

        # The current database shown in the GUI
        # db is an instance of the class LibraryDatabase2 from database.py
        # This class has many, many methods that allow you to do a lot of
        # things.
        self.db = gui.current_db

        self.l = QVBoxLayout()
        self.setLayout(self.l)
        
        self.label = QLabel("No Keyword has been selected yet")
        self.l.addWidget(self.label)

        self.setWindowTitle('Sign Dict Plugin Demo')
        self.setWindowIcon(icon)

        self.conf_button = QPushButton(
                'Click this to enter keyword', self)
        self.conf_button.clicked.connect(self.config)
        self.l.addWidget(self.conf_button)

        self.resize(self.sizeHint())

    
    def config(self):
        self.do_user_config(parent=self)
        # Apply the changes
        a = self.getPlayersForKeyword(prefs['hello_world_msg'])
        self.label.setText("You have entered: " + a)
        

    def getPlayersForKeyword(self,keyword):
        #replace unicode apostrophes and quotation marks in keyword
        keyword = re.sub(ur'([\u2018]|[\u2019])',"'",keyword)
        keyword = re.sub(ur'([\u201D]|[\u201C])',"\"",keyword)
        #clean up keyword
        keyword = re.sub("(\'s|\'d|\.|,|\?|!|;|,|\"|:|\(|\))","",keyword)
        keyword = re.sub("(~ |~|_)"," ",keyword)
        keyword = keyword.strip("'")
        keyword = keyword.strip()
        #grab info from REST API
        if keyword == "":
            return ""
        url = "http://smartsign.imtc.gatech.edu/videos?keywords=" + keyword
        try:
            response = urllib2.urlopen(url)
        except:
            print("unable to connect to url: "+url)
            return ""
        #convert JSON to Python object
        info = json.load(response)
        #pull ids from converted JSON
        ids = []
        for item in info:
            keywords = item["keywords"]
            #default rank for unranked videos
            rank = 999
            for word in keywords:
                if word.find("{") != -1:
                    rank = int(word.strip("{}"))
            ids.append((item["id"],rank))
        #use ids to build a list of embedded players
        players = "<h1>"
        #sort using rank
        ids = sorted(ids,key=lambda id: id[1])
        for i in ids:
            players+='<iframe width="640" height="360" align:right src="http://www.youtube.com/embed/' + i[0] + '?rel=0"> </iframe>'
        print("keyword is: "+keyword)
        print(len(ids))
        players += "</h1>"
        if len(ids)>0:
            f = open(tempfile.gettempdir()+"/temp.html","w")
            f.write(players)
            temp = f.name
            f.close()
            webbrowser.open(temp,2,True)
            return keyword
        else:
            return ""

