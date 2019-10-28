import requests
import sys

if __name__ == '__main__':
	try:
		port = int(sys.argv[0])
		route = str(sys.argv[1])
		data = {'target':f'http://localhost:{port}'}
		headers={'Authorization': 'token 31507a9ddf3e41cf86b58ffede2db68326657437704461ae2c1a4018d55e18f0'}
		usr = input(f"Are you sure you want to delete the route: {route} at port {port} (y or n)")
		if usr.lower() == 'y':
			response = requests.delete(f'http://localhost:8001/api/routes/{route}',json=data,headers=headers)
		else:
			print(f"Not deleting route {route} at port {port}")

	except:
		print("Check inputs!\nSyntax is: python delete_route.py $port $route")