import models as m
import math
from datetime import datetime

#maybe add a setting json file for these variable?
skip_nan_irradiation_value = True #choose if skip or set to 0 the void irradiation, see after the chart generation
description_max_len = 150
name_max_len = 60
first_data_avaiable = '2005-01-01T00:59:59'

def get_locations_info()->dict['success':bool,'message':str,'data':list[dict]]:
    """
    probably this will be the first database function call by the the gui,
    evaluate if add here the creation of the external dabatase if doesn't exists

    Return a dict with all the info of the locations
    output: [{'id':1,'name':'Montichiari (BS)','latitude':12.56,'longitude':34.67,'description':''},{...},...]
    """
    result = {'success':False,'message':'','data':None}

    result = m.check_db()
    if not result['success']:
        return result
    
    result = m.get_location_list()
    if not result['success']:
        return result
    
    output = [] #create a list of  dict with the info of the location in database
    location_list = result['data']
    for location in location_list:
        output.append(dict(location))

    result = {'success':True,
              'message':'location list exported correctly',
              'data':output}
    
    return result

def get_last_irradiation_date(location_id:int)->dict['success':bool,'message':str,'data':]:
    '''
    output = date in ISO 8601 format with day precision "2005-01-01" not "2005-01-01T00:59:59"
    '''
    result = {'success':False,'message':'','data':None}

    result = m.check_db()
    if not result['success']:
        return result
    
    #add a check if location id exists???
    
    result = m.get_last_irradiation_date(location_id=location_id)
    if not result['success']:
        return result
    
    value = result['data']

    #if value exist set it to 
    if value and value[0]:
        last_dateT = value[0]
    else:
        last_dateT = first_data_avaiable
    
    #cut off the hour from the database date and check if is a date format (maybe a useless check)
    try:
        dt = datetime.fromisoformat(last_dateT)
    except Exception as e:
        result = {'success':False,
                  'message':f'error during reading database date: {e}','data':None}
        return result

    last_date = dt.strftime(r'%Y-%m-%d')   
    
    result = {'success':True,'message':f'last date of location {location_id} get correctly','data':last_date}
    return result

def add_location(name:str, latitude:float, longitude:float, description: str=None
                 ) -> dict['success':bool,'message':str,'data':]:
    """
    """
    result = {'success':False,'message':'','data':None}

    result = m.check_db()
    if not result['success']:
        return result
    
    if len(name) > name_max_len:
        result['message'] = f'localion name {name[0:20]}... is too long, please use less then {name_max_len} character'
        return result

    if description and len(description) > description_max_len: #if decription exist and then if description len > max
        result['message'] = f'description is too long, please use less then {description_max_len} character'
        return result
    
    if not -90 <= latitude <= +90:
        result['message'] = f'latitude must be more then -90 and less then +90'
        return result
    
    if not -180 <= latitude <= +180:
        result['message'] = f'longitude must be more then -180 and less then +180'
        return result
    
    result = m.insert_location(name=name,
                      latitude=latitude,
                      longitude=longitude,
                      description=description)
    
    return(result)

def add_irradiation(location_id:int,data:dict
                    ) -> dict['success':bool,'message':str,'data':]:
    """
    """
    result = {'success':False,'message':'','data':None}
    result = m.check_db()
    if not result['success']:
        return result
    
    data_to_save = []

    #check if the given dict is correct, it shouldn't be necessary because it came from backend
    try:
        data[0]['dhi']
        data[0]['bhi']
        data[0]['date']
    except:
        result = {'success':False,
                  'message':"irradiations data to insert in the database isn't in the correct format",
                  'data':None}
        return result

    for record in data:
        dhi = record['dhi']
        bhi = record['bhi']
        date = record['date']
        #!!!!!!!!!!!!!!!!!!!!!!!!!!
        #add check for date format, it shouldn't be necessary because it is alreadey be verified in api process

        #check if a irradiation value is Nan, if yes skip (choose if set it to 0 or skip)
        if math.isnan(dhi) or math.isnan(bhi):
            if skip_nan_irradiation_value:
                continue
            else:
                dhi = 0
                bhi = 0
        
        data_to_save.append((location_id,date,dhi,bhi))
    
    result = m.insert_irradiation(data=data_to_save)
    return(result)


if __name__ == '__main__':
    '''testing'''
    print(get_locations_info()['data'])