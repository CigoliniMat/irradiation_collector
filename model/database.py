from classes import Result
import sqlite3
import os.path as path

db_file = 'test.db'

def create_db():
    """
    Create base database for the app
    """

    #format db name and add extension name if not specified
    #now useless, remove if useless in the end of the project
    db_file = db_file.lower()
    if db_file[-3:] != '.db':
        db_file = db_file + '.db'

    conn = None

    #if file already exists exit
    if path.exists(db_file):
        return Result(False,f'file {db_file} already exists, exit')

    try:
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        print(f'connected to {db_file} database successfully')

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

    except sqlite3.Error as e:
        return Result(False, f'error during database {db_file} creation: {e}')
    finally:
        if conn:
            conn.close()
            return Result(True,f'database {db_file} created successfully')

def insert_location(name:str, lat:float, lon:float, description: str=None):
    """
    insert location in locations table
    """

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
        return Result(True, 'location {name} added succesfully')

    except sqlite3.Error as e:
        return Result(False,f'error during location {name} insertion: {e}')
    finally:
        if conn:
            conn.close()

def insert_irradiation(location_id:int,date_time:str,dhi:float,bhi:float):
    """
    Insert irradiation value in irradiation table
    Args:
        location_id: self explanined
        date_time: local date time in format ISO 8601 (YYYY-MM-DD T HH:mm:ss), excepted precision to hour
        dhi: diffuse irradiation on orizzontal plane (W/m2)
        bhi: beam irradiation on orizzontal plane (W/m2)
    """
    # verify date_time 
    return Result(True,'irradiation added succesfully')
    
if __name__ == '__main__':
    pass