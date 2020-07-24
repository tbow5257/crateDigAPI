from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import redirect
from urllib.parse import urlencode

# Create your views here.


def spotify_login(request):
    payload = {
            'client_id': '60a84f8787bb4900949d3ff89dd896c9',
            'response_type': 'code',
            'redirect_uri': 'http://localhost:8000/spotcallback/',
            'state': 'w000w',
            'scope': 'user-read-private user-read-email',
        }
    
    return redirect('https://accounts.spotify.com/authorize/?' + urlencode(payload))

def spotify_callback(request):
    get = request.GET
    print("callback request ", get)

    print("get.code ", get.get('code'))
    print("get.state ", get.get('state'))

