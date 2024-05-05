import requests
from django.shortcuts import render, redirect, reverse, get_object_or_404
from .models import City
from .forms import CityForm

def is_valid_city(city_name):
    url = f'http://api.openweathermap.org/data/2.5/weather?q={city_name}&units=imperial&appid=271d1234d3f497eed5b1d80a07b3fcd1'

    response = requests.get(url)
    
    if response.status_code == 200 and 'main' in response.json() and 'weather' in response.json():
        return True
    else:
        return False

def index(request):
    cities = City.objects.all()
    url = 'http://api.openweathermap.org/data/2.5/weather?q={}&units=imperial&appid=271d1234d3f497eed5b1d80a07b3fcd1'
    weather_data = []
    message = ''

    if request.method == 'POST':
        form = CityForm(request.POST)
        if form.is_valid():
            city_name = form.cleaned_data['name']
            if is_valid_city(city_name):
                if not City.objects.filter(name=city_name).exists():
                    form.save()
                    message = f"'{city_name}' added to the list."
                else:
                    message = f"'{city_name}' is already in your list."
            else:
                message = "Please enter a valid city name"
    else:
        form = CityForm()

    for city in cities:
        try:
            city_weather = requests.get(url.format(city.name)).json()

            temperature_fahrenheit = city_weather['main']['temp']
            temperature_celsius = round(((temperature_fahrenheit - 32) * 5/9),2)
             

            weather = {
                'city' : city,
                'temperatureC' : temperature_celsius,
                'temperatureF' : temperature_fahrenheit,
                'description' : city_weather['weather'][0]['description'],
                'icon' : city_weather['weather'][0]['icon']
            }
            

            weather_data.append(weather)
        except KeyError as e:
            print(f"KeyError for city '{city.name}': {e}")

    context = {'weather_data' : weather_data, 'form' : form, 'message' : message}
    return render(request, 'weather/index.html', context)

def delete_city(request, city_id):
    city = get_object_or_404(City, pk=city_id)
    city.delete()
    return redirect(reverse('index'))
