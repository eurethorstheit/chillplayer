#!/usr/bin/env python3
# coding: utf8

import time
import threading
import urllib.request, urllib.error, urllib.parse #Zum Holen der Internetseite
import re
from subprocess import PIPE, Popen, call
import sys, os
from  time import sleep
from configparser import ConfigParser

# Neurerungen: Alles in einer Datei

class URLS(): 
	def __init__(self,anchor, newest):
		self._URL = anchor
		self.newest_URL = newest 		
		self._Page = self.page_holen(self._URL)
		self.titel = "mein Titel"
		self.ladeprozess = None
		self.abspielprozess = None
		self.videolink = None
		self.DM = 0 # Developermode
	def page_holen(self, url): # Herunterladen einer URL
		try:
			resp = urllib.request.urlopen(url)
			contents = resp.read()
			return contents.decode('utf8')
		except urllib.error.HTTPError as error:
			contents = False
			return contents

	def url_testen(self, url): # Pruefen, ob eine URL vorhanden ist
		try:
			resp = urllib.request.urlopen(url)
			contents = True
			return contents
		except urllib.error.HTTPError as error:
			contents = False
			return contents

	def hole_url_prev_next(self):
		''' Holt die nächste und die vorherige Seite als Liste '''	
		Next = re.search(r"(http.*\.html)(.*Älter)",self._Page)

		Prev = re.search(r"(http.*\.html)(.*Neuer)",self._Page)
		if Next != None:
			Next = Next.group(1)
		if Prev != None:
			Prev = Prev.group(1)
		
		Urls = []
		Urls.append(Next)
		Urls.append(Prev)
		return Urls

	def url_holen():
		''' Diese Funktion gibt holt eine Liste mit URLS, in denen die aktuelle, die vorherige und die nächste URL enthalten ist. Erste Fortschritte siehe test.py'''
		pass

	''' Hiermit hole ich den Titel des aktuellen Videos '''
	def hole_titel(self):
		self.titel = re.search(r"(contentTitle)(.*)(=)(.*)(;)",self._Page)
		print("Titel  "+str(self.titel))
		if self.titel is not None:
			self.titel = self.titel.group(4)
			self.titel = (self.titel[2:len(self.titel)-1])

	''' Hiermit fange ich an, das aktuelle Video zu laden '''
	def hole_videolink(self):
		self.videolink = re.search(r"(MOVIE_LOC_PLAIN)(.*)(http.*mp4)",self._Page)
		if self.videolink is not None:
			self.videolink = self.videolink.group(3)
			''' Starte den Ladeprozess '''	
			if os.path.isfile('Videos/'+self.titel) == False:
				self.lade_video()		
	
	def hole_liste_vorhandene_videos(self):
		''' Holt die Liste der Videos, die bereits geladen sind '''
		pass

	def lade_video(self):
		self.ladeprozess = call(['wget', '-O','Videos/'+self.titel,str(self.videolink)])
		''' Error Code 0 tritt auf, wenn alles Ordnungsgemäß herunter geladen wurde'''
		while (self.ladeprozess != 0): 
			pass	

	def change_video(self,next_urls = []):
		self.ladeprozess = None
		self.abspielprozess = None
		self.videolink = None
	
		self._URL = next_urls
		print("ChangeVideoURL"+str(self._URL))
		self._Page = self.page_holen(self._URL)
		self.hole_titel()
		self.hole_videolink()

		self.show()

	def Close_Player(self):
		''' Beenden des Programmes '''
		parser.set('videooptions','anchor',self._URL)
		parser.set('videooptions','newest',"")				
		datei = open('config.ini','w')
		parser.write(datei)
		datei.close()
		exit()

	def show(self):
		''' Das Menue '''
		os.system("clear")
			# Neuste URL -- Darf nicht weiter auf neustes gedrückt werden
		print('aktuelles Video: '+ "\x1b[01;34m"+str(self.titel)+"\33[32m")
		print('----------------------------------------')
		print('1\t-\tVideo abspielen')
		print('2\t-\tneueres Video')
		print('3\t-\tälteres Video')
		if self.DM == 1 : print('4\t-\tTestfunktion')
		print('0\t-\tPlayer beenden')
		print('----------------------------------------')
		Auswahl = input("\tBitte eine Auswahl treffen: ") 
		if (Auswahl == "1") : 
			''' Spielt das auf der Platte liegende Video ab '''
			self.starte_video()
		if (Auswahl == "2") : 
			''' nächstes, neueres Video '''
			if (self._URL != self.newest_URL):		
				self.change_video(self.hole_url_prev_next()[1])
			else:
				os.system("clear")				
				sys.stdout.write("\t\x1b[01;34mkeine Neueren Folgen verfügbar\33[32m")
				eingabe = input("\t\tReturn = Zurück zum Menue")
				self.show()
		if (Auswahl == "3") : 
			''' vorheriges, älteres Video '''
			self.change_video(self.hole_url_prev_next()[0])
		
		if (Auswahl == "4") and (DM == 1) : 
			''' Test '''
			self.test()
		if (Auswahl == "0"): 
			''' Speichern des letzten Videos, ggf. Videos löschen und beenden '''
			self.Close_Player()
		else:
			self.show()

	def starte_video(self):
		''' Spiele das Video ab'''
		player = str(parser.get('videooptions','player'))
		if player == "0":
			self.abspielprozess = call(['omxplayer','-o','local','-b', 'Videos/'+self.titel])
		if player == "1":
			self.abspielprozess = call(['mplayer','-fs', 'Videos/'+self.titel])
		''' Solange das Video läuft, Füße still halten'''
		while (self.abspielprozess == True):
			pass
		self.show()
	def test(self):
		print(self.hole_url_prev_next())
#		print(self.hole_url_prev_next()[1])

class player_startup():

	def page_holen(self, url): # Herunterladen einer URL
		try:
			resp = urllib.request.urlopen(url)
			contents = resp.read()
			return contents.decode('utf8')
		except urllib.error.HTTPError as error:
			contents = False
			return contents

	def hole_neuste_url(self):
		_startpage = self.page_holen('http://www.chilloutzone.net/')
		first_match = re.search(r"(h2.*)(/video.*html)(.*h2)",_startpage)
		if (first_match != None):
			first_match = first_match.group(2)
			newesturl = "http://www.chilloutzone.net"+first_match
		return newesturl		
	def first_start(self):
		print("\n----------------------------------\nDas ist die erste Verwendung des Players. Zunächst müssen einige Einstellungen vorgenommen werden, welche in der Datei config.ini gespeichert und jederzeit verändert werden können\n----------------------------------\n")
		parser.add_section('developermode')
		parser.add_section('videooptions')
		eingabe = input("\nDevelopermode an ? Wenn ja, gibt es zusätzliche Auswahlmöglichkeiten, die aber für die normale Anwendung nur störend sind\n \t0 -- nein\n\t1 -- ja\n Eingabe: ")
		parser.set('developermode','on',str(eingabe))
		eingabe = input("\n\tWelcher Videoplayer?\n\tBeim Raspberry Pi ist es für gewöhnlich der omxplayer.Möglicherweise ändert sich das je nach Modell auch noch, entsprechend die Option.\n\t\t0 -- omxplayer\n\t\t1 -- mplayer\nEingabe: ")
		parser.set('videooptions','player',eingabe)
		datei = open('config.ini','w')
		parser.write(datei)
		datei.close()
		datei = open('config.ini','w')
		parser.write(datei)
		input(" Die Einstellungen sind abgeschlossen. \nDie Optionen werden in der Datei config.ini gespeichert und können jederzeit manuell geändert werden. Lösche die Datei config.ini, wenn sich das Startmenü wiederholen soll.\n\tEingabetaste für weiter…")
		print("Laden des Menues…")
		parser.read('config.ini')

	#Erstelle Objekte für den Start und die Konfigurationsdatei
startup = player_startup()
parser = ConfigParser()

	# Neustes Video als Stopper für die Menüführung holen
newest = startup.hole_neuste_url()

if os.path.isfile("config.ini") == False: 
	startup.first_start()
	parser.set('videooptions','anchor',newest)
	datei = open('config.ini','w')
	parser.write(datei)
	datei.close()
	parser.read('config.ini')
		# Starturl (Anker) und neuste URL fallen in diesem Fall zusammen.
	anchor = newest
		# Prüfen, ob Videos-Ordner existiert und erstellen, falls nicht der Fall
	if not os.path.exists('Videos'):
		os.makedirs('Videos')
	
else:
	parser.read('config.ini')
	anchor = str(parser.get('videooptions','anchor'))
	parser.read('config.ini')
	# Objekt der Quellenverarbeitung

urls = URLS(anchor,newest) 

	# Erster Start (Auslagern in startup ?)
urls.DM = int(parser.get('developermode','on'))
urls.hole_titel()
urls.hole_videolink()
	# Zeigen des Menues (Auslagern in Startup ?)
urls.show()

