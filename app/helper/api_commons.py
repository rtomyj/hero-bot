import os

def get_headers():
	return {
		'Accept-Charset': 'application/x-www-form-urlencoded;charset=UTF-8',
		'X-Riot-Token': os.getenv('RIOT_API_KEY'),
		'Accept-Language': 'en-us'
		}


def parse_username_tokens(username_tokens):
	username = ''

	for token in username_tokens:
		username += f'{token} '

	username = username.rstrip()
	url_friendly_username = username.replace(' ', '%20')
	return username, url_friendly_username
