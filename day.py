import dateutil.parser
from broadcast import Broadcast

class Day(object):

	def __init__(self, day):
		self.date = dateutil.parser.parse(day['dateISO'])
		self.broadcasts = []
		tracknumber = 0
		for broadcast in day['broadcasts']:
			tracknumber += 1
			self.broadcasts.append(Broadcast(
				href=broadcast['href'],
				station=broadcast['station'],
				broadcastDay=broadcast['broadcastDay'],
				entity=broadcast['entity'],
				id=broadcast['id'],
				program=broadcast['program'],
				programKey=broadcast['programKey'],
				programTitle=broadcast['programTitle'],
				title=broadcast['title'],
				subtitle=broadcast['subtitle'],
				ressort=broadcast['ressort'],
				state=broadcast['state'],
				isOnDemand=broadcast['isOnDemand'],
				isGeoProtected=broadcast['isGeoProtected'],
				start=broadcast['startISO'],
				end=broadcast['endISO'],
				scheduledStart=broadcast['scheduledStartISO'],
				scheduledEnd=broadcast['scheduledEndISO'],
				niceTime=broadcast['niceTimeISO'],
				tracknumber=tracknumber
			))
