from bs4 import BeautifulSoup 
import urllib
import csv
import pandas as pd
from openpyxl import Workbook 


def main():
	#gathers website to scrape from user
	website = raw_input("Please enter website link: ")
	scrape = urllib.urlopen(website)
	soup = BeautifulSoup(scrape, 'lxml')
	new_file = excel_sheet_downloader(soup)
	relevant_links = summary_link_grabber(new_file)
	summary_scrape(relevant_links, new_file)
	


def excel_sheet_downloader(soup):
	#pulls the relevant CSV/Excel file from Federal Register site
	links = soup.find_all('span', class_= 'other_formats')	
	website_base_name = "https://www.federalregister.gov"
	
	compiled_links = []
	#creates list of all download links
	for sites in links:
		compiled_links.append(sites.a['href'])
	#pulls first link which is the one that contains the CSV file.
	excel_link = compiled_links[0]
	full_website_link = website_base_name + excel_link
	#allows user to choose name of output file
	fileName = raw_input("Please enter name for output sheet (+ .csv): ")
	print("Now downloading %s from the Federal Register..." % fileName)

	#downloads CSV file to current working directory.
	excel_file = urllib.urlretrieve(full_website_link, fileName)
	return fileName

def summary_link_grabber(new_file):
	#reads through downloaded file
	csvFile = pd.read_csv(new_file)
	#pulls summary sites from html_url column
	link_column = csvFile['html_url']
	#converts pandas object into a list
	link_column_list = list(link_column.values.flatten())
	return link_column_list  

def summary_scrape(links, new_file):
	#allows user to input filename of soon to be created excel file
	outputFile = raw_input("Please enter name for output file (+.xlsx): ")
	csvFile = pd.read_csv(new_file)
	#sets up relevant variables
	date_column = csvFile['publication_date']
	date_column = list(date_column.values.flatten())
	title_column = csvFile['title']
	title_column = list(title_column.values.flatten())
	cfr_column = csvFile['citation']
	cfr_column = list(cfr_column.values.flatten())
	
	"""print(date_column)
	print(len(date_column))
	i = 0 
	for site in links:
		print(date_column[i])
		i +=1"""

	#create new excel sheet
	wb = Workbook()
	ws = wb.active
	#append column headers
	ws.append(["Date", "Title/Action", "PL", "Federal Register Page #", "CFR", "RIN", "Content", "Website Link"])
	#set counter for for loop for use with pulling from old excel sheet
	a = 0
	for site in links:
		
		g = date_column[a]
		
		#print("A is now " + str(a))
		#print("date: " + date_column[a])
		scrape = urllib.urlopen(site)
		soup = BeautifulSoup(scrape, 'lxml')
		date = date_column[a]
		title = title_column[a]
		cfr = cfr_column[a]
		summary = soup.find_all('p', id="p-3")
		summary_end = len(summary) -5
		#saves summary without html tags
		summary_string = str(summary)[31: summary_end].encode('utf-8')
		page_number = cfr[6:]
		metadata = soup.find_all('dl', class_="metadata_list ")			
		metadata = str(metadata).split("\\n")
		
		a +=1 
		

		#for use with finding RIN value on the page
		for i, values in enumerate(metadata):
			if '<dt>RIN:</dt>' in values:
				rin = metadata[i+1]
			else:
				rin = '              '
		
		rin = rin[4: len(rin) -5]
		if len(rin) > 9: 
			tag_end= rin.index('>') + 1
			rin = str(rin)
			rin = rin[tag_end: len(rin) - 4]		
		pl = " "

		#appends the data to the excel sheet
		ws.append([g, title, pl, page_number, cfr, rin, summary_string, site])
		
		#increment counter for use in matching website data with excel data 
	wb.save(outputFile)
	
	print("Process Complete. You can now open %s to see the data." % outputFile)
main()