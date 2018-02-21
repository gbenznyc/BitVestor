from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait # available since 2.4.0
from selenium.webdriver.support import expected_conditions as EC # available since 2.26.0
from selenium.webdriver.common.keys import Keys
import datetime
import unicodedata
import time

def loginDiscord(driver):
	emailKey = ""
	passwordKey = ""
	
	#URL
	discordLogin = 'https://discordapp.com/login'

	#Go to the test page URL
	driver.get(discordLogin)

	#Wait until page is fully loaded
	WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "register-email")))

	#Find the email box
	emailElement = driver.find_element_by_id("register-email")
	emailElement.send_keys(emailKey)

	#Find the password box
	passwordElement = driver.find_element_by_id("register-password")
	passwordElement.send_keys(passwordKey)

	#Click login
	passwordElement.send_keys(Keys.RETURN)
	#passwordElement.submit()

def writeToLog(messages, group):
	#The current date
	now = datetime.datetime.now()

	print(messages)

	#Create new file named after the days date
	file = open(group + str(now.month) + "-" + str(now.day) + "-" + str(now.year) + ".txt", "a")
	file.writelines(messages)
	file.close()

def detectNewMessages(driver, group):
	
	#Dictionary of all the URLS
	URLs = {"CL_chat" : "https://discordapp.com/channels/390595553228226570/391006848633012254", "CL_member-chat" : "https://discordapp.com/channels/390595553228226570/405100274945097738", "SS_members-chat" : "https://discordapp.com/channels/393474769992810496/393518977512374293", "XBY_trading" : "https://discordapp.com/channels/388279933102718976/388338374416662528"}
	
	#Go to the URL
	driver.get(URLs[group])

	#Waits until the page has loaded
	WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "messages-wrapper")))
	
	#This loop finds the difference between the last 50 messages 5 seconds apart
	x = 0
	prevMessages = []
	while (x < 10):
		#Soupify html of the page
		soup = BeautifulSoup(driver.page_source, 'html.parser')
	
		#Find all the messages within the HTML
		messages = soup.findAll(class_="markup")

		#Clean up the HTML from soup
		newMessages = []
		for message in messages:
			newMessages.append(unicodedata.normalize('NFKD', message.text).encode('ascii','ignore') + "\n")

		#Write to the log file the difference between the two lists
		prevSet = set(prevMessages)
		newSet = set(newMessages)
		writeToLog(newSet.difference(prevSet), group)

		prevMessages = newMessages
		time.sleep(3)

def main():
	#Create a new instance of the FireFox driver
	driver = webdriver.Firefox()

	#Login
	loginDiscord(driver)

	#Wait for login process
	WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "guilds-wrapper")))
	
	#Join a chat and detect new messages
	detectNewMessages(driver, "CL_chat")
	
main()
