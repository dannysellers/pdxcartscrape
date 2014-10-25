# from urlparse import urljoin
import bs4
import requests
import csv
# import sys
import re
import cart_scrape
# import logging

BASE_URL = 'http://www.foodcartsportland.com/'
user_agent = {'User-agent': 'Mozilla/5.0'}


def prephtml(bhead):
	"""	Prepares HTML for resulting page (jQuery?)
	:param bhead: Boolean = printing head vs. footer of the page
	:return: String which is either head or foot
	"""
	if bhead:
		# if we're working on the head, print the start of the page
		head = """
<!DOCTYPE html>
<html>
<head>
	<title>Title</title>
</head>
<body>
<table border="1" style="width:80%">
<tr>
	<th>source_url</th>
	<th>subject</th>
	<th>body</th>
	<th>datetime</th>
</tr>"""  # return html header
		return head
	else:
		# otherwise, return the ending
		foot = """</table>
</body></html>"""
		return foot


def scrape_list():
	""" Scrape location list <ul> for further investigation
	**List ("Locations")** -> Locations (e.g. "Downtown") -> Neighborhoods (e.g. "Hillsdale Food Park") """

	try:
		r = requests.get(BASE_URL, headers = user_agent)
		soup = bs4.BeautifulSoup(r.content, from_encoding='utf-8')
		print("Status code: " + str(r.status_code))  # + "\nGot: " + soup.title.text)
	except requests.ConnectionError, e:
		print(e)
		quit(1)
		# sys.exit(1)

	locationul = soup.find('a', {'href': BASE_URL + 'category/location/'}).next_sibling.next_sibling
	nhlist = [i for i in locationul]
	# podlist = []
	# for pod in nhlist[1::2]:  # 0, 2, 4, etc are just linebreaks
	# 	namelist = re.findall(r'<a href=".*">(.*)</a>', str(pod))
	# 	linklist = re.findall(r'<a href="(.+/)"', str(pod))
	# 	podlist.append(zip(namelist, linklist))
	# return podlist  # [(name1, link1), (name2, link2)...]

	newlist = []
	newdict = {}
	for pod in nhlist[1::2]:
		podlist = re.findall(r'<a href=".*">(.*)</a>', str(pod))
		linklist = re.findall(r'<a href="(.+/)"', str(pod))
		newlist.append(zip(podlist, linklist))

	# return {x: y for x, y in newlist}
	for pod in newlist:
		for cart in pod:
			newdict[cart[0]] = cart[1]
	return newdict


def tofile(text, filename, boolhtml):
	"""	Prints text to filename
	:param text: text to print
	:param filename: the filename (plus extension) to print to
	:return: Success bool, file
	"""
	if boolhtml:
		try:
			with open(filename, 'w') as f:
				f.write(text)
			f.close()
		except IOError, e:
			print("IO Error: " + str(e))
		# finally:
		# 	f.close()
	else:
		try:
			# fieldnames = [i for i, j in text.items()]
			fieldnames = ['cart', 'url']
			_csv = open(filename, 'wb')

			csvwriter = csv.DictWriter(_csv, delimiter=',', fieldnames=fieldnames, quotechar='"')
			csvwriter.writerow(dict((fn, fn) for fn in fieldnames))
			# csvwriter.writerow(fieldnames)

			# [rowdict.get(key, self.restval) for key in self.fieldnames]

			for key, value in text.iteritems():
				csvwriter.writerow(key, value)
			_csv.close()
		except IOError, e:
			print("IO Error: " + str(e))
		# finally:
		# 	_csv.close()


def main(boolhtml):
	"""	Orchestrates scraping and printing
	:return: Success bool
	"""
	if boolhtml:
		site = [prephtml(True), scrape_list(), prephtml(False)]
		s = ''.join(site)
		tofile(s, 'foodcarts.html', True)
	elif not boolhtml:
		# tofile(scrape_list(), 'carts.csv', False)

		cartdict = scrape_list()
		# tofile(cartdict, 'carts.csv', False)
		newdict = {}
		for i, j in cartdict.iteritems():
			cart_scrape.main(j, True)  # yields .csvs of each pod
			# thing = cart_scrape.find_carts(j, True)  # returns dicts
			pass

		# tofile(thing, 'carts.csv', False)


def menu(title, optionlist):
	print(30 * '-')
	print('  {}'.format(title.upper()))
	print(30 * '-')
	for num, option in enumerate(optionlist):
		print("{}. {}".format(num + 1, option))

	_is_valid = 0
	while not _is_valid:
		try:
			choice = int(raw_input('Enter your choice [1-{}]: '.format(len(optionlist))))
			_is_valid = 1  # break the loop
		except ValueError, e:
			print("'%s' is not a valid integer." % e.args[0].split(": ")[1])

	if choice == 1:
		print("Scraping site...")
		main(False)
	elif choice == 2:
		print("Choose location:")
		locations = [i for i, j in scrape_list()]
		print locations
		# parse locations?
		# invoke cart_scrape on selected pod


if __name__ == '__main__':
	main(False)
	# menu("PDX food cart scraper", ["Scrape www.foodcartsportland.com", "Scrape individual cart pod"])