from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import redirect
from rest_framework.response import Response
from rest_framework.views import APIView
from urllib.parse import urlencode
from rest_framework import status
import requests
import os
import json

# Create your views here.


def spotify_login(request):
    payload = {
            'client_id': '60a84f8787bb4900949d3ff89dd896c9',
            'response_type': 'code',
            'redirect_uri': 'http://localhost:8000/spotcallback/',
            'scope': 'streaming user-read-email ' +
                     'user-read-private user-library-read user-library-modify ' +
                     'user-read-playback-state user-modify-playback-state' ,
            'show_dialog': 'true'
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

class SpotifyLookup(APIView):
    def post(self, request):
        
        print("request.POST.get('usertoken') ", request.POST.get('usertoken'))
        print("request.POST.get('usertoken') ", request.POST.get('searchterm'))

        if not request.POST.get('usertoken') or not request.POST.get('searchterm'):
            print("fffffffffff ")
            content = 'missing required body usertoken and/or searchterm'
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

        user_token = request.POST.get('usertoken')

        searchTerm = request.POST.get('searchterm').replace('-','%20')
        
        SEARCH_URL = "https://api.spotify.com/v1/search?q=" + searchTerm + "&type=artist,album"

        headers = {"Authorization": 'Bearer ' + user_token }

        res = requests.get(SEARCH_URL, headers=headers)
        print(res.json())
        res_data = 'nada'

        if 'albums' in res.json() and len(res.json()['albums']['items']) > 0:
            res_data = res.json()['albums']['items'][0]['uri']
    
        if 'artists' in res.json() and len(res.json()['artists']['items']) > 0:
            res_data = res.json()['artists']['items'][0]['uri']

        print('albums results', res_data)

        return Response(res_data, 200)
