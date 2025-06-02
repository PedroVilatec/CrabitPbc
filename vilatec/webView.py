#sudo apt-get install python3-pyqt5.qtwebkit
#!/usr/bin/python
# -*- coding: utf-8 -*-
 
import PyQt5
from PyQt5.QtCore import QUrl, Qt, QTimer
from PyQt5.QtWidgets import QApplication, QWidget 
from PyQt5.QtWebKitWidgets import QWebView , QWebPage
from PyQt5.QtWebKit import QWebSettings
from PyQt5.QtNetwork import *
import sys
from optparse import OptionParser
 
 
class MyBrowser(QWebPage):
	''' Settings for the browser.'''
 
	def userAgentForUrl(self, url):
		''' Returns a User Agent that will be seen by the website. '''
		return "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36"
 
class Browser(QWebView):
	def __init__(self):
		# QWebView
		self.view = QWebView.__init__(self)
		#self.view.setPage(MyBrowser())
		self.setWindowTitle('Mcc - Modulo de controle e comando')
		self.setWindowFlags(Qt.WindowStaysOnTopHint)
		self.titleChanged.connect(self.adjustTitle)
		#super(Browser).connect(self.ui.webView,QtCore.SIGNAL("titleChanged (const QString&)"), self.adjustTitle)
		self.initUI()
 
	def load(self,url):  
		self.setUrl(QUrl(url)) 
 
	def adjustTitle(self):
		self.setWindowTitle(self.title())
 
	def disableJS(self):
		settings = QWebSettings.globalSettings()
		settings.setAttribute(QWebSettings.JavascriptEnabled, False)
		
	def keyPressEvent(self, event):
		if event.key() == Qt.Key_F5:
				self.reload()

		event.accept()
	def recurring_timer(self):
		self.reload()
		
	def initUI(self):

		self.timer = QTimer()
		self.timer.setInterval(60000 * 60 )
		self.timer.timeout.connect(self.recurring_timer)
		self.timer.start()
		self.show()

		
		
if __name__ == '__main__':
	app = QApplication(sys.argv) 
	view = Browser()
	view.showFullScreen()
	view.load("http://127.0.0.1:8000")
	app.exec_()
	sys.exit(app.exec_())
