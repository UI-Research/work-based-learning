from site_monitor import *
import requests

sm = SiteMonitor(burn_in=20)

for i in range(100):
	print(i)
	url = "https://flscns.fldoe.org/PbInstituteCourseSearch.aspx"
	response = requests.get(url)
	delay = sm.track_request(response)

# Display the report of response times in graph format
sm.report('display')