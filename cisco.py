import requests
requests.packages.urllib3.disable_warnings()
import json
import os

class Cisco(object):
	def __init__(self, config=None):
		self.base_url = 'https://api.cisco.com/'
		if config is None:
			print('[E] No configuration filename not provided')
		else:
			self.load_configuration(config)
		return
	
	def load_configuration(self, config):
		config_file = 'configuration.json'
		path = os.path.abspath(__file__)
		dir_path = os.path.dirname(path)
		with open(f'{dir_path}/{config_file}','r') as f:
			raw_file = f.read()
		config_raw = json.loads(raw_file)
		if config not in config_raw['servers']:
			print('[E] Configuration not found in configuration.json')
		else:
			connection_info = config_raw['servers'][config]
			response = self.authenticate(connection_info)
			return response
			#self.collector = connection_info['host']
			#self.authenticate(connection_info)
	
	def authenticate(self, connection_info):
		self.session = requests.Session()
		self.session.trust_env = False
		proxies = {
			'http':''
		}
		self.session.proxies = proxies
		
		authentication_params = {
			'grant_type':	'client_credentials',
			'client_id':	connection_info['client_id'],
			'client_secret':	connection_info['client_secret'],
		}
		self.session.params.update(authentication_params)
		
		auth_url = 'https://cloudsso.cisco.com/as/token.oauth2'
		response = self.session.post(auth_url, params=authentication_params, verify=False)
		
		if response.status_code:
			response_json = json.loads(response.text)
			authorization_string = (
				f'{response_json["token_type"]}'
				f' '
				f'{response_json["access_token"]}'
			)
			authorization_header = {
				'Authorization':	authorization_string,
			}
			self.session.headers.update(authorization_header)
			self.session.params = {}
		return response
	
	def post_request(self, path, params='', data=''):
		url = f'{self.base_url}{path}'
		response_raw = self.session.post(url, params=params, data=data, verify=False)
		if response_raw.status_code == 200:
			return {
				'success':	True,
				'result':	response_raw.text,
				'response_object':	response_raw,
			}
		else:
			return {
				'success':	False,
				'result':	'',
				'response_object':	response_raw,
			}
		return
	
	def get_request(self, path, params=''):
		url = f'{self.base_url}{path}'
		response_raw = self.session.get(url, params=params, verify=False)
		if response_raw.status_code == 200:
			return {
				'success':	True,
				'result':	response_raw.text,
				'response_object':	response_raw,
			}
		else:
			return {
				'success':	False,
				'result':	'',
				'response_object':	response_raw,
			}
		return
	
	def get_eox_product(self, product, encoding='json'):
		path = f'eox/rest/5/EOXByProductID/1/{product}?responseencoding={encoding}'
		output = self.get_request(path)
		return output
	
	def get_eox_serial(self, serial, encoding='json'):
		path = f'supporttools/eox/rest/5/EOXBySerialNumber/1/{serial}?responseencoding={encoding}'
		output = self.get_request(path)
		return output
	
	def get_eox_date_range(self, date_start, date_end, page=1, attribute='EO_LAST_SUPPORT_DATE', encoding='json'):
		page_index = page
		p = {
			'responseencoding': encoding,
			'eoxAttrib': attribute
		}
		path = (
			f'supporttools/eox/rest/5/'
			f'EOXByDates/'
			f'{page_index}/'
			f'{date_start}/'
			f'{date_end}/'
		)
		# initial query for records
		output = self.get_request(path, params=p)
		# remainder of records
		results = []
		response_json = json.loads(output['result'])
		index_last = response_json['PaginationResponseRecord']['LastIndex']
		records_total = response_json['PaginationResponseRecord']['TotalRecords']
		results.extend(
			response_json['EOXRecord']
		)
		print(f'[I] {page_index}/{index_last} requests. {len(results)}/{records_total} total')
		# loop until all records retrieved
		while page_index < index_last:
			page_index += 1
			path = (
				f'supporttools/eox/rest/5/'
				f'EOXByDates/'
				f'{page_index}/'
				f'{date_start}/'
				f'{date_end}/'
			)
			try:
				response = self.get_request(path, params=p)
			except:
				print(f'[W] Fail, trying again. Last : {page_index}/{index_last} requests. {len(results)}/{records_total} total')
				response = self.get_request(path, params=p)
			response_json = json.loads(response['result'])
			results.extend(response_json['EOXRecord'])
			print(f'[I] {page_index}/{index_last} requests. {len(results)}/{records_total} total')
			#
		output['result'] = results
		self.store_data('records',results)
		return output
	
	def store_data(self, name, data):
		filename = f'{name}.pickle'
		import _pickle
		_pickle.dump(data, open(filename,'wb'))
		return
	
	def json_to_dict(self, data):
		output = []
		for record in data:
			output_d = {}
			for k,v in record.items():
				if isinstance(v,dict):
					for kk,vv in record[k].items():
						output_d[f'{k}_{kk}'] = vv
				else:
					output_d[k] = v
			output.append(output_d)
		return output

if __name__ == '__main__':
	c = Cisco(config='apiconsole')
	r = c.get_request('hello')
	#
	#
	#date_start = '2000-01-01'
	#date_end = '2040-12-31'
	#data = c.get_eox_date_range(date_start, date_end)
	#c.store_data(data['result'])
	#data_dict = c.json_to_dict(data['result'])
	#
