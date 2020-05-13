# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

from socketIO_client import SocketIO

class LivedataPipeline(object):
	def open_spider(self, spider):
		self.socketIO = SocketIO('localhost', 35775)
		print('#############################')

	def process_item(self, item, spider):
		self.socketIO.emit('scrapy', item['response'])
		return item
