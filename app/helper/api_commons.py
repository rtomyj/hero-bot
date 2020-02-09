import os

def get_headers():
	print(os.getenv('RIOT_API_KEY'))
	return {
		'Accept-Charset': 'application/x-www-form-urlencoded;charset=UTF-8',
		'X-Riot-Token': os.getenv('RIOT_API_KEY'),
		'Accept-Language': 'en-us'
		}



def parse_username_tokens(usernameTokens):
	username = ''

	for token in usernameTokens:
		username += f'{token} '

	username = username.rstrip()
	urlFriendlyUsername = username.replace(' ', '%20')
	return username, urlFriendlyUsername