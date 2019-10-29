import requests
import sys

if __name__ == '__main__':
	port = sys.argv[0]
	route = sys.argv[1]
	data = {'target':f'http://localhost:{port}'}
	headers={'Authorization': 'token 31507a9ddf3e41cf86b58ffede2db68326657437704461ae2c1a4018d55e18f0'}
	response = requests.post('http://localhost:8001/api/routes/{route}',json=data,headers=headers)
