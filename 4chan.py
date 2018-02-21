from bs4 import BeautifulSoup
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait # available since 2.4.0
from selenium.webdriver.support import expected_conditions as EC # available since 2.26.0
from selenium.webdriver.common.keys import Keys
from selenium.webdriver import ActionChains
from selenium.webdriver.firefox.options import Options
import datetime
import unicodedata
import time

class thread:

	def __init__(self, driver, url):
		self.url = url
		self.driver = driver
		self.replies = []
		self.staleCounter = 0

	def __str__(self):
		return self.url

	def __eq__(self, other):
		if (self.url == other.url):
			return True
		else:
			return False

	def __hash__(self):
		return hash(self.url)

	def scrapeThread(self, windowNum):
		#Start by updating the thread
		self.driver.switch_to_window(self.driver.window_handles[windowNum])
		#Test to see if thread is archived or not
		try:
			if self.driver.find_element_by_class_name("tu-error").text == "This thread is archived":
				self.staleCounter = 30
		except:
			pass

		try:
			self.driver.find_element_by_xpath("//*[@id='delform']/div[1]/div[2]/a[4]").click()
		except:
			self.staleCounter = 30

		WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "desktop")))

		soup = BeautifulSoup(self.driver.page_source, 'html.parser')

		replies = soup.findAll(class_="postMessage")

		#Clean up the HTML from soup
		cleanReplies = []
		for reply in replies:
			cleanReplies.append(unicodedata.normalize('NFKD', reply.text).encode('ascii','ignore') + "\n")

		#If self.replies hasn't been intialized yet with a list
		if(len(self.replies) == 0):
			self.replies = cleanReplies

		#If statement to see if thread has been updated recently
		if (cleanReplies[-1] == self.replies[-1]):
			self.staleCounter += 1
		else:
			self.staleCounter = 0
		#print(self.staleCounter)

		#Add only replies that are new
		self.replies = self.replies + newElementsInList(self.replies, cleanReplies)

	def writeToLog(self):
		#The current date
		now = datetime.datetime.now()

		folder = "BIZlogs-" + str(now.month) + "-" + str(now.day) + "-" + str(now.year)

		#Create new folder for the logs named after the days date
		if not os.path.exists(folder):
			os.makedirs(folder)


		file = open("/Users/georgebenz/Desktop/BitVestor/" + folder + "/" + self.url.replace("/", "-") + ".txt", "w")
		file.writelines(self.replies)
		file.close()

class threadsClass:

	def __init__(self, driver):
		self.driver = driver
		self.threadList = self.initialThreads()
		self.oldthreads = []

	def __str__(self):
		for threads in threadList:
			return threads.replies[0]

	def initialThreads(self):
		#Go to URL of BIZ board
		self.driver.get("https://boards.4chan.org/biz/catalog")

		WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "desktop")))

		soup = BeautifulSoup(self.driver.page_source, 'html.parser')

		links = soup.findAll(class_="thread")

		threads = []
		for URLs in links:
			threads.append(thread(self.driver, unicodedata.normalize('NFKD', URLs.get('id').replace("thread-","")).encode('ascii','ignore')))

		del threads[:2]

		return threads

	def updateThreadsCatalog(self):
		#Goes to inital page and re gets all the links
		self.driver.switch_to_window(self.driver.window_handles[0])
		self.driver.find_element_by_xpath("//*[@id='content']/span[1]/span[4]/a").click()
		WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "desktop")))

		soup = BeautifulSoup(self.driver.page_source, 'html.parser')

		links = soup.findAll(class_="thread")

		threads = []
		for URLs in links:
			threads.append(thread(self.driver, unicodedata.normalize('NFKD', URLs.get('id').replace("thread-","")).encode('ascii','ignore')))

		del threads[:2]
		
		newThreads = newElementsInList(self.threadList, threads)
		self.openNewThreads(newThreads)
		self.threadList = self.threadList + newThreads

	def openNewThreads(self, threads):
		for thread in threads:
			#time.sleep(10000)
			self.driver.switch_to_window(self.driver.window_handles[-1])
			WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "desktop")))
			print(thread.url)
			self.driver.execute_script("window.open('https://boards.4chan.org/biz/thread/" + thread.url +"');")

	def crawlThreads(self):
		x = 5
		while(x != 0):
			self.updateThreadsCatalog()
			for index, thread in enumerate(self.threadList):
				#Checks to see if the thread hasn't been updated in 20 ticks
				print(thread.staleCounter)
				if (thread.staleCounter > 20):
					print("ARCHIVED")
					thread.writeToLog()
					self.threadList.remove(thread)
					self.driver.switch_to_window(self.driver.window_handles[index + 1])
					self.driver.close()
				else:
					thread.scrapeThread(index + 1)

def difference(li1, li2):
	"""returns the difference of two lists"""
	li_dif = [i for i in li1 + li2 if i not in li1 or i not in li2]
    	return li_dif

def newElementsInList(li1, li2):
	li3 = list(set(li1).intersection(set(li2)))
	dif1 = difference(li1, li2)
	dif2 = difference(li1, dif1)
	return difference(dif2, li3)

def main():
	#Create a new instance of the Firefox driver
	options = Options()
	options.set_preference("browser.link.open_newwindow", 3)
	options.set_preference("dom.popup_maximum", 300)
	options.set_preference("privacy.popups.showBrowserMessage", "false")
	driver = webdriver.Firefox(firefox_options = options)


	test = threadsClass(driver)
	test.openNewThreads(test.threadList)
	test.crawlThreads()

main()