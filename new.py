import  psycopg2
import json 
import sys
import logging



#============== step 1 ============

class DatabaseConnection:
    def __init__(self,dbname,user,password,host,port):
        self.conn = None
        self.cursor = None
        self.config = {
            'dbname' : dbname,
            'user' : user,
            'password': password,
            'host': host,
            'port': port
        }
        
    
    def connect(self):
        try:
            self.conn = psycopg2.connect(**self.config)
            logging.info("successfully")
            return self.conn
        except Exception as e:
            logging.error(f"connection error: {e}")
            return False
        
    def close(self):
        if self.cursor:
            self.cursor.close()
            self.cursor = None
        if self.conn:
            self.conn.close()
            self.conn = None

    def commit(self):
        self.conn.commit()

    def get_cursor(self):
        self.cursor = self.conn.cursor()
        return self.cursor


#================== step 2 ======================
    
class TableCreator:
    def __init__(self,cursor, conn):
        self.cursor = cursor 
        self.conn = conn
        
    query_rooms = ''' 
        CREATE TABLE IF NOT EXISTS rooms(
                id SERIAL PRIMARY KEY NOT NULL,
                name VARCHAR(50)
                )
        '''
    query_students = '''
        CREATE TABLE IF NOT EXISTS students(
                id SERIAL PRIMARY KEY NOT NULL,
                name VARCHAR(50),
                birthday DATE,
                room INT REFERENCES rooms(id),
                sex CHAR(1)
                )
        '''
    def create_table(self):
        try:
            self.cursor.execute(self.query_rooms)
            self.cursor.execute(self.query_students)
            logging.info("Tables are created successfully")
            self.conn.commit()
            return True
        except Exception as e:
            logging.error(f"error: {e}")
            self.conn.rollback()
            return False

# ========== step 3 ======= 


class DataInserter:
    def __init__(self, cursor,conn):
        self.cursor = cursor
        self.conn = conn 

    query_insert_rooms = '''
        INSERT INTO rooms(id, name)
        VALUES(%s, %s)    
        ON CONFLICT (id) DO NOTHING
    '''
    query_insert_students = '''
        INSERT INTO students(id, name, birthday, room, sex)
        VALUES(%s, %s, %s, %s, %s) 
        ON CONFLICT (id) DO NOTHING
    '''

    def get_data(self):
        rooms_file = sys.argv[1]
        students_file = sys.argv[2]
        # output_format = sys.argv[3]

        with open(rooms_file,"r", encoding= "utf-8") as file :
            data_rooms = json.load(file)

        with open(students_file,"r", encoding= "utf-8") as file :
            data_students = json.load(file)

        return data_rooms, data_students


    def insert_data(self,data_rooms,data_students):
        try:
            for item in data_rooms:
                self.cursor.execute(self.query_insert_rooms , (item['id'], item['name']))
            for item in data_students:
                self.cursor.execute(self.query_insert_students, (item['id'], item['name'], item['birthday'], item['room'], item['sex']))
            logging.info("ok")
            self.conn.commit()    
            return True
        except Exception as e:
            logging.error(f"error: {e}")
            self.conn.rollback()
            return False

# ========== step 4 ======= 
        
class IndexCreator:
    def __init__(self,cursor, conn):
        self.cursor = cursor
        self.conn = conn 

    query_1 = '''
        CREATE INDEX IF NOT EXISTS idx_students_room
        ON students (room)
        '''
    
    query_2 = '''
        CREATE INDEX IF NOT EXISTS idx_students_birthday
        ON students (birthday)
        '''
    
    def create_index(self):
        try:
            self.cursor.execute(self.query_1)
            self.cursor.execute(self.query_2)
            logging.info("ok")
            self.conn.commit()
            return True
        except Exception as e:
            logging.error(f"error: {e}")
            return False

# ========== step 5 ======= 
            
class QueryExecutor:
    def __init__(self, cursor, conn):
        self.cursor = cursor 
        self.conn = conn 

    queries = [
        '''
        SELECT 
            r.name,
            COUNT(s.id) as number_of_students
        FROM rooms r
        JOIN students s ON r.id =  s.room
        GROUP BY r.id
        ORDER BY number_of_students 
        ''',

        '''
        SELECT 
            room,
            FLOOR( AVG(EXTRACT(YEAR FROM age(NOW(), birthday)))) as avg_age
        FROM students
        GROUP BY room
        ORDER BY avg_age
        LIMIT 5
        ''',

        '''
        SELECT 
            room,
            EXTRACT(YEAR FROM AGE(MAX(birthday),MIN(birthday))) AS difference_age
        FROM students
        GROUP BY room
        ORDER BY difference_age DESC
        LIMIT 5
        ''',

        '''
        SELECT 
            room
        FROM students
        GROUP BY room
        HAVING COUNT(DISTINCT sex) > 1
        '''
        ]

    def execute_all_queries(self):
        try:
            result = []
            for item in self.queries:
                self.cursor.execute(item)
                res = self.cursor.fetchall()
                result.append(res)
            logging.info("ok")
            
        except Exception as e:
            logging.error(f"error 'query': {e}")
            
        return result 



# ========== step 6 ======= 

class ResultTransformer:
    def __init__(self,cursor, conn,result):
        self.cursor = cursor
        self.conn = conn 
        self.result =result
        
    
    def transform(self, data,keys):
        return [dict(zip(keys, row)) for row in data]
    

    def transform_all(self):
        result_query_1 = self.transform(self.result[0], ['room_name', 'students_count'])
        result_query_2 = self.transform(self.result[1], ['room_id', 'average_age of students'])
        result_query_3 = self.transform(self.result[2], ['room_id', 'age difference'])
        result_query_4 = self.transform(self.result[3], ['room_id'])
        
        results ={
            'query_1': result_query_1,
            'query_2': result_query_2,
            'query_3': result_query_3,
            'query_4': result_query_4
            }
        return results


# ========== step 7 ======= 

class JsonSaver:
    def __init__(self,cursor, conn):
        self.cursor = cursor
        self.conn = conn 

    def save_json_file(self,results):
        try:
            with open('output.json', 'w', encoding='utf-8' )as f:
                json.dump(results, f, indent=2, default=str, ensure_ascii=False)
            logging.info('results are saved')
            return True
        except Exception as e:
            logging.error(f'error: {e}')
            return False
        
#================= step 8 ===============

def main():
    logging.basicConfig(level=logging.INFO)

    db = DatabaseConnection("postgres","postgres","1234","localhost","5432")
    db.connect()
    cursor =db.get_cursor()

    table_creator = TableCreator(cursor, db.conn)
    table_creator.create_table()

    data_inserter = DataInserter(cursor, db.conn)
    data_rooms, data_students = data_inserter.get_data()
    data_inserter.insert_data(data_rooms, data_students)

    index_creator = IndexCreator(cursor, db.conn)
    index_creator.create_index()

    query_executor = QueryExecutor(cursor, db.conn)
    query_results = query_executor.execute_all_queries()

    if query_results:
        transformer = ResultTransformer(cursor, db.conn, query_results)
        transformed_results = transformer.transform_all()

        json_saver = JsonSaver(cursor, db.conn)
        json_saver.save_json_file(transformed_results)

    db.close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit()
    main()

