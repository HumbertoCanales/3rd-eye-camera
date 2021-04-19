import socket
import requests


def get_ip_address():
    """ip_address = ''
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ip_address = s.getsockname()[0]
    s.close()"""
    url = 'http://127.0.0.1:4040/api/tunnels'
    r = requests.get(url)
    res = r.json()
    ip = res['tunnels'][0]['public_url']
    print(ip)
    return ip


get_ip_address()
