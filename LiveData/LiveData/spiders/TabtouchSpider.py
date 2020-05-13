import scrapy
import json

import datetime
from datetime import timedelta
import time

from LiveData.items import LivedataItem

class TabtouchSpider(scrapy.Spider):
	name = "tabtouch"
	search_url = "https://www.tabtouch.com.au/racing/hub?date=%s&code=Races&_=%s"
	domain = "https://www.tabtouch.com.au/"
	venue_api_url = "http://staging.dw.xtradeiom.com/api/venues?filters[venue_types]=%s"
	meeting_api = "https://staging.dw.xtradeiom.com/api/meetings/venue/%d?venue_type=%s&meeting_date=%s"

	converter = {}

	counter = None;

	def __init__(self):
		self.venues = None

	def start_requests(self):
		yield scrapy.Request(url=self.venue_api_url % "THOROUGHBRED", callback=self.parse_base)

	def parse_base(self, response):
		self.venues = json.loads(response.body)["data"];

		current = datetime.datetime.utcnow() + timedelta(hours=10)
		self.counter = int(time.time())
		yield scrapy.Request(url=self.search_url % (current.strftime('%Y-%m-%d'), self.counter),
			meta={'date': current.strftime('%Y-%m-%d')},
			callback=self.parse)

	def parse(self, response):
		meetings = response.xpath("//table[@id='race-hub-races']//tbody//tr")
		res = []

		for meeting in meetings:
			meeting_res = []
			course = self.validate(meeting.xpath("./td[2]/a/text()"))
			country = "Australia"

			if len(course.split("-")) > 1:
				continue

			venue = self.getVenue(course, country)

			print ([course, country])
			if venue == None:
				venue = self.getVenue(course, country)
				if venue == None:
					course = course.replace("park", "").strip()
					venue = self.getVenue(course, country)

			if venue != None:
				meeting_res = {
					"events": [], 
					"status": "CLOSED",
					"meeting_date": response.meta['date'],
					"provider_id": 1,
					"venue_id": venue['venue_id'],
					"venue_itsp_codes": [tp["itsp_code"] for tp in venue["itsp_codes"].values()],
					"venue_name": venue["name"],
					"venue_type": venue["venue_type"]
				}
			else:
				print "============== new venue =============="
				print course, country, response.meta['date']
				print "============================"
				continue

			race_closes = []
			for idx in range(1, 13):
				data = self.validate(meeting.xpath("./td[%s]//a/text()" % (idx+2)))
				print data

				if data == "":
					continue

				race_closes.append(False if ":" in data else True)
			meeting_res['events'] = race_closes

			print json.dumps(meeting_res, indent=4)
			res.append(meeting_res)

		item = LivedataItem()
		item['response'] = json.dumps(res, indent=4)
		yield item

		current = datetime.datetime.utcnow() + timedelta(hours=10)
		print ("################# time diff #####################")
		print ("seconds: %s" % (int(time.time()) - self.counter))
		print ("#################################################")
		self.counter = int(time.time())
		yield scrapy.Request(url=self.search_url % (current.strftime('%Y-%m-%d'), self.counter),
			meta={'date': current.strftime('%Y-%m-%d')},
			callback=self.parse, dont_filter=True)

	def getVenue(self, course, country):
		country = country.replace("-", " ")
		country_id = None
		for country_item in self.venues["countries"]:
			country_item = self.venues["countries"][country_item]
			if country_item['name'].lower() == country.lower():
				country_id = country_item['country_id']

		for venue in self.venues["venues"]:
			venue = self.venues["venues"][venue]
			course = course.lower()
			if course in self.converter:
				course = self.converter[course]
			if (venue["name"].lower() == course.lower() or course.lower() in venue["name"].lower()) and \
				int(venue["country_id"]) == country_id:
				return venue

		return None

	def validate(self, xpath_obj):
		try:
			return xpath_obj.extract_first().strip()
		except:
			return ""