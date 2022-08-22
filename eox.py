import requests
requests.packages.urllib3.disable_warnings()
import json

s = requests.Session()
s.trust_env = False
proxies = {
	'https':''
}
s.proxies = proxies
p = {
	'grant_type': 'client_credentials',

	# API console
	'client_id': '',
	'client_secret': '',
}
s.params.update(p)

auth_url = 'https://cloudsso.cisco.com/as/token.oauth2'
ar = s.post(auth_url, verify=False)
print(ar.status_code,'auth')
rj = json.loads(ar.text)

token = rj['access_token']
token_type = rj['token_type']
auth_string = f'{token_type} {token}'
auth = {
	'Authorization': auth_string,
}
s.headers.update(auth)
s.params = {}

#url = 'https://api.cisco.com/supporttools/eox/rest/5/EOXByProductID/1/WIC-1T=?responseencoding=json'
#url = 'https://apx.cisco.com/cs/api/v1/inventory/hardware'
#url = 'https://apx.cisco.com/cs/api/v1/product-alerts/hardware-eol'
#url = 'https://api.cisco.com/supporttools/eox/rest/5/EOXBySerialNumber/1/###?responseencoding=json'

page_index = 1
date_start = '2000-01-01'
date_end = '2030-12-31'
p = {
	'responseencoding': 'json',
}
url = (
	f'https://api.cisco.com/'
	f'supporttools/eox/rest/5/'
	f'EOXByDates/'
	f'{page_index}/'
	f'{date_start}/'
	f'{date_end}/'
)

records = []
r = s.get(url, params=p, verify=False)
print(r.status_code,'url')
rj = json.loads(r.text)
index_last = rj['PaginationResponseRecord']['LastIndex']
records.extend(
	rj['EOXRecord']
)
available_records = rj['PaginationResponseRecord']['TotalRecords']
while page_index < index_last:
	page_index += 1
	url = (
		f'https://api.cisco.com/'
		f'supporttools/eox/rest/5/'
		f'EOXByDates/'
		f'{page_index}/'
		f'{date_start}/'
		f'{date_end}/'
	)
	rr = s.get(url, params=p, verify=False)
	print(rr.status_code,page_index,'/',index_last,len(records),'/',available_records)
	rrj = json.loads(rr.text)
	records.extend(rrj['EOXRecord'])

# Store records
import _pickle
_pickle.dump(records, open('records.pickle','wb'))

# convert JSON to dict
output = []
for record in records:
	output_d = {}
	for k,v in record.items():
		if isinstance(v,dict):
			for kk,vv in record[k].items():
				output_d[f'{k}_{kk}'] = vv
		else:
			output_d[k] = v
	output.append(output_d)

'''
# SQL Import to Stage
from mysql.mysql import MySQL
m = MySQL(config='stage')
headers = m.get_headers(output)
column_params = {k:'TEXT' for k in headers}
m.recreate_table('cisco_eox',column_params)
m.populate_table('cisco_eox',output,headers,rows_per_send=300)
'''

#
#
print('[I] End')
