import requests
import pycountry
from django.shortcuts import render,redirect
from django.http import *
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from Main.settings import access_key_from_ip_stack
# Create your views here.

def get_client_ip(request):
   x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
   if x_forwarded_for:
       ip = x_forwarded_for.split(',')[0]
   else:
       ip = request.META.get('REMOTE_ADDR')
   return ip


def get_geolocation_for_ip(ip):
    url = f"http://api.ipstack.com/{ip}?access_key={access_key_from_ip_stack}"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

@api_view(['GET'])
def home(request):
    geo_info = get_geolocation_for_ip(get_client_ip(request))
    if geo_info['country_name'] is not None:
        country = pycountry.countries.get(name = geo_info['country_name'])
        currency = pycountry.currencies.get(numeric=country.numeric)
        vs_currency = currency.name
    else:
        vs_currency = 'usd'
    url = f"https://api.coingecko.com/api/v3/coins/markets?vs_currency={vs_currency}&order=market_cap_desc&per_page=100&sparkline=false"
    response = requests.get(url)
    if response.status_code == 200:
        coins = response.json()
    else:
        coins = None
    context = {
        'coins':coins,
        'geo_info':geo_info,
        'ip':get_client_ip(request),
    }
    return render(request,'index.html',context=context)

