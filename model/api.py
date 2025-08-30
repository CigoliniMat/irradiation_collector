from classes import Result
import urllib.request as request #check internet connection
import xarray as xr #to read .nc file
import cdsapi #api
import json, os
from datetime import datetime

#safe site for check if there is internet connection
#if google failed change it

safe_host = 'http://google.com'

def safe_api_keys(url: str,key:str) -> Result: #optional
    '''
    from given url and key create the file needed for the api to work,
    maybe only with (url is always the same)
    '''

def get_api(start_date:str,end_date:str,
        lon:float,lat:float,
        file_position:str='.t/api_file.nc',testing:bool=False) -> Result:
    '''
    Get data from api
    Args:
        start_date: start intervall date format 'YYYY-MM-DD'
        end_date: end intervall date format 'YYYY-MM-DD' -> always set to today
        lon: longitude
        lat: latuitude
        file_positon: where the file .nc will be temporarily saved

    output: [{date:'',dhi:12.56,bhi:34.67},{...}]
    '''
    data_output = [] #list of dict [{'date':'2005-01-01T01:00:00,'dhi':12.56,'bhi':34,56},{...},...]

    #check internet connection
    try:
        request.urlopen(safe_host, timeout=10)
    except Exception as e:
        return Result(False,f'unable to connect to internet: {e}')
    
    #api setting
    client = cdsapi.Client()
    dataset = 'cams-solar-radiation-timeseries'
    params = {"sky_type": "observed_cloud",
                "location": {"longitude": lon, "latitude": lat},
                "altitude": ["-999."], #???
                "date": [f"{start_date}/{end_date}"],
                "time_step": "1hour", #options = 1minute, 15minute, 1hour, 1day, 1month
                "time_reference": "true_solar_time", #universal_time or true_solar_time
                "format": "netcdf" #NETCDF, but can be switched to csv
                }
    
    #api call
    try:
        client.retrieve(dataset,params,file_position)
    except Exception as e:
        return Result(False,f'error during api call: {e}')
    
    ds = xr.open_dataset(file_position)
    time_ds = ds['time'].values
    dhi_ds = ds['DHI'].squeeze()
    bhi_ds = ds['BHI'].squeeze()
    iso_format = r'%Y-%m-%dT%H:%M:%S'

    for time in time_ds:
        date = time[:13] + ':59:59'
        #time = 2025-08-01T23:24:45.000000000, date = 2025-08-01T23:59:59
        #set :59:59 for a better clarity (the value is the sum of every minute for the previus value until this)
        #the api base minute instead is not the last minute (i don't know why)

        #check if the date is a correct format, if not go to next loop
        try:
            datetime.strptime(date, iso_format)
        except:
            continue

        dhi = dhi_ds.sel(time=time).values
        bhi = bhi_ds.sel(time=time).values

        data_output.append({'date':date,'dhi':dhi,'bhi':bhi})
    
    ds.close()

    if not testing:
        os.remove(file_position)
    else:
        with open('.t/api_output.json','w') as f:
            json.dump(data_output,f)

    return Result(True,'irradiation correctly dowloaded and readed',data_output)

if __name__ == '__main__':
    pass
    





