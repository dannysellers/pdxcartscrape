# coding=utf-8
__author__ = 'danny'
""" Scrapes information about
	individual food carts. To be called by foodcarts.py"""

import csv

import re
import os
from types import *
import requests
import bs4


UA = {'User-agent': 'Mozilla/5.0'}


class FoodCart():
	def __init__ (self, div):
		"""
		Constructor method for FoodCart object, does nothing besides call and
		parse existing scrape method
		:param div: HTML element containing all information about the cart
		:return: FoodCart object
		"""
		# self.div = div
		self.name = ''
		self.url = ''
		self.location = ''
		self.hours = ''
		self.story = ''
		self.scrape_div(div)  # populates attributes

	# def __repr__ (self):
	# return {'cart_name': self.name, 'cart_url': self.url, 'location': self.location,
	# 			'hours': self.hours, 'story': self.story}

	# @property
	def scrape_div (self, div):
		"""
		Scrapes individual cart information from div
		:return: information for class properties
		"""
		title = div.find('a', {'rel': 'bookmark'})
		post = div.find('div', {'class': 'entry-content'})
		try:
			cart_url = title.get('href')

			if u'\u2019' in title.text:  # str() can't deal with u'\u2019',
				# which is a contextual apostrophe
				cart_name = re.sub(u'\u2019', "'", title.text)
			elif u'\xfc' in title.text:
				cart_name = re.sub(u'\xfc', "ü", title.text)
			else:
				cart_name = str(title.text)

			loclist = [re.compile(r'Location:\s</strong>(.+)<br/>'),
					   re.compile(r'Location:\W(\w+\s\w+\sand\s\w+),'),
					   re.compile(r'Location:\S+</strong>(.+)<br/>'),
					   re.compile(r'Location:\s</strong>(.+)<\w+.*<br/>')]

			location = getmatch(str(post.contents[2]), loclist)

		# find 'Location: ', the element prior

		except AttributeError, e:
			print("Error ({0}): {1}".format(type(e), e))
			return
		except BaseException, e:
			print("I/O error({0}): {1}".format(type(e), e))
			# print type(e), e
			return

		try:
			story = str(post.contents[6])
		except BaseException as e:
			print("Couldn't find {} story".format(cart_name))
			story = ''
			print(e)

		hours = str(repr(post.contents[2].contents[-1]))
		hourlist = [re.compile(r'<strong>Hours:(.*)</strong>'),
					re.compile(r'Hours:\s</strong>(.*)</p>'),
					re.compile(r'Hours:\s</strong></strong>(.*)</p>'),
					re.compile(r'(.*)')]  # this negates all of the above, and may not even work...

		hours = getmatch(hours, hourlist)

		self.name = cart_name
		self.url = cart_url
		self.location = location
		self.hours = hours
		self.story = story

	def __str__(self):
		return "cart_name, {0}, cart_url, {1}, location, {2}, hours, {3}, story, {4}".format(
			self.name, self.url, self.location, self.hours, self.story)


def find_carts (url):
	"""
	Parses cart pod page into list of <div> elements containing individual carts
	:param url: URL of pod page
	:return: List of dicts containing individual cart info
	"""
	print('retrieving ' + url)
	r = requests.get(url, headers = UA)
	print('parsing')
	soup = bs4.BeautifulSoup(r.content)

	# all carts are cleanly stored within <div id="content">
	carts = soup.find('div', {'id': 'content'}).findAll('div', recursive = False)

	page = 1
	cartlist = []
	_cartlist = []

	# checking for any subsequent or previous pages first eliminates an issue with
	# parsing carts[-1], which would just have 'Next' and 'Previous' links

	if 'Next Page' in str(carts[-1]):  # the first page of multiple
		for cart in carts[:-1]:
			_cart = FoodCart(cart)
			# cartlist.append(_cart.scrape_div() if _cart)
			if _cart:
				cartlist.append(_cart)

		page += 1
		# creates an additional list for carts on the next page

		if not re.search(r'page\/\d$', url):
			_cartlist.append(find_carts(url + 'page/{}'.format(page)))
		else:
			page += 1
			_cartlist.append(find_carts(url.rstrip(re.search(r'page/\d$', url).group()) + '/page/{}'.format(page)))
		# extracts items from the list, rather than having nested lists of variable depth
		for _cart in _cartlist:
			cartlist.append(_cart)
		return cartlist
	elif 'Previous Page' in str(carts[-1]) and 'Next Page' not in str(carts[-1]):  # the final page
		for cart in carts[:-1]:
			_cart = FoodCart(cart)
			# cartlist.append(_cart.scrape_div() if _cart.exists)
			if _cart:
				if not isinstance(_cart, list):
					cartlist.append(_cart)
				else:
					cartlist.append()
		return cartlist
	else:  # single page pods, scrape all carts
		for cart in carts:
			_cart = FoodCart(cart)
			if _cart:
				cartlist.append(_cart)
		return cartlist


def getmatch (txt, regexlist, default = 'N/A'):
	"""
	Tries different regex patterns to parse txt
	:param regexlist: List of regex patterns
	:param default: If nothing is found, return indication
	:param txt: Text to search
	:return: Match text
	"""
	for pattern in regexlist:
		j = re.search(pattern, txt)
		if j:
			return j.group()
	else:
		return default


def tofile (list, fname, boolcsv):
	"""
	Writes dicts from list to file, either as CSV or text as HTML
	:param list: List of individual pod dicts
	:param fname: Filename
	:param boolcsv: Parse dicts as is or convert to HTML tags
	:return: Nothing, EOF
	"""
	if boolcsv:
		fname += '.csv'
		assert isinstance(list[0], FoodCart)
		fieldnames = [i for i, j in vars(list[0]).iteritems()]
		assert type(fieldnames) is ListType
		_csv = open(fname, 'w')  # 'w' here? or 'wb'?
		_csvwriter = csv.DictWriter(_csv, fieldnames = fieldnames, delimiter = ',', quotechar = '"')
		_csvwriter.writeheader()

		for cart in list:
			if isinstance(cart, FoodCart):
				try:
					_csvwriter.writerow(dict(vars(cart).iteritems()))
				except IOError, e:
					print type(e), e
				# for i, j in row.iteritems():
			else:
				for _cart in cart:
					try:
						_csvwriter.writerow(dict(vars(_cart).iteritems()))
					except IOError, e:
						print type(e), e

		_csv.close()
	else:
		fname += '.html'
		_text = ''
		for cart in list:
			assert isinstance(cart, FoodCart)
			_text += "<tr><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>".format(
				cart.url, cart.name, cart.location, cart.hours)
		# assert isinstance(cart, dict)
		# _text += "<tr><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>".format(
		# cart['cart_url'], cart['cart_name'], cart['location'], cart['hours'])
		try:
			f = open(fname, 'w')
			f.write(_text)
		except IOError, e:
			print(type(e), e)
		# sys.exit('Could not open file: ' + fname)
		finally:
			f.close()


def ensure_dir (folder):
	""" Create a folder to dump all the files """
	d = os.path.dirname(folder)
	if not os.path.exists(d):
		os.mkdir(d)


def main (url, boolcsv):
	"""
	Scrapes the cart pod information and writes it to file (for standalone operation). When
	called by foodcarts.py, find_carts() may be invoked directly.
	:param url: URL of cart pod location
	:param boolcsv: Whether to yield CSV (True) or HTML (False)
	:return: List of dicts containing cart info
	"""
	folder = 'carts/'
	ensure_dir(folder)  # puts the location files into their own folder
	filename = folder + str(re.findall(r'/location/*/\S+/([\S+$]|[/\S+/page/\d$])', url)[0])

	pod_carts = find_carts(url)
	# pass
	if pod_carts:   # the likelihood of this being False seems low / to have
		# been caught elsewhere. to confirm
		tofile(pod_carts, filename, boolcsv)
	else:
		print("*Error, no result returned*")
		exit(1)


if __name__ == '__main__':
	if len(sys.argv) < 2:  # sys.argv[0] is the name of the script itself
		# url = 'http://www.foodcartsportland.com/category/location/southeast-portland-location/se-13th-and-lexington/'
		# url = 'http://www.foodcartsportland.com/category/location/southeast-portland-location/cartlandia/'
		url = 'http://www.foodcartsportland.com/category/location/southeast-portland-location/se-52nd-and-foster/page/3'
		main(url, True)
	else:
		# regex for sys.argv[1] url
		# search from cart list?
		url = sys.argv[1]
		main(url, True)
