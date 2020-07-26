from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import redirect
from urllib.parse import urlencode
import requests
import os
import json

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

    TOKEN_URL = "https://accounts.spotify.com/api/token"
    CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
    CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
    REDIRECT_URI = os.getenv("REDIRECT_URI")

    payload = {
        'grant_type': 'authorization_code',
        'code': request.GET.get('code'),
        'redirect_uri': REDIRECT_URI,
    }

    res = requests.post(TOKEN_URL, auth=(CLIENT_ID, CLIENT_SECRET), data=payload)
    res_data = res.json()

    if res_data.get('error') or res.status_code != 200:
        print('error', res_data.get('error'))
    # app.logger.error(
    #     'Failed to receive token: %s',
    #     res_data.get('error', 'No error information received.'),
    # )
    # abort(res.status_code)

    print("access token ", res_data.get('access_token'))
    print("refresh token ", res_data.get('refresh_token'))
    
    return redirect('http://localhost:3000' + '?access_token=' + res_data.get('access_token'))


