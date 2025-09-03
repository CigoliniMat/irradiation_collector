from model import database as db
from model import get_api
from datetime import datetime
import json


def insert_location(name:str,latitude:float,longitude:float,description:str=None) -> dict:
    """
    format the value for the database, then insert then in the database
    """
    max_lat = 90
    min_lat = -90
    max_lon = 180
    min_lon = -180
    result = {'success':False,'messagge':'','data':None}

    #check if longitude and latitude isn't to big or to small
    if not min_lat <= latitude <=max_lat:
        result['messagge'] = 'latitude value not valid'
        return result
    if not  min_lon <= longitude <= max_lon:
        result['messagge'] = 'longitude value not valid'
        return result
    
    db_result = db.insert_location(name,latitude,longitude,description)
    
    if not db_result['success']:
        return db_result

    result['success'] = True
    result['messagge'] = f'inserted location {name} correctly'
    return result

def download_irradiation() -> dict:
    '''
    for each location see the last irradiation date that we have
    and dowlaod the differecen from today
    save the data
    '''
    result = {'success':False,'message':'','data':None}
    db_result = db.get_locations_info()
    if db_result['success']:
        locations_list = db_result['data']
    else:
        return db_result
    
    min_date = '2005-01-01'

    for location in locations_list:
        id = location['id']
        latitude = location['lat']
        longitude = location['lon']

        db_result = db.get_last_irradiation_date(location_id=id)
        if not db_result['success']:
            return db_result
        
        if db_result['data']:
            start_date = db_result['data']
        else:
            start_date = min_date

        #split the intervall to max x year to avoid long api request time (take approximately 1 min for 5 year)
        year_span = 3
        today = datetime.now()
        start_date_obj = datetime.strptime(start_date,r'%Y-%m-%d')
        current_year = start_date_obj.year + year_span      

        times_intervall = []
        while current_year <= today.year:
            if current_year-year_span == start_date_obj.year:
                start = start_date_obj.strftime(r'%Y-%m-%d')
            else:
                start = f'{current_year}-01-01'

            if current_year >= today.year:
                end = today.strftime(r'%Y-%m-%d')
            else:
                end = f'{current_year}-12-31'
            
            times_intervall.append({'start':start,'end':end})

            current_year = current_year + year_span

        for time_intervall in times_intervall:
            start = time_intervall['start']
            end = time_intervall['end']
            api_result = get_api(start_date=start,
                                end_date=end,
                                lat=latitude,
                                lon=longitude)
            
            if not api_result['success']:
                return api_result
            
            irradiation_value = api_result['data']

            db_result = db.insert_irradiation(id,irradiation_value)
            if not db_result['success']:
                return db_result

            #with open(f'.t/api_output_{id}_{start}.json','w') as f:
                #json.dump(irradiation_value,f)

    result['message']='ok!'
    result['success'] =True
    return result

if __name__ == '__main__':
    result = download_irradiation()
    print(result)