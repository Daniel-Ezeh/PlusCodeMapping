This Repository contains the code that helps to generate the plus code 
of a particular country to a specific precision, say 6, 8...

* First, get the rectangular boundaries of the country in question.
This can be gotten from https://www.openstreetmap.org/

* Get the following from the map when you have drawn a rectangle on it.
- Maximum Latitude (North most point)
- Minimum Latitude  (South most point)
- Maximum Longitude (East most point)
- Mininum Longitude (West most point)

In this case 
min_lat, max_lat  = 4.17, 14.01
min_lon, max_lon = 2.58, 14.72

* You can clone the repository from 
https://github.com/Daniel-Ezeh/PlusCodeMapping.git

* Python version used was Python 3.10.11

* Set up a virtual environment and activate it.

* Pip install the provided requirements.txt.

* Go to https://gadm.org/data.html
- Select the country you want to download the geospatial data (Nigeria in this case)
- Download level 1 GeoJSON data for that country.
- Copy into working directory.



