import forecastio

api_key = 'ee19a049da4f1a77ed80c962f1d3fbff'
lat = 49.1163800
lng = -122.5505350

forecast = forecastio.load_forecast(api_key,lat,lng,units='ca')

byHour = forecast.hourly()

for hourlyData in byHour.data:
    print hourlyData.temperature
print byHour.summary
