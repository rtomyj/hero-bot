import requests
from requests.exceptions import HTTPError
from helper.riot_api_constants import SUMMONER_INFO_URL
from helper.api_commons import get_headers


def get_account_info_using_summoner_name(url_friendly_username):
	try:
		r = requests.get(SUMMONER_INFO_URL.format(url_friendly_username=url_friendly_username), headers=get_headers())
		r.raise_for_status()
		json = r.json()
		return json['accountId']
	except HTTPError as exception:
		print("Error connecting to riot API while trying to fetch account info")
