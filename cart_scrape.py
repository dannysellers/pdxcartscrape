# coding=utf-8
__author__ = 'danny'
""" Scrapes information about
	individual food carts. To be called by foodcarts.py"""

import requests
import bs4
import re
import csv
import os
# import logging

UA = {'User-agent': 'Mozilla/5.0'}


def find_carts(url, boolcsv):
	print 'retrieving', url
	r = requests.get(url, headers = UA)
	print 'parsing'
	soup = bs4.BeautifulSoup(r.content)

	# all carts are cleanly stored within <div id="content">, handily
	carts = soup.find('div', {'id': 'content'}).findAll('div', recursive=False)

	count = 0
	cartlist = []
	for cart in carts:
		count += 1
		_cart = scrape_cart(cart, boolcsv)
		cartlist.append(_cart)  # creates a list of dicts
		# print('Carts scraped: ' + str(count) + '\n{}'.format([i['cart_name'] for i in cartlist]))

	return cartlist


def getmatch(txt, regexlist, default='N/A'):
	"""
	Tries different regex patterns to parse txt
	:param regexlist: list of regex patterns
	:param default: else return some text, so we can see what wasn't parsed (at all)
	:param txt: text to parse
	:return: match
	"""

	for pattern in regexlist:
		j = re.search(pattern, txt)
		if j:
			return j.group()
	else:
		return default


def scrape_cart(div, boolcsv):
	"""
	:param div: scrapes information from a <div> element about a single cart
	:return: curcart, a dict
	"""
	# if not div.text == u'Next Page\xbb':
	if u'Next Page\xbb' not in div.text:
		title = div.find('a', {'rel': 'bookmark'})
		post = div.find('div', {'class': 'entry-content'})
		try:
			cart_url = title.get('href')

			if u'\u2019' in title.text:  # str() can't deal with u'\u2019', which is a contextual apostrophe
				cart_name = re.sub(u'\u2019', "'", title.text)
			elif u'\xfc' in title.text:  # u'\xfc' is a u with an umlaut, ü
				cart_name = re.sub(u'\xfc', "ü", title.text)
			else:
				cart_name = str(title.text)

			loclist = [re.compile(r'Location:\s</strong>(.+)<br/>'),
					   re.compile(r'Location:\W(\w+\s\w+\sand\s\w+),'),
					   re.compile(r'Location:\S+</strong>(.+)<br/>'),
					   re.compile(r'Location:\s</strong>(.+)<\w+.*<br/>')]

			location = getmatch(str(post.contents[2]), loclist)

			# if location:
			# 	location = location[0]
			# elif re.findall(r'Location:\W(\w+\s\w+\sand\s\w+),', unicode(post.text)):
			# 	location = re.findall(r'Location:\W(\w+\s\w+\sand\s\w+),', unicode(post.text))[0]
			# elif re.findall(r'Location:\S+</strong>(.+)<br/>', str(post.contents[2])):
			# 	location = re.findall(r'Location:\S+</strong>(.+)<br/>', str(post.contents[2]))[0]
			# else:
			# 	location = ''

			# find 'Location: ', the element prior

		except BaseException, e:
			print type(e), e
			return

		# try:
		# 	story = str(post.contents[6])
		# except BaseException, e:
		# 	print("Couldn't find {} story".format(cart_name))
		# 	story = ''
		# 	print e

		hours = str(repr(post.contents[2].contents[-1]))
		hourlist = [re.compile(r'<strong>Hours:(.*)</strong>'),
					re.compile(r'Hours:\s</strong>(.*)</p>'),
					re.compile(r'Hours:\s</strong></strong>(.*)</p>'),
					re.compile(r'(.*)')]  # this negates all of the above...

		hours = getmatch(hours, hourlist)

		curcart = dict(cart_name = cart_name, cart_url = cart_url, location = location, hours = hours)  #, story = story)
		# print curcart['cart_name']
		if boolcsv:
			return curcart
		else:
			return "<tr><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>".format(
					curcart['cart_url'], curcart['cart_name'], curcart['location'], curcart['hours'])
	else:
		# pagination goes here
		newlink = re.findall(r'<a href="(.*)">.*</a>', str(div))
		find_carts(newlink[0], boolcsv)


def ensure_dir(f):
	""" Create a folder to dump all the files """
	d = os.path.dirname(f)
	if not os.path.exists(d):
		os.mkdir(d)


def tofile (text, fname, boolcsv):
	""" Generic write to file """
	if boolcsv:
		fieldnames = [i for i in text[0]]  # dict at text[0] should contain headers
		_csv = open(fname, 'wb')  # 'w' here? or 'wb'?
		_csvwriter = csv.DictWriter(_csv, fieldnames=fieldnames, delimiter=',', quotechar='"')
		_csvwriter.writeheader()

		for row in text:
			if row:
				try:
					_csvwriter.writerow(row)
				except IOError, e:
					print type(e), e
		_csv.close()
	else:
		try:
			f = open(fname, 'w')
			f.write(text)
		except IOError, e:
			print(type(e), e)
			# sys.exit('Could not open file: ' + fname)
		f.close()


def main(url, boolcsv):
	filename = str(re.findall(r'/location/*/\S+/(\S+)/$', url)[0])
	folder = 'carts/'
	ensure_dir(folder)  # puts the location files into their own folder

	if boolcsv:
		filename += '.csv'
		# print('CSV selected')
	elif not boolcsv:
		filename += '.html'
		# print('HTML selected')
	else:
		filename += '.csv'  # default to csv for now

	pod_carts = find_carts(url, boolcsv)
	tofile(pod_carts, folder + filename, boolcsv)


if __name__ == '__main__':
	# URL = 'http://www.foodcartsportland.com/category/location/southeast-portland-location/se-13th-and-lexington/'
	URL = 'http://www.foodcartsportland.com/category/location/southeast-portland-location/cartlandia/'
	# URL = 'http://www.foodcartsportland.com/category/location/north-portland-location/n-killingsworth-and-maryland/'
	main(URL, True)