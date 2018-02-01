from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait # available since 2.4.0
from selenium.webdriver.support import expected_conditions as EC # available since 2.26.0

def loginDiscord(driver):
	emailKey = "gbenz@bowdoin.edu"
	passwordKey = "george7george"
	
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

	passwordElement.submit()

def discordGroupSelect(driver, group):
	#Dictionary of all the URLS
	URLs = {"CL_chat" : "https://discordapp.com/channels/390595553228226570/391006848633012254", "CL_member-chat" : "https://discordapp.com/channels/390595553228226570/405100274945097738", "SS_members-chat" : "https://discordapp.com/channels/393474769992810496/393518977512374293", "XBY_trading" : "https://discordapp.com/channels/388279933102718976/388338374416662528"}
	
	#Go to the URL
	driver.get(URLs[group])


def main():
	#Create a new instance of the FireFox driver
	driver = webdriver.Firefox()

	loginDiscord(driver)

	#Wait for login process
	WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "guilds-wrapper")))

	#Select a chat
	discordGroupSelect(driver, "CL_member-chat")
	
	#Create a soup of the page
	soup = BeautifulSoup(driver.page_source, 'html.parser')
	print(soup.prettify())

		
main()