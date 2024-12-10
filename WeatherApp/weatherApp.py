
from flask import Flask,request,jsonify
from flask_cors import CORS
import json
import requests
import pandas as pd
import numpy as np
app = Flask(__name__)
CORS(app)

# provide the city name based on latitude and longitude
def get_city_name(latitude, longitude):
    API_KEY = 'b2f9f608122f4fedb5f706da5d71829d'
    url = f'https://api.opencagedata.com/geocode/v1/json?q={latitude}+{longitude}&key={API_KEY}'
    response = requests.get(url,verify=False)
    data = response.json()
 
    if data['results']:
        # Extract city name from results
        city = data['results'][0]['components'].get('city') or data['results'][0]['components'].get('town')
        return city
    return None

@app.route('/location',methods=['POST','GET'])
def location():
    data = request.get_json()
    latitude = data.get('latitude')
    longitude = data.get('longitude')
    print('latitude : ',latitude)
    print('longitude :',longitude)
    # Get city name from latitude and longitude
    city_name = get_city_name(latitude, longitude)
    print('location city name-',city_name)
    if city_name:
        return jsonify({'city': city_name})
    else:
        return jsonify({'error': 'City not found'}), 404
 

@app.route('/weather',methods=['POST','GET'])
def weather():
     api_key = 'VQNWGSZS23J8L4CRNLWQH6NKT'
     print('res :',request.get_json())
     data=request.get_json()
     print('data city:',data.get('city'))
     city=data.get('city')
     print('cityName: ->',city)
     url = f"https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{city}?unitGroup=metric&key={api_key}&include=days"
     response = requests.get(url,verify=False)
     if response.status_code == 200:
        data = response.json()
        i=0
        a=[]
        for day in data['days']:
            if i==7:
                break
            date = day['datetime']
            temp = day['temp']
            conditions = day['conditions']
            tempmax=day['tempmax']
            tempmin=day['tempmin']
            a.append ({"Date": date , "Temp": temp, "TempMax" : tempmax , "TempMin" : tempmin, "Conditions": conditions})
            i+=1
        print({'res':a,'city':city})
        print('weather city>>',city)
        return jsonify({'res':a,'city':city})
     else:
        return jsonify({'Error':'Could not retrieve data'})



@app.route('/data')
def data():
    with open('data.json', errors='ignore') as f:
        data=json.load(f)
    df=pd.DataFrame(data)
    a=df['name'].tolist()
    return jsonify({'country': a})



@app.route('/state', methods=['POST','GET'])
def state():
    countryName=''
    res=request.get_json()
    countryName=res['selectCountryName']
    with open('data.json', errors='ignore') as f:
        data=json.load(f)
    df=pd.DataFrame(data)
    temp=df['states'].where(df['name']==countryName)
    n=temp.notnull()
    t=[]
    t=list(temp[n])
    # print('t-->',t)
    print(t[0])
    if len(t[0])==0:
        return jsonify({'states':'No state'})
    state=pd.DataFrame(t[0]) 
    a=state['name'].tolist()
    print({'states':a})
    
    return jsonify({'states':a})

@app.route('/city', methods=['POST','GET'])
def city():
    res=request.get_json()
    print(res)
    with open('data.json', errors='ignore') as f:
        data=json.load(f)
    df=pd.DataFrame(data)
    temp=df['states'].where(df['name']==res['selectCountryName'])
    n=temp.notnull()
    t=list(temp[n])

    state=pd.DataFrame(t[0]) 
    temp2=state['cities'].where(state['name']==res['selectStateName'])

    n2=temp2.notnull()
    t2=list(temp2[n2])

    if len(t2[0])==0:
        return jsonify({'states':'No city'})
    city=pd.DataFrame(t2[0]) 
    a=city['name'].tolist()
   
    # print({'city':a})
    return jsonify({'cities':a})


# provide the latitude and longitude based on city name
def get_city_coordinates(city, api_key):
    base_url = f"http://api.openweathermap.org/geo/1.0/direct?q={city}&limit=1&appid={api_key}"
    response = requests.get(base_url)
    if response.status_code == 200:
        data = response.json()
        if data:
            lat = data[0]['lat']
            lon = data[0]['lon']
            return lat, lon
        else:
            print(f"Error: Could not find coordinates for {city}")
    else:
        print(f"Error: Geocoding API failed with status code {response.status_code}")
    return None, None

@app.route('/get_Date', methods=['POST','GET'])
def get_Date():
    dateRes=request.get_json()
    selectDate=dateRes.get('date')
    print('flask date-->',selectDate)
    fetchData=weather().response
    api_key="9330acf6137ad87b4078c323212d2387"
    city_name=dateRes.get('city')
    print('flask_date_city',city_name)
    lat, lon = get_city_coordinates(city_name, api_key)
    url = f"http://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={api_key}&units=metric"
    response = requests.get(url,verify=False)
    
    if response.status_code == 200:
        data=response.json()
        # print('data-->',data)
        d=dict()
        for forecast in data['list']:
            time = forecast['dt_txt'][11:13]
            if time in ['00', '03', '06', '09', '12', '15','18','21','24']:
                date=((forecast['dt_txt']).split())
                try:
                    d[date[0]]+=[{'time':date[1],'temp':forecast['main']['temp']}]
                except:
                    d[date[0]]=[{'time':date[1],'temp':forecast['main']['temp']}]
    print('dict-->',d)
    dateList=d[selectDate]
    print({'dates':dateList})
    return jsonify({'dates':dateList,'cityName':city_name, 'selectDate':selectDate})


if __name__ == '__main__':

    app.run(debug=True)




# visualcrossing -- provide 7 days forecast 
# openweathermap -- provide 3hr. interval weather report
# countrystatecity.in -- provide whole country name, state name and city name
# opencagedata.com -- provide city name based on Lan and Lon (like gps)