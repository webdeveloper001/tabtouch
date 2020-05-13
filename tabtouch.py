import scrapy
import requests

from socketIO_client import SocketIO, LoggingNamespace

search_url = "https://www.tabtouch.com.au/racing/hub?date=%s&code=Races&_=%s"
domain = "https://www.tabtouch.com.au/"
venue_api_url = "http://staging.dw.xtradeiom.com/api/venues?filters[venue_types]=%s"
meeting_api = "https://staging.dw.xtradeiom.com/api/meetings/venue/%d?venue_type=%s&meeting_date=%s"

def main():
	socketIO = SocketIO('localhost', 35775)
	venues = requests.get(venue_api_url % "THOROUGHBRED").json()
	print venues
	socketIO.emit('scrapy', venues)

if __name__ == '__main__':
	with SocketIO('localhost', 35775, LoggingNamespace) as socketIO:
	    socketIO.emit('scrapy', 'pppppppp')