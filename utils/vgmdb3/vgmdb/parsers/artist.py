import bs4

from . import utils

fetch_url = lambda id: utils.url_info_page('artist', id)
fetch_page = lambda id: utils.fetch_info_page('artist', id)

def parse_page(html_source):
	artist_info = {}
	soup = bs4.BeautifulSoup(html_source, features='html.parser')
	soup_profile = soup.find(id='innermain')
	if soup_profile == None:
		return None	# info not found

	spans = soup_profile.find_all('span', recursive=False)
	soup_name = spans[1]
	artist_info['name'] = soup_name.string.strip()
	artist_info['type'] = 'Individual'
	if len(spans)>2 and spans[2]['class'] and 'time' in spans[2]['class']:   # artist type (unit)
		soup_type = spans[2]
		artist_type = utils.parse_string(soup_type)
		if 'Alias' in artist_type:
			artist_info['type'] = 'Alias'
			if 'of' in artist_type:
				alias_info = {}
				soup_alias_link = soup_type.a
				if soup_alias_link:
					alias_info['link'] = utils.trim_absolute(soup_alias_link['href'])
					alias_info['names'] = utils.parse_names(soup_alias_link)
				else:
					left_index = artist_type.find('of')
					if left_index > 0:
						name = artist_type[left_index+3:-1]
						alias_info['names'] = {'en': name}
				artist_info['alias_of'] = alias_info
		else:
			if len(artist_type) > 0 and artist_type[0] == '(':
				artist_type = artist_type[1:]
			if len(artist_type) > 0 and artist_type[-1] == ')':
				artist_type = artist_type[:-1]
			artist_info['type'] = artist_type
	if len(spans)>2 and spans[2].string and 'deceased' in spans[2].string:
		artist_info['deathdate'] = utils.parse_date_time(spans[2].string[10:])

	soup_profile = soup_profile.div
	(soup_profile_left,soup_profile_right) = soup_profile.find_all('div', recursive=False, limit=2)
	soup_right_column = soup.find(id='rightcolumn')

	# Determine sex
	soup_profile_sex_image = soup_profile_left.img
	if soup_profile_sex_image['src'] == '/db/icons/male.png':
		artist_info['sex'] = 'male'
	elif soup_profile_sex_image['src'] == '/db/icons/female.png':
		artist_info['sex'] = 'female'

	# Parse japanese name
	japan_name = soup_profile_left.span.string.strip()
	artist_info.update(_parse_full_name(japan_name))

	# Parse picture
	soup_picture = soup_profile_left.div.a
	if soup_picture and soup_picture.img:
		artist_info['picture_full'] = utils.force_absolute(soup_picture['href'])
		artist_info['picture_small'] = utils.force_absolute(soup_picture.img['src'])

	# Parse info
	artist_info['info'] = _parse_profile_info(soup_profile_left)
	artist_info.update(_promote_profile_info(artist_info['info']))

	# Parse Notes
	soup_notes = soup_profile_right.div.find_next_sibling('div').div
	artist_info['notes'] = utils.parse_string(soup_notes).strip()

	# Parse Discography
	disco_container = soup_profile_right.find(id='albumlist')
	soup_disco_div = disco_container.find(id='discotable')
	if soup_disco_div:
		artist_info['discography'] = utils.parse_discography(soup_disco_div.find('table'), 'roles')
	else:
		artist_info['discography'] = []
	soup_featured_div = disco_container.find(id='featuredtable')
	if soup_featured_div:
		artist_info['featured_on'] = utils.parse_discography(soup_featured_div.find('table'), 'roles')
	else:
		artist_info['featured_on'] = []

	# Parse for Websites
	soup_divs = soup_right_column.find_all('div', recursive=False)
	if soup_divs[0].div and soup_divs[0].div.h3 and soup_divs[0].div.h3.string == 'Websites':
		artist_info['websites'] = _parse_websites(soup_divs[1].div)
	else:
		artist_info['websites'] = {}
	artist_info['meta'] = utils.parse_meta(soup_divs[-1].div)

	# Parse for twitter handle
	twitters = []
	soup_links = soup_right_column.find_all('a')
	for soup_link in soup_links:
		if soup_link.text == "Twitter":
			index = soup_link['href'].find("twitter.com")
			if index > -1:
				index = soup_link['href'].find("/", index)
				twitters.append(soup_link['href'][index+1:])

	if len(twitters) > 0:
		artist_info['twitter_names'] = twitters


	return artist_info

def _parse_full_name(japan_name):
	name_data = {}
	if len(japan_name) > 0:
		if japan_name.find('(') >= 0:
			(orig_name, gana_name) = japan_name.split('(',1)
			gana_name = gana_name[0:-1]	# strip )
			orig_name = orig_name.strip()
			gana_name = gana_name.strip()
			name_data['name_real'] = orig_name
			name_data['name_trans'] = gana_name
		else:
			name_data['name_real'] = japan_name
	return name_data

def _parse_profile_info(soup_profile_left):
	ret = {}
	for soup_item in soup_profile_left.find_all('div', recursive=False)[1:]:
		item_name = soup_item.b.string.strip()
		item_list = []
		list_item_pre = soup_item.br
		while list_item_pre:
			soup_item_data = list_item_pre.next
			# plain text entry in the section
			if isinstance(soup_item_data, bs4.NavigableString):
				texts = []
				while isinstance(soup_item_data, bs4.NavigableString):
					texts.append(str(soup_item_data))
					soup_item_data = soup_item_data.next
				text = ''.join(texts).strip()
				if len(text) > 0:
					item_list.append(text)
			# link entry
			if isinstance(soup_item_data, bs4.Tag):
				item_data = {}
				if soup_item_data.name == 'a':
					item_data['link'] = utils.trim_absolute(soup_item_data['href'])
					item_data['names'] = {"en":str(soup_item_data.string)}
					pic_tag = soup_item_data.find_next_sibling('img')
					if pic_tag:
						if pic_tag['src'] == 'http://media.vgmdb.net/img/owner.gif':
							item_data['owner'] = 'true'
					soup_names = soup_item_data.find_all('span', "artistname")
					if len(soup_names) > 0:
						del item_data['names']
						names = {}
						for soup_name in soup_names:
							lang = soup_name['lang']
							name = str(soup_name.string)
							names[lang] = name
						item_data['names'] = names
					item_list.append(item_data)
				# rating stars
				if soup_item_data.name == 'div' and \
				  soup_item_data.has_attr('class') and \
				  'star' in soup_item_data['class']:
					total_stars = soup_item.find_all('div', 'star')
					stars = soup_item.find_all('div', 'star_on')
					item_list.append('%s/%s'%(len(stars),len(total_stars)))
					soup_votes = soup_item.find_all('div')[-1]
					ret['Album Votes'] = soup_votes.contents[0].string + \
					  soup_votes.contents[1] + \
					  soup_votes.contents[2].string + \
					  soup_votes.contents[3]
					ret['Album Votes'] = str(ret['Album Votes'])
				if soup_item_data.name == 'span' and \
				  soup_item_data.has_attr('class') and \
				  'time' in soup_item_data['class']:
					if soup_item_data.next_sibling:
						item_list.append(str(soup_item_data.string) + \
						                 soup_item_data.next_sibling)


			list_item_pre = list_item_pre.find_next_sibling('br')
		if len(item_list) == 0:
			continue
		# what item headings indicate people, and should have names
		people_lists = ['Aliases', 'Former Members', 'Members', 'Units', 'Organizations', 'Variations']
		# detect if there is a single text item
		if len(item_list) == 1 and isinstance(item_list[0], str) and \
		   item_name not in people_lists:
			ret[item_name] = item_list[0]
		else:
			ret[item_name] = item_list
		# make sure all the items from people have names
		for people_type in people_lists:
			if people_type not in ret:
				continue
			proper = []
			for improper in ret[people_type]:
				if isinstance(improper,str):
					langcode = 'en'
					if not utils.is_english(improper):
						langcode = 'ja'
					proper.append({'names': {langcode:improper}})
				else:
					proper.append(improper)
			ret[people_type] = proper
	return ret

def _promote_profile_info(profile_info):
	artist_info = {}
	if 'Birthdate' in profile_info:
		artist_info['birthdate'] = utils.parse_date_time(profile_info['Birthdate']);
	if 'Birthplace' in profile_info:
		artist_info['birthplace'] = profile_info['Birthplace'];
	promote_types = {'aliases':'Aliases',
	                 'members':'Members',
	                 'units':'Units',
	                 'organizations':'Organizations'}
	for promote_key, info_key in list(promote_types.items()):
		if info_key not in profile_info:
			continue
		artist_info[promote_key] = profile_info[info_key]
	return artist_info

def _parse_websites(soup_websites):
	""" Given an array of divs containing website information """
	sites = {}
	for soup_category in soup_websites.find_all('div', recursive=False):
		category = str(soup_category.b.string)
		soup_links = soup_category.find_all('a', recursive=False)
		links = []
		for soup_link in soup_links:
			link = soup_link['href']
			name = str(soup_link.string)
			if link[0:9] == '/redirect':
				link = utils.strip_redirect(link)
			links.append({"link":link,"name":name})
		sites[category] = links
	return sites
