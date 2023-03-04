from django.shortcuts import render,redirect
from django.http import JsonResponse
import json
import pytz
from datetime import datetime,date,time,timedelta
from timezonefinder import TimezoneFinder
import mysql.connector
import pandas as pd
import math
import ladybug
from ladybug.epw import EPW
from django.contrib import messages
import mimetypes
from PIL import Image
#from .models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from pythermalcomfort.models import utci
import geopandas as gpd
from shapely.geometry import Point
import matplotlib.pyplot as plt
from branca.element import MacroElement
from jinja2 import Template
import os
import folium
from folium import plugins
from folium import Map, FeatureGroup, Marker, LayerControl
import branca.colormap as cm
import ipywidgets
import geocoder
import geopy
import numpy as np
import pandas as pd
import sys
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib.auth import authenticate, login, logout
# Get altitude and longitude
from ladybug.location import Location
from ladybug.sunpath import Sunpath
from geopy.geocoders import Nominatim
import csv
import contextily as ctx

class BindColormap(MacroElement):
    def __init__(self, layer, colormap):
        super(BindColormap, self).__init__()
        self.layer = layer
        self.colormap = colormap
        self._template = Template(u"""
        {% macro script(this, kwargs) %}
            {{this.colormap.get_name()}}.svg[0][0].style.display = 'block';
            {{this._parent.get_name()}}.on('layeradd', function (eventLayer) {
                if (eventLayer.layer == {{this.layer.get_name()}}) {
                    {{this.colormap.get_name()}}.svg[0][0].style.display = 'block';
                }});
            {{this._parent.get_name()}}.on('layerremove', function (eventLayer) {
                if (eventLayer.layer == {{this.layer.get_name()}}) {
                    {{this.colormap.get_name()}}.svg[0][0].style.display = 'none';
                }});
        {% endmacro %}
        """)

def landing_page(request):
    return render(request,'landing_page.html')   
def read_data(username,password,table_name):
  
    db=mysql.connector.connect(
    host='climateflux.com',
    user=username,
    passwd=password,
    database="climate_walk"
    )

    query=f"select * from {table_name} where has_fix=1"  #remove pi8 and make it automated
    df_2=pd.read_sql(query,db)
   
    return df_2

def fetch_table_data(table_name,username,password):
    # The connect() constructor creates a connection to the MySQL server and returns a MySQLConnection object.
    db = mysql.connector.connect(
        host='climateflux.com',
        database='climate_walk',
        user=username,
        password=password
    )

    mycursor = db.cursor()
    mycursor.execute('select * from ' + table_name)

    header = [row[0] for row in mycursor.description]

    rows = mycursor.fetchall()

    # Closing connection
    db.close()

    return header, rows

def transform_Longitude(dataframe):
    dataframe["Longitude"]=dataframe["Longitude"]/1000000
    
    
def transform_Latitude(dataframe):
    dataframe["Latitude"]=dataframe["Latitude"]/1000000

def transform_Tglobe(dataframe):
    dataframe["Tglobe"]=dataframe["Tglobe"]/100    
def transform_humidity(dataframe):
    dataframe["humidity"]=dataframe["humidity"]/100

def transform_RH_Tair(dataframe):
    dataframe["RH_Tair"]=dataframe["RH_Tair"]/100
    
def transform_decibel(dataframe):
    dataframe["decibel"]=dataframe["decibel"]/10
    
def transform_RAD(dataframe):
    dataframe["radiation"]=125*(dataframe["radiation"]/1000000-4)
    
def add_colour(parmaeter_name,list_values):
    
    db=mysql.connector.connect(
    host="climateflux.com",
    user="bishoykaleny",
    passwd="01280408351",
    database="climate_walk"
    )
    mycursor=db.cursor()
    for x in list_values:
      query="INSERT INTO mapping(parameter,colour) VALUES ("+"'"+parmaeter_name+"',"+"'"+x+"'"+")"
      mycursor.execute(query)
    db.commit()
    
 
def display_colour(parameter_name):
    db=mysql.connector.connect(
    host="climateflux.com",
    user="bishoykaleny",
    passwd="01280408351",
    database="climate_walk"
    )
    mycursor=db.cursor()
    
    query_2=f"SELECT parameter,colour FROM mapping WHERE colour IS NOT NULL AND parameter='{parameter_name}'"
    df=pd.read_sql(query_2,db)
    return df



def add_index(parameter_name,list_values):
    db=mysql.connector.connect(
    host="climateflux.com",
    user="bishoykaleny",
    passwd="01280408351",
    database="climate_walk"
    )
    mycursor=db.cursor()
    for x in list_values:
      query=f"INSERT INTO mapping(parameter,indexing) VALUES ('{parameter_name}',{x})"
      mycursor.execute(query)

    db.commit()
    
def display_index(parameter_name):
    db=mysql.connector.connect(
    host="climateflux.com",
    user="bishoykaleny",
    passwd="01280408351",
    database="climate_walk"
    )
    mycursor=db.cursor()
    
    query_2=f"SELECT parameter,indexing FROM mapping WHERE indexing IS NOT NULL AND parameter='{parameter_name}'"
    df=pd.read_sql(query_2,db)
    return df    
    
    
def add_vmin_vmax(parameter_name,vmin,vmax):
    db=mysql.connector.connect(
    host="climateflux.com",
    user="bishoykaleny",
    passwd="01280408351",
    database="climate_walk"
    )
    mycursor=db.cursor()
    query=f"INSERT INTO mapping(parameter,vmin,vmax) VALUES ('{parameter_name}',{vmin},{vmax})"
    mycursor.execute(query)
    db.commit()
    
def display_vmin(parameter_name):
    db=mysql.connector.connect(
    host="climateflux.com",
    user="bishoykaleny",
    passwd="01280408351",
    database="climate_walk"
    )
    mycursor=db.cursor()
    query_4=f"SELECT parameter,vmin FROM mapping WHERE vmin IS NOT NULL AND parameter='{parameter_name}'"
    df_3=pd.read_sql(query_4,db)
    return df_3

def display_vmax(parameter_name):
    db=mysql.connector.connect(
    host="climateflux.com",
    user="bishoykaleny",
    passwd="01280408351",
    database="climate_walk"
    )
    mycursor=db.cursor()
    query_4=f"SELECT parameter,vmax FROM mapping WHERE vmax IS NOT NULL AND parameter='{parameter_name}'"
    df_3=pd.read_sql(query_4,db)
    return df_3
    
def list_parameters():
    db=mysql.connector.connect(
    host="climateflux.com",
    user="bishoykaleny",
    passwd="01280408351",
    database="climate_walk"
    )
    mycursor=db.cursor()
    query="SELECT DISTINCT parameter FROM mapping"
    df=pd.read_sql(query,db)
    return df['parameter'].values.tolist()
    
    
def get_gdf(df):
    df_geometry = [Point(xy) for xy in zip(df.Longitude, df.Latitude)] 
    gdf = gpd.GeoDataFrame(df, crs= {"init": "epsg:4326"}, geometry=df_geometry)
    gdf = gdf.to_crs(epsg=3857)
    return gdf

# def popup1(time,p):
#     #time_1=str(int(time))
#     time_1=str(time)
#     if len(time_1)==11:
        
#         html = "<br><b>Time: &nbsp</b>"+ time_1[0:2]+":"+time_1[2:4]+":"+time_1[4:6]+"<br><b>Value: &nbsp</b>"+ str(round(p,2))
#     else:
#         html = "<br><b>Time: &nbsp</b>"+ time_1[0:2]+":"+time_1[2:4]+":"+time_1[4:6]+"<br><b>Value: &nbsp</b>"+ str(round(p,2))
#     iframe = folium.IFrame(html)
#     popup = folium.Popup(iframe, min_width=150,max_width=150)
#     return popup

def popup1(time,p):
    #time_1=str(int(time))
    time_1=str(time)

        
    html = "<br><b>Time: &nbsp</b>"+ time_1+"<br><b>Value: &nbsp</b>"+ str(round(p,2))

    iframe = folium.IFrame(html)
    popup = folium.Popup(iframe, min_width=150,max_width=150)
    return popup


def circlemarker (layer, scale, feature_group):
    for loc, p, time in zip(zip(layer.iloc[:,0],layer.iloc[:,1]),layer.iloc[:,2], layer.iloc[:,3]):
        folium.CircleMarker(
        color=scale(p),
        colormap=scale,
        location=loc,
        radius=2, 
        fill=True,
        popup=popup1(time,p)).add_to(feature_group)
        
def convert_time(time_1):
    time = time_1[0:2]+":"+time_1[2:4]+":"+time_1[4:6]
    #if len(time_1)==11:
        
        #time = time_1[0:2]+":"+time_1[2:4]+":"+time_1[4:6]
    #else:
        #time = time_1[0]+":"+time_1[1:3]+":"+time_1[3:5]
    return time
       
@login_required(login_url='login')   
def run_map(request,pk):
    username = request.POST.get('username')
    password = request.POST.get('password')
    print(str(username))
    
    db=mysql.connector.connect(
    host="climateflux.com",
    user="bishoykaleny",
    port="3306",
    passwd="01280408351",
    database="climate_walk"
    )
    mycursor=db.cursor()
    tables=[]
    table_names_list=[]
    mycursor.execute("SHOW TABLES")
    i=0
    for table_name in mycursor:
        table_name_corrected=str(table_name)[2:-3]
        underscore=table_name_corrected.find('_')
        print(table_name_corrected[0:underscore])
        if table_name_corrected.find(request.user.username)>=0:
            
            table_names_list.append(table_name_corrected)
            hashed={'id':i,'name':table_name_corrected}
            tables.append(hashed)
            print(table_name_corrected)
            i=i+1
    table=None
    for table_temp in tables:
        if table_temp['id']==int(pk):
            table = table_temp
    
    df=read_data('bishoykaleny','01280408351',table['name'])
    df['wind_s']=(abs(df['north_wind'])+abs(df['east_wind']))/2
    transform_decibel(df)
    transform_Latitude(df)
    transform_Longitude(df)
    transform_humidity(df)

    transform_RAD(df)
    transform_Tglobe(df)
    transform_RH_Tair(df)
    print(str(df['GPS_date'].values[2]))
    lat_sun=str(df["Latitude"].values[2])
    long_sun=str(df["Longitude"].values[2])
    lat_sun_fl=df["Latitude"].values[2]
    long_sun_fl=df["Longitude"].values[2]
    if len(str(int(float((df['GPS_date'].values[2])))))==6:
        month_check=str((float(int(df['GPS_date'].values[2]))))[2:4]
        print(month_check)
        if month_check[0]=='0':
            month=month_check[1]
            day=str(int(float((df['GPS_date'].values[2]))))[0:2]
        else:
            
            month=str(int(float((df['GPS_date'].values[2]))))[2:4]
            day=str(int(float((df['GPS_date'].values[2]))))[0:2]
    else:
        month_check=str(int(float((df['GPS_date'].values[2]))))[1:3]
        if month_check[0]=='0':
            month=month_check[1]
            day=day='0'+str(int(float((df['GPS_date'].values[2]))))[0]
            
        else: 
            month=str(int(float((df['GPS_date'].values[2]))))[1:3]
            day='0'+str(int(df['GPS_date'].values[2]))[0]
    if len(str(int(float((df['GPS_time'].values[2])))))==9:
        
        hour=str(int(float((df['GPS_time'].values[2]))))[0:2]
    else:
        hour='0'+str(int(float((df['GPS_time'].values[2]))))[0]
    df['Readable_GPS_time'] = df.apply(lambda x: readable_gps_time(x['GPS_time']), axis=1)
    local=get_local_time(df['Readable_GPS_time'].values[2],df['Longitude'].values[2],df['Latitude'].values[2])[0:2]
    print(int(month))
    print(int(day))
    print(int(hour))
    BerAlt=get_ber_alt(lat_sun,long_sun,lat_sun_fl,long_sun_fl,int(month),int(day),int(local))
    Prof=Pfactor(BerAlt)
    df['MRT'] = df.apply(lambda x: mrt(x['Tglobe'], x['wind_Tair'], x['wind_s']), axis=1)
    df['MRT_S'] = df.apply(lambda x: MRT(x['MRT'], x['radiation'], Prof), axis=1)
    df.loc[df['wind_s'] < 0.5, 'wind_s'] = 0.5
    df['UTCI'] = df.apply(lambda x: utci(x['wind_Tair'], x['MRT'], x['wind_s'], x['humidity']), axis=1)
    #df['Readable_gps_time']=df.apply(lambda x:readable_gps_time(x['GPS_time']),axis=1)
    #df['Local_time']=df.apply(lambda x: get_local_time(longi=long_sun_fl,lati=lat_sun_fl,GPS_time=x['Readable_gps_time']),axis=1)
    gdf=get_gdf(df)
    print(len(df)//2)
    midd_long=df["Longitude"].values[len(df)//2]
    midd_lat=df["Latitude"].values[len(df)//2]
    intMap = folium.Map(location=[midd_lat, midd_long], zoom_start=15, tiles=None)
    base_map = folium.FeatureGroup(name='Basemap', overlay=True, control=False)
    folium.TileLayer(tiles='Stamen Terrain').add_to(base_map)
    base_map.add_to(intMap)
    gdf_f = gdf
    locations = list(zip(gdf_f.Latitude, gdf_f.Longitude))
    all_paramters=list_parameters()
    integrated_paramaeters=list(df.columns)
    mapping_parameters=[par for par in all_paramters if par in integrated_paramaeters]
    sys.path.insert(0, 'folium')
    sys.path.insert(0, 'branca')   
    for x in mapping_parameters:
        
        parameter_name=gdf_f[["Latitude","Longitude",x,"Readable_GPS_time"]]
        parameter_name=parameter_name.dropna(subset=[x])
        scale=cm.LinearColormap(display_colour(x)['colour'].values.tolist(),
                                index=display_index(x)['indexing'].values.tolist(),
                                vmin=display_vmin(x)['vmin'].values.tolist()[0],
                                vmax=display_vmax(x)['vmax'].values.tolist()[0]
                                )
    
        print(display_index(x)['indexing'].values.tolist())
        feature_group=FeatureGroup(name=x,overlay=False)
        circlemarker(parameter_name,scale,feature_group)
        intMap.add_child(feature_group)
        intMap.add_child(scale)
        intMap.add_child(BindColormap(feature_group,scale))
    utci_et = gdf_f[["Latitude", "Longitude", "UTCI", "GPS_time"]]
    utci_et = utci_et.dropna(subset=['UTCI'])

    scale_utci_et = cm.LinearColormap(['#000080','#0000c0','#0000ff','#0062ff','#00C0FF','#00C000','#FF6600','#FF3300','#CC0000','#800000'], index =[-40,-27,-13,0,9,26,32,38,46], vmin=-46, vmax=52, caption='UTCI Equivalent Temperature (°C)')
    feature_group7 = FeatureGroup(name='UTCI ET', overlay=False)
    circlemarker(utci_et,scale_utci_et,feature_group7)
    intMap.add_child(feature_group7)
    intMap.add_child(scale_utci_et)
    intMap.add_child(BindColormap(feature_group7,scale_utci_et))
    intMap.add_child(folium.map.LayerControl('bottomleft', collapsed=False))
    mapFname = 'output.html'
    #intMap.save(mapFname)
    intMap = intMap._repr_html_()
    context={'intMap':intMap}
    #mapUrl = 'file://{0}/{1}'.format(os.getcwd(), mapFname)
    #return HttpResponseRedirect(mapUrl)
    #context={'mapFname':mapFname}
    return render(request,'maps.html',context)

def get_local_time(GPS_time,longi,lati):
  tf = TimezoneFinder()
  tz = tf.timezone_at(lng=longi, lat=lati)
  GPS_time_time = datetime.strptime(GPS_time, '%H:%M:%S').time()
  loc_time=pytz.timezone(tz)
  local_time_now=str(datetime.now(loc_time))
  hours_difference=int(local_time_now[27:29])
  minutes_difference=int(local_time_now[30:])
  delta_hours = timedelta(hours = hours_difference,minutes=minutes_difference)
  delta_minutes=timedelta(minutes=minutes_difference)
  if local_time_now[26]=='+':
    local_time=(datetime.combine(date(1,1,1),GPS_time_time) + delta_hours).time()
  elif local_time_now[26]=='-':
    local_time=(datetime.combine(date(1,1,1),GPS_time_time) - delta_hours).time()
  return str(local_time)

def readable_gps_time(GPS_time):
    if len(str(int(float(GPS_time))))==9:
        
        hour=str(int(float(GPS_time)))[0:2]
        minute=str(int(float(GPS_time)))[2:4]
        second=str(int(float(GPS_time)))[2:4]
    else:
        hour='0'+str(int(float(GPS_time)))[0]
        minute=str(int(float(GPS_time)))[1:3]
        second=str(int(float(GPS_time)))[3:5]
    string_gps=f'{hour}:{minute}:{second}'
        
    return string_gps
def get_processed_data(request,pk):
    username = request.POST.get('username')
    password = request.POST.get('password')
    
    db=mysql.connector.connect(
    host="climateflux.com",
    user="bishoykaleny",
    port="3306",
    passwd="01280408351",
    database="climate_walk"
    )
    mycursor=db.cursor()
    tables=[]
    table_names_list=[]
    mycursor.execute("SHOW TABLES")
    i=0
    for table_name in mycursor:
        table_name_corrected=str(table_name)[2:-3]
        underscore=table_name_corrected.find('_')
        print(table_name_corrected[0:underscore])
        if table_name_corrected.find(request.user.username)>=0:
            
            table_names_list.append(table_name_corrected)
            hashed={'id':i,'name':table_name_corrected}
            tables.append(hashed)
            print(table_name_corrected)
            i=i+1
    table=None
    for table_temp in tables:
        if table_temp['id']==int(pk):
            table = table_temp
    tableeee=table['name']
 
    df=read_data('bishoykaleny','01280408351',table['name'])
    df['wind_s']=(abs(df['north_wind'])+abs(df['east_wind']))/2
    transform_decibel(df)
    transform_Latitude(df)
    transform_Longitude(df)
    transform_humidity(df)

    transform_RAD(df)
    transform_Tglobe(df)
    transform_RH_Tair(df)
    lat_sun=str(df["Latitude"].values[2])
    long_sun=str(df["Longitude"].values[2])
    lat_sun_fl=float(df["Latitude"].values[2])
    long_sun_fl=float(df["Longitude"].values[2])
    print(long_sun_fl)
    print(lat_sun_fl)
    tf = TimezoneFinder()
    tz = tf.timezone_at(lng=long_sun_fl, lat=lat_sun_fl)
    if len(str(int(float((df['GPS_date'].values[2])))))==6:
        month_check=str((float(int(df['GPS_date'].values[2]))))[2:4]
        print(month_check)
        if month_check[0]=='0':
            month=month_check[1]
            day=str(int(float((df['GPS_date'].values[2]))))[0:2]
        else:
            
            month=str(int(float((df['GPS_date'].values[2]))))[2:4]
            day=str(int(float((df['GPS_date'].values[2]))))[0:2]
    else:
        month_check=str(int(float((df['GPS_date'].values[2]))))[1:3]
        if month_check[0]=='0':
            month=month_check[1]
            day='0'+str(int(float((df['GPS_date'].values[2]))))[0]
            
        else: 
            month=str(int(float((df['GPS_date'].values[2]))))[1:3]
            day='0'+str(int(df['GPS_date'].values[2]))[0]
    if len(str(int(float((df['GPS_time'].values[2])))))==9:
        
        hour=str(int(float((df['GPS_time'].values[2]))))[0:2]
        
    else:
        hour='0'+str(int(float((df['GPS_time'].values[2]))))[0]
    df['Readable_GPS_time'] = df.apply(lambda x: readable_gps_time(x['GPS_time']), axis=1)
    local=get_local_time(df['Readable_GPS_time'].values[2],df['Longitude'].values[2],df['Latitude'].values[2])[0:2]
    print(int(month))
    print(int(day))
    print(int(hour))
    print(int(local))

    BerAlt=get_ber_alt(lat_sun,long_sun,lat_sun_fl,long_sun_fl,int(month),int(day),int(hour))
    Prof=Pfactor(BerAlt)

    df['MRT'] = df.apply(lambda x: mrt(x['Tglobe'], x['wind_Tair'], x['wind_s']), axis=1)
    df['MRT_S'] = df.apply(lambda x: MRT(x['MRT'], x['radiation'], Prof), axis=1)
    df.loc[df['wind_s'] < 0.5, 'wind_s'] = 0.5
    df['UTCI'] = df.apply(lambda x: utci(x['wind_Tair'], x['MRT'], x['wind_s'], x['humidity']), axis=1)
    print('done')
    #df['Readable_GPS_time'] = df.apply(lambda x: readable_gps_time(x['GPS_time']), axis=1)
    print('done2')
    #list_of_local_time=[]
    #for x in range(len(df)):
        #value=get_local_time(df['Readable_GPS_time'].values[x],df['Longitude'].values[x],df['Latitude'].values[x])
        #list_of_local_time.append(value)
    #print(list_of_local_time[0])
    #df['local_time']=list_of_local_time
    #df['local_time']=get_local_time(df['Readable_GPS_time'].values[2],df['Longitude'].values[2],df['Latitude'].values[2])
    #for x in range (len(df)):
        #df['local_time']=get_local_time(df['Readable_GPS_time'].values[x],df['Longitude'].values[x],df['Latitude'].values[x])
        
    #df['Local_time'] = df.apply(lambda x: get_local_time(x['Readable_GPS_time'],x["Longitude"],x["Latitude"]), axis=1)
    #df['Local_time'] = df.apply(lambda x: get_local_time(x['Readable_GPS_time'],long_sun_fl,lat_sun_fl), axis=1)
    #df['Local_time']=df.apply(lambda x: get_local_time(longi=long_sun_fl,lati=lat_sun_fl,GPS_time=x['Readable_GPS_time']),axis=1)
    print('done3')
    response = HttpResponse(
        content_type='text/csv',
        headers={'Content-Disposition': f'attachment; filename="{tableeee}_processed.csv"'},
    )
    df.to_csv(path_or_buf=response)  # with other applicable parameters
    return response

    
    
def display_csv(request,pk):
    username = request.POST.get('username')
    password = request.POST.get('password')
    
    db=mysql.connector.connect(
    host="climateflux.com",
    user="bishoykaleny",
    port="3306",
    passwd="01280408351",
    database="climate_walk"
    )
    mycursor=db.cursor()
    tables=[]
    table_names_list=[]
    mycursor.execute("SHOW TABLES")
    i=0
    for table_name in mycursor:
        table_name_corrected=str(table_name)[2:-3]
        underscore=table_name_corrected.find('_')
        print(table_name_corrected[0:underscore])
        if table_name_corrected.find(request.user.username)>=0:
            
            table_names_list.append(table_name_corrected)
            hashed={'id':i,'name':table_name_corrected}
            tables.append(hashed)
            print(table_name_corrected)
            i=i+1
    table=None
    for table_temp in tables:
        if table_temp['id']==int(pk):
            table = table_temp
   
    tableeee=table['name']
    coloums,rows=fetch_table_data(table['name'],'bishoykaleny','01280408351')
    response = HttpResponse(
        content_type='text/csv',
        headers={'Content-Disposition': f'attachment; filename="{tableeee}.csv"'},
    )

    writer = csv.writer(response)
    writer.writerow(coloums)
    for row in rows:
        writer.writerow(row)
    return response
    
def delete_table(request,pk):
    username = request.POST.get('username')
    password = request.POST.get('password')
    
    db=mysql.connector.connect(
    host="climateflux.com",
    user="bishoykaleny",
    port="3306",
    passwd="01280408351",
    database="climate_walk"
    )
    mycursor=db.cursor()
    tables=[]
    table_names_list=[]
    mycursor.execute("SHOW TABLES")
    i=0
    for table_name in mycursor:
        table_name_corrected=str(table_name)[2:-3]
        underscore=table_name_corrected.find('_')
        print(table_name_corrected[0:underscore])
        if table_name_corrected.find(request.user.username)>=0:
            
            table_names_list.append(table_name_corrected)
            hashed={'id':i,'name':table_name_corrected}
            tables.append(hashed)
            print(table_name_corrected)
            i=i+1
    table=None
    for table_temp in tables:
        if table_temp['id']==int(pk):
            table = table_temp
    tableeee=table['name']
    mycursor.execute(f"DROP TABLE {tableeee}")
    return redirect('tables')                  

def loginPage(request):
    
    if request.user.is_authenticated:
        return redirect('tables')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        print(username)

        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request, 'User does not exist')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('tables')
        else:
            messages.error(request, 'Username OR password does not exit')

    context = {}
    return render(request, 'login_page.html', context)

def logoutUser(request):
    logout(request)
    return redirect('tables')


@login_required(login_url='login')
def read_tables(request):
    #username = request.POST.get('username')
    #password = request.POST.get('password')
    #print(request.user.username)
    db=mysql.connector.connect(
    host="climateflux.com",
    user=f"CF_{request.user.username}",
    port="3306",
    passwd=f"{request.user.username}_Climatewalks",
    database="climate_walk"
    )
    mycursor=db.cursor()
    tables=[]
    table_names_list=[]
    days=[]
    days_names=[]
    mycursor.execute("SHOW TABLES")
    i=0
    for table_name in mycursor:
        table_name_corrected= str(table_name)[2:-3]
        if table_name_corrected.find(request.user.username)>=0:
            table_names_list.append(table_name_corrected)
            hashed={'id':i,'name':table_name_corrected}
            tables.append(hashed)
        i=i+1
    j=0
    for table in table_names_list:
        und=table.find("_")
        if table[und+1:und+11] not in days_names:
            days_names.append(table[und+1:und+11])
            hashed_days={'id':j,'day':table[und+1:und+11]}
            days.append(hashed_days)
            j=j+1
        else:
            j=j+1
        print(table[und+1:und+11])
        
    context={'days':days}    
    #
    # 
    #context={'tables':tables}
    return render(request,'tables.html',context)
def days_tables(request,pk):
    db=mysql.connector.connect(
    host="climateflux.com",
    user=f"CF_{request.user.username}",
    port="3306",
    passwd=f"{request.user.username}_Climatewalks",
    database="climate_walk"
    )
    mycursor=db.cursor()
    tables=[]
    table_names_list=[]
    days=[]
    days_names=[]
    mycursor.execute("SHOW TABLES")
    i=0
    for table_name in mycursor:
        table_name_corrected= str(table_name)[2:-3]
        if table_name_corrected.find(request.user.username)>=0:
            table_names_list.append(table_name_corrected)
            hashed={'id':i,'name':table_name_corrected}
            tables.append(hashed)
        i=i+1
    j=0
    for table in table_names_list:
        und=table.find("_")
        if table[und+1:und+11] not in days_names:
            days_names.append(table[und+1:und+11])
            hashed_days={'id':j,'day':table[und+1:und+11]}
            days.append(hashed_days)
            j=j+1
        else:
            j=j+1
    day=None
    for day_temp in days:
        if day_temp['id']==int(pk):
            day = day_temp['day']
    table_by_day=[]
    n=0
    print(day)
    
    for table in table_names_list:
        und=table.find("_")
        print(table[und+1:und+11])
        if table[und+1:und+11]==day:
            hashed_table_by_day={'id':n,'table_by_day':table}
            table_by_day.append(hashed_table_by_day)
            n=n+1
        else:
            n=n+1
    context={'table_by_day':table_by_day}
    print(context)
    return render(request,'tables_by_day.html',context)
            

    

@login_required(login_url='login')
def show_table(request,pk):
    username = request.POST.get('username')
    password = request.POST.get('password')
    
    db=mysql.connector.connect(
    host="climateflux.com",
    user="bishoykaleny",
    port="3306",
    passwd="01280408351",
    database="climate_walk"
    )
    mycursor=db.cursor()
    tables=[]
    table_names_list=[]
    mycursor.execute("SHOW TABLES")
    i=0
    for table_name in mycursor:
        table_name_corrected=str(table_name)[2:-3]
        underscore=table_name_corrected.find('_')
        print(table_name_corrected[0:underscore])
        if table_name_corrected.find(request.user.username)>=0:
            
            table_names_list.append(table_name_corrected)
            hashed={'id':i,'name':table_name_corrected}
            tables.append(hashed)
            print(table_name_corrected)
            i=i+1
    table=None
    for table_temp in tables:
        if table_temp['id']==int(pk):
            table = table_temp
    tableeee=table['name']
    df=read_data('bishoykaleny','01280408351',table['name'])
    time_1=str(int(float(df['GPS_time'].values[1])))
    time_n=str(int(float(df['GPS_time'].values[len(df.axes[0])-1])))
    converted_1=readable_gps_time(time_1)
    converted_2=readable_gps_time(time_n)
    number_of_rows=len(df.axes[0]-1)
    names_of_parameters=list(df.columns)
    print(convert_time(time_1))
    print(convert_time(time_n))
    meta_data=[]
    hashed={'start_time':converted_1,'end_time':converted_2,'len':number_of_rows,'names':names_of_parameters}    
    meta_data.append(hashed)
    context={'meta_data':meta_data}
    print(context)
    return render(request,'show_table.html',context)

# def edit_name(request,pk):
#     db=mysql.connector.connect(
#     host="climateflux.com",
#     user="bishoykaleny",
#     port="3306",
#     passwd="01280408351",
#     database="climate_walk"
#     )
#     mycursor=db.cursor()
#     tables=[]
#     mycursor.execute("SHOW TABLES")
#     i=0
#     for table_name in mycursor:
#         table_name_corrected=str(table_name)[2:-3]
#         hashed={'id':i,'name':table_name_corrected}
#         tables.append(hashed)
#         i=i+1
#     table=None
#     for table_temp in tables:
#         if table_temp['id']==int(pk):
#             table = table_temp
#     tableeee=table['name']
#     if request.method == 'POST':
#         Day = request.POST.get('Day')
#         Hour = request.POST.get('Hour')
#     index=tableeee.find('_')
#     device_name=tableeee[0:index]
    
#     print(device_name)
#     day=tableeee[index+1:index+3]
#     tableeee[index+1:index+3]=Day
#     print(day)
#     hour=tableeee[index+12:index+14]
#     new_name=f""
#     mycursor.execute(f"ALTER TABLE {tableeee} RENAME TO ")

#     return

def home(request):
    return render(request,'home.html')


def get_location_data(lat, lon):
    geolocator = Nominatim(user_agent="geoapiExercises")
    location = geolocator.reverse(lat+","+lon)
    address = location.raw['address']
    city = address.get('city', '')
    country = address.get('country', '')
    code = address.get('country_code')
    return city, country, code

def get_sunpath_data(lat, lon,lat_fl,lon_fl,month,day,hour):
    # Get the location data
    city, country, code = get_location_data(lat, lon)



    # Create a Location object and a Sunpath object
    City = Location(country,city, code, latitude=lat_fl, longitude=lon_fl) #change time zone
    sp = Sunpath.from_location(City)

    # Calculate the sunpath data
    sun = sp.calculate_sun(month=int(month), day=int(day), hour=int(hour))
    return sun

# Define a function to get the altitude of the sun
def get_sun_altitude(lat, lon,lat_fl,lon_fl,month,day,hour):
    # Calculate the sunpath data
    sun = get_sunpath_data(lat, lon,lat_fl,lon_fl,month,day,hour)

    # Return the altitude of the sun
    return sun.altitude

# Define a function to get the azimuth of the sun
def get_sun_azimuth(lat, lon,lat_fl,lon_fl,month,day,hour):
    # Calculate the sunpath data
    sun = get_sunpath_data(lat, lon,lat_fl,lon_fl,month,day,hour)

    # Return the azimuth of the sun
    return sun.azimuth

def get_ber_alt(lat,long,lat_fl,lon_fl,month,day,hour):
    BerAlt=get_sun_altitude(lat,long,lat_fl,lon_fl,month,day,hour)
    
    return BerAlt

def Pfactor(SunAlt):
    return 0.308*(math.cos(math.radians(SunAlt)*(1 - math.pow(math.radians(SunAlt),2) / 48402)))





#MRT from Tglobe
D = 0.03 # globe diameter in meters
def mrt(Tg, Ta, W):
    return math.pow((math.pow((Tg + 273.15), 4)) + (1.1* math.pow(10, 8) * math.pow(W, 0.6) / (0.95 * math.pow(D, 0.4))) * (math.fabs(Tg - Ta)), 0.25) - 273.15

   
def MRT(mrt, Rad, PF):
    return math.pow((math.pow((mrt + 273), 4)) + ((abs(PF) * 0.7 * Rad) / (0.97 * 5.67 * math.pow(10, -8))), 0.25) - 273
