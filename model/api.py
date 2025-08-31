import urllib.request as request #check internet connection
import xarray as xr #to read .nc file
import cdsapi #api
import json, os
import pandas as pd
from datetime import datetime

#safe site for check if there is internet connection
#make sure site is on-line
safe_host = 'http://google.com'

def safe_api_keys(url: str,key:str) -> json: #optional
    '''
    from given url and key create the file needed for the api to work,
    maybe only with (url is always the same)
    '''
    result = {'success':False,'message':'','data':None}

def get_api(start_date:str,end_date:str,
        lon:float,lat:float,
        file_position:str='.t/api_file.nc') -> json:
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
    result = {'success':False,'message':'','data':None}
    data_output = [] #list of dict [{'date':'2005-01-01T01:00:00,'dhi':12.56,'bhi':34,56},{...},...]

    #check internet connection
    try:
        request.urlopen(safe_host, timeout=10)
    except Exception as e:
        result['message'] = f'unable to connect to internet: {e}'
        return result
    
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
        result['message'] = f'error during api call: {e}'
        return result
    
    try:
        ds = xr.open_dataset(file_position)
        dhi_ds = ds['DHI'].squeeze()
        bhi_ds = ds['BHI'].squeeze()

        dataframe = pd.DataFrame({
                    'dhi': dhi_ds.values,
                    'bhi': bhi_ds.values
                    }, index=dhi_ds.time.values)
        
        dataframe.index = pd.to_datetime(dataframe.index).floor('h')
        dataframe.index = dataframe.index.strftime(r'%Y-%m-%dT%H:59:59')

        dataframe.index.name = 'date'

        data_output = dataframe.reset_index().to_dict(orient='records')

    except Exception as e:
        result['message'] = f'error during dataset conversion: {e}'
        return result
    finally:
        if 'ds' in locals():
            ds.close()
        os.remove(file_position)

    result['success'] = True
    result['message'] = 'irradiation correctly dowloaded and readed'
    result['data'] = data_output
    return result

if __name__ == '__main__':
   pass






