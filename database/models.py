import sqlite3
import os.path as path

#maybe add a setting json file for these variable?
db_path = 'database/database.db'

def check_db() -> dict['success':bool,'message':str,'data':]:
    result={'success':False,'message':'','data':None}
    if path.exists(db_path):
        result['success'] = True
        result['message'] = f'file {db_path} exists, exit'
        return result
    result['message'] = f"file {db_path} doesen't exists, exit"
    return result

def create_bd() -> dict['success':bool,'message':str,'data':]:
    result={'success':False,'message':'','data':None}

    conn = None

    #if file already exists exit
    if path.exists(db_path):
        result['message'] = f'file {db_path} already exists, exit'
        return result
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        #create locations table
        cursor.execute("""
            CREATE TABLE locations (
                       id INTEGER PRIMARY KEY,
                       name TEXT NOT NULL,
                       latitude REAL NOT NULL,
                       longitude REAL NOT NULL,
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
        result['message'] = f'database {db_path} created successfully'

    except sqlite3.Error as e:
        result['message'] = f'error during database {db_path} creation: {e}'

    finally:
        if conn:
            conn.close()

    return result

def insert_location(name:str, latitude:float, longitude:float, description: str=None
                    ) -> dict['success':bool,'message':str,'data':]:
    """
    insert location in locations table
    """
    result = {'success':False,'message':'','data':None}
    conn = None

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO locations (name, lat, lon, description)
                    VALUES (?,?,?,?)
            """, (name,latitude,longitude,description)
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

def get_location_list()-> dict['success':bool,'message':str,'data':list]:
    """
    """
    result = {'success':False,'message':'','data':None}
    conn = None
    data_output = []
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM locations")

        output = cursor.fetchall()

        result['success'] = True
        result['message'] = 'got locations list'
        result['data'] = output
    except sqlite3.Error as e:
        result['message'] = f'error in database: {e}'
    finally:
        if conn:
            conn.close()

    return result

def insert_irradiation(data:list) -> dict['success':bool,'message':str,'data':]:
    """
    Insert massive irradiation value in irradiation table
    Args:
        data = list [
                    (locationid,date,dhi,bhi),
                    (int,str,float,float),
                    (1,"2025-12-31T24:59:59",12.45,45.67)
                    ]
    """
    result = {'success':False,'message':'','data':None}

    conn = None
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.executemany("""
                    INSERT INTO irradiation (location_id, date_time, dhi, bhi)
                    VALUES (?, ?, ?, ?)
                """,data)
        
        conn.commit()
        
        result['success'] = True
        result['message'] = 'irradiation data insert correctly'
    except sqlite3.Error as e:
        result['message'] = f'error during saving irradiation data in database: {e}'
    finally:
        if conn:
            conn.close()
    return result

def get_last_irradiation_date(location_id) -> dict['success':bool,'message':str,'data':]:
    result = {'success':False,'message':'','data':None}
    conn = None

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        #use select max because date with ISO 8601 are self ordered by date
        instruction = """
        SELECT MAX (date_time)
        FROM irradiation
        WHERE location_id = ?
        """

        cursor.execute(instruction,(location_id,))
        value = cursor.fetchone()
        result = {'success':True,'message':f'last day of location {location_id} get correctly','data':value}

    except sqlite3.Error as e:
        result['message'] = f'Error in database: {e}'
    finally:
        if conn:
            conn.close()
        return(result)

if __name__ == '__main__':
    '''testing'''
    print(create_bd())