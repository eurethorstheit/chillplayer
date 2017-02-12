#!/usr/bin/env python3
# coding: utf8

import time
import threading
import urllib.request, urllib.error, urllib.parse #Zum Holen der Internetseite
import re
from subprocess import PIPE, Popen, call
import sys, os
import glob # Rückgabe von Ordnerinhalten 
from  time import sleep
from configparser import ConfigParser
import curses
from threading import Thread
import fcntl, select
# Was weiter entwickelt wird seit Version 1

# Runterladen im Hintergrund mit Threading und starten mit Pufferabsicherung wie beim Royalplayer
	# Nötige Funktionen: hole_video_length, video_puffer, starte_video, lade_video
	# Puffer ändern: Restzeitdownloadzeit: ETA oder so aus wget. Gesamtzeit ist gegeben --> einfach 

# Laden des linken und rechten Videos
# manchmal trefen noch Fehler auf: Herausfinden wieso, fixen oder Errorhandling und sagen, Video kann nicht abgespielt werden

class URLS(): 
	def __init__(self,anchor, newest, othermenu):
		self._othermenu = othermenu # 0 für standard, 1 für alternativ -- gerade experimentell, muss noch in die config
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
		Prev = re.search(r"(http.*\.html)(.*Älter)",self._Page)

		Next = re.search(r"(http.*\.html)(.*Neuer)",self._Page)
		if Next != None:
			Next = Next.group(1)
		if Prev != None:
			Prev = Prev.group(1)
		# dieser soll vor dem Umschalten in die config gespeichert werden
		

		Urls = []
		Urls.append(Prev)
		Urls.append(Next)
		
		return Urls

	def hole_video_length_dev(self):
		''' Gibt die Videolänge einer Datei auf der Festplatte zurück (in Sekunden) '''
		p = Popen(['ffmpeg','-i',self.titel], stdout = PIPE, stderr = PIPE, stdin = PIPE)
		out, err = p.communicate()
		err = str(err)
		print(err)
		input("\n…Rohdaten…\n")
		err = re.search(r"(Duration:)(.*)(start)",err)
		if (err != None):
			err = err.group(0)
			#duration ist Liste mit zwei Werten: 0 - Minuten , 1 - Sekunden
			print(err)
			input("\n…Gefiltert…\n")
			duration_min = err.rstrip()[13:].split(',')[0].split('.')[0].split(':')
			duration_sek = int(duration_min[0])*60 + int(duration_min[1])
			return duration_sek


	def hole_video_length(self):
		''' Gibt die Videolänge einer Datei auf der Festplatte zurück (in Sekunden) '''
		p = Popen(['ffmpeg','-i',self.titel], stdout = PIPE, stderr = PIPE, stdin = PIPE)
		out, err = p.communicate()
		err = str(err)
		err = re.search(r"(Duration:)(.*)(start)",err)
		if (err != None):
			err = err.group(0)
			#duration ist Liste mit zwei Werten: 0 - Minuten , 1 - Sekunden
			duration_min = err.rstrip()[13:].split(',')[0].split('.')[0].split(':')
			duration_sek = int(duration_min[0])*60 + int(duration_min[1])
			return duration_sek


	def url_holen():
		''' Diese Funktion gibt holt eine Liste mit URLS, in denen die aktuelle, die vorherige und die nächste URL enthalten ist. Erste Fortschritte siehe test.py'''
		pass

	''' Hiermit hole ich den Titel des aktuellen Videos '''
	def hole_titel(self):
		self.titel = re.search(r"(contentTitle)(.*)(=)(.*)(;)",self._Page)
		if self.titel is not None:
			self.titel = self.titel.group(4)
			self.titel = (self.titel[2:len(self.titel)-1])
			self.titel = 'Videos/'+self.titel
	''' Hiermit fange ich an, das aktuelle Video zu laden '''
	def hole_videolink(self):
		self.videolink = re.search(r"(MOVIE_LOC_PLAIN)(.*)(http.*mp4)",self._Page)
		if self.videolink is not None:
			self.videolink = self.videolink.group(3)
			''' Starte den Ladeprozess '''	
			self.lade_video()		
	
	def hole_liste_vorhandene_videos(self):
		''' Holt die Liste der Videos, die bereits geladen sind '''
		pass

	def lade_video(self):

		if self.DM == 1 : print("Funktion lade_video\tDownload-URL: \n\t"+str(self.videolink))
		if self._othermenu == 0:
			self.ladeprozess = Popen(['wget', '-O',self.titel,'--continue', str(self.videolink)],stdin = PIPE, stderr = PIPE, stdout = PIPE)			
		elif self._othermenu == 1:
			#self.ladeprozess = call(['wget', '-O','Videos/'+self.titel,str(self.videolink)],stdin = PIPE, stderr = PIPE, stdout = PIPE)
			self.ladeprozess = Popen(['wget', '-O',self.titel,'--continue', str(self.videolink)])

	def set_anchor(self,anchor):
		parser.set('videooptions','anchor',anchor)
		datei = open('config.ini','w')
		parser.write(datei)
		datei.close()

	def change_video(self,next_urls = []):
		self.ladeprozess = None
		self.abspielprozess = None
		self.videolink = None
			#	Vor dem Wechsel der URL soll diese als neuer Anker festgelegt werden und in die config.ini geschrieben werden
		self.set_anchor(self._URL)
		self._URL = next_urls
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
		delete_tempfiles = parser.get('videooptions','delete_tempfiles')		
		if (delete_tempfiles == "1"):
			files = glob.glob('Videos/*')
			for f in files:
				os.remove(f)
		exit()

	def show(self):
		''' Das Menue '''
		if self._othermenu == 0:
			os.system("clear")
				# Neuste URL -- Darf nicht weiter auf neustes gedrückt werden
			print('aktuelles Video: '+ "\x1b[01;34m"+str(self.titel)[6:]+"\33[32m")
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
				if self.DM == 1:
					print("aktuelle URL\n\t")
					print(self._URL)
					print("neuste URL\n\t")
					print(self.newest_URL)
					eingabe =  input("Eingabe für weiter…")
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
		
			if (Auswahl == "4") and (self.DM == 1) : 
				''' Test '''
				self.test()
			if (Auswahl == "0"): 
				''' Speichern des letzten Videos, ggf. Videos löschen und beenden '''
				self.Close_Player()
			else:
				self.show()
		if self._othermenu == 1:
			screen = curses.initscr()
			curses.noecho()
			curses.cbreak()
			screen.keypad(1)
			screen.refresh()
			curses.start_color()
			curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLUE)
			curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLACK)


			win = curses.newwin(12, 60, 5, 5)

			win.box()
	
			win.addstr(2, 2, 'aktuelles Video: '+str(self.titel), curses.color_pair(1))
			#win.addstr(3, 2, '----------------------------------------')
			win.addstr(4, 2, 'Benutze die Pfeiltasten')

			win.addstr(6, 2, 'Hoch - Video abspielen')
			win.addstr(7, 2, "Rechts - neueres Video")
			win.addstr(8, 2, "Links - älteres Video")
			win.addstr(10, 2, "q - Player beenden")

			win.refresh()

			c = screen.getch()

			if c == ord('q'):
				print('w gedrückt')
			elif c == curses.KEY_LEFT:
				''' vorheriges, älteres Video '''
				curses.endwin()			
				self.change_video(self.hole_url_prev_next()[0])


			elif c == curses.KEY_RIGHT:
				''' nächstes, neueres Video '''
				curses.endwin()
				if (self._URL != self.newest_URL):		
					self.change_video(self.hole_url_prev_next()[1])
				else:
					win.addstr(2, 2, "keine neueren Folgen verfügbar")
					self.show()

			elif c == curses.KEY_UP:
				''' Spielt das auf der Platte liegende Video ab '''
				curses.endwin()
				self.starte_video()

			elif c == curses.KEY_DOWN:
				curses.endwin()
				self.Close_Player()

			elif c == ord('q'):
				''' Speichern des letzten Videos, ggf. Videos löschen und beenden '''
					# reset funktioniert nicht. Keine Ahnung wieso, im Beispielprogramm gehts
#				consolen_reset = call(['reset'])	
				self.Close_Player()
			curses.endwin()

	def video_puffer(self):
		while self.ladeprozess.poll() == None:
			for line in self.ladeprozess.stderr:
				match = re.search(r"(%.*[KM])(.*)s",str(line))
				if (match != None):
					match = match.group(2)	
#					print(match.rstrip())
#					print("\t\t\tVideo abspielbar in %s Sekunden\r" % str(match.rstrip()))
					sys.stdout.write("\t\t\tVideo wird abgespielt in %s Sekunden\r" % str(match.rstrip()))
					return int(match.rstrip())

	def starte_video(self):
		''' Zuerst Puffern ''' 
		self.video_puffer()
		''' Spiele das Video ab'''
		player = str(parser.get('videooptions','player'))
		if player == "0":
			self.abspielprozess = call(['omxplayer','-o','local','-b', self.titel],stdin = PIPE, stderr = PIPE, stdout = PIPE)
		if player == "1":
			self.abspielprozess = call(['mplayer','-fs', self.titel],stdin = PIPE, stderr = PIPE, stdout = PIPE)
		''' Solange das Video läuft, Füße still halten'''
		while (self.abspielprozess == True):
			pass
		self.show()

	def hole_url_prev_next_fehler(self):
		''' Bei dem ausmarkierten Video wird None für das neuere Video, also für Next zurückgegeben, obwohl es nicht das neuste ist. '''	
							
		# http://www.chilloutzone.net/video/wie-von-der-tarantel-gestochen.html
		Prev = re.search(r"(http.*\.html)(.*Älter)",self._Page)

		Next = re.search(r"(http.*\.html)(.*Neuer)",self._Page)
	#	if Next != None:
	#		Next = Next.group(1)
	#	if Prev != None:
	#		Prev = Prev.group(1)
		# dieser soll vor dem Umschalten in die config gespeichert werden
		

		Urls = []
		Urls.append(Prev)
		Urls.append(Next)
		
		return Urls

	def test(self):
			# nächste und vorherige Video-URL
		print(self.hole_video_length_dev())


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
		eingabe = input("\nWelcher Videoplayer?\n\tBeim Raspberry Pi ist es für gewöhnlich der omxplayer.Möglicherweise ändert sich das je nach Modell auch noch, entsprechend die Option.\n\t\t0 -- omxplayer\n\t\t1 -- mplayer\nEingabe: ")
		parser.set('videooptions','player',eingabe)
		eingabe = input("\nWelche Oberfläche?\n\t0 -- keine Oberfläche\n\t1 -- Curses - in noch sehr experimentellem Zustand\nEingabe: ")
		parser.set('videooptions','othermenu',eingabe)
		eingabe = input("\nTemporäre Videodateien beim Beenden löschen <empfohlen>? \n\t0 -- nein\n\t1 -- ja\nEingabe: ")
		parser.set('videooptions','delete_tempfiles',eingabe)

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

def init_curses():
	''' Initialisieren des alternativen Displays'''
	screen = curses.initscr()
	curses.noecho()
	curses.cbreak()
	screen.keypad(1)


othermenu = int(parser.get('videooptions','othermenu'))

urls = URLS(anchor,newest,othermenu) 

	# Erster Start (Auslagern in startup ?)
urls.DM = int(parser.get('developermode','on'))

urls.hole_titel()
urls.hole_videolink()

	#Schaltet das alternativmenue an

	# Zeigen des Menues (Auslagern in Startup ?)
urls.show()

