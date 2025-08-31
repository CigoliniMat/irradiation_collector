import sqlite3, json
import os.path as path
import math

db_file = 'test.db'

def create_db(db_file=db_file) -> dict:
    """
    Create base database for the app
    """
    result={'success':False,'message':'','data':None}
    #format db name and add extension name if not specified
    #now useless, remove if useless in the end of the project
    db_file = db_file.lower()
    if db_file[-3:] != '.db':
        db_file = db_file + '.db'

    conn = None

    #if file already exists exit
    if path.exists(db_file):
        result['message'] = f'file {db_file} already exists, exit'
        return result

    try:
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()

        #create locations table
        cursor.execute("""
            CREATE TABLE locations (
                       id INTEGER PRIMARY KEY,
                       name TEXT NOT NULL,
                       lat REAL NOT NULL,
                       lon REAL NOT NULL,
                       description TEXT
                       )
            """)

        #create irradiation table
        cursor.execute("""
            CREATE TABLE irradiation (
                       id INTEGER PRIMARY KEY,
                       location_id INTEGER NOT NULL,
                       date_time TEXT NOT NULL,
                       dhi REAL NOT NULL,
                       bhi REAL NOT NULL,
                       FOREIGN KEY (location_id) REFERENCES location (id)
                       )
            """)
        
        #create index for speed up data filter
        cursor.execute("CREATE INDEX idx_location_id ON irradiation (location_id);")
        cursor.execute("CREATE INDEX idx_date_time ON irradiation (date_time);")

        conn.commit()
        result['success'] = True
        result['message'] = f'database {db_file} created successfully'

    except sqlite3.Error as e:
        result['message'] = f'error during database {db_file} creation: {e}'

    finally:
        if conn:
            conn.close()

    return result

def insert_location(name:str, lat:float, lon:float, description: str=None,db_file=db_file) -> dict:
    """
    insert location in locations table
    """
    result = {'success':False,'message':'','data':None}
    conn = None

    try:
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO locations (name, lat, lon, description)
                    VALUES (?,?,?,?)
            """, (name,lat,lon,description)
            )
        
        conn.commit()
        result['success'] = True
        result['message'] = f'location {name} added succesfully'

    except sqlite3.Error as e:
        result['message'] = f'error during location {name} insertion: {e}'
    finally:
        if conn:
            conn.close()

    return result

def insert_irradiation(location_id:int,data:list,db_file=db_file) -> dict:
    """
    Insert irradiation value in irradiation table
    Args:
        location_id: self explanined
        date_time: local date time in format ISO 8601 (YYYY-MM-DD T HH:mm:ss), excepted precision to hour
        dhi: diffuse irradiation on orizzontal plane (W/m2)
        bhi: beam irradiation on orizzontal plane (W/m2)
    """
    result = {'success':False,'message':'','data':None}

    with open('test.json', 'r') as f:
            data = json.load(f)

    data_to_pull = []
    for record in data:
        dhi = record['dhi']
        bhi = record['bhi']
        date = record['date']
        #choose if set it to 0 or skip
        if math.isnan(dhi):
            continue
        if math.isnan(bhi):
            continue

        data_to_pull.append((location_id,date,dhi,bhi))
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()

        cursor.executemany("""
                    INSERT INTO irradiation (location_id, date_time, dhi, bhi)
                    VALUES (?, ?, ?, ?)
                """,data_to_pull)
        
        conn.commit()
        
        result['success'] = True
        result['message'] = 'irradiation data insert correctly'
    except sqlite3.Error as e:
        result['message'] = f'error during saving irradiation data in database: {e}'
    finally:
        if conn:
            conn.close()
    return result


def get_locations_info(db_file=db_file) -> dict:
    '''
    Return a dict with all the info of the locations
    output: [{'name':'Montichiari (BS)','lat':12.56,'lon':34.67,'description':''},{...},...]
    '''
    result = {'success':False,'message':'','data':None}
    conn = None
    data_output = []
    try:
        conn = sqlite3.connect(db_file)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM locations")

        rows = cursor.fetchall()

        for row in rows:
            data_output.append(dict(row))
        

        #with open('.t/get_all_location_output.json','w') as f:
            #json.dump(data_output,f)

        result['success'] = True
        result['message'] = 'got locations info successfully'
        result['data'] = data_output
    except sqlite3.Error as e:
        result['message'] = f'error in database: {e}'
    finally:
        if conn:
            conn.close()

    return result

def get_last_irradiation_date(location_id,db_file=db_file) -> dict:
    result = {'success':False,'message':'','data':None}
    conn = None
    last_datetime = None
    try:
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()

        instruction = """
        SELECT MAX (date_time)
        FROM irradiation
        WHERE location_id = ?
        """

        cursor.execute(instruction,(location_id,))

        value = cursor.fetchone()

        if value and value[0]:
            last_datetime = value[0]
            result['message'] = 'finded last date successfully'
            result['data'] = last_datetime
        else:
            result['message'] = 'no data founded'
            result['data'] = None
        result['success'] = True
    except sqlite3.Error as e:
        result['message'] = f'Error in database: {e}'
    
    return result




if __name__ == '__main__':
    result = insert_irradiation(1,[])
    print(result)