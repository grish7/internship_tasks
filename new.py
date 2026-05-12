import  psycopg2
import json 
import sys
import logging

# logger = logging.getLogger(__name__)
# # 1-database connection
# try:
#     conn = psycopg2.connect(
#                 dbname= "postgres",
#                 user= "postgres",
#                 password= "1234",
#                 host= "localhost",
#                 port= "5432"
#             )
#     logging.info("Connected successfully")
    
# except Exception as e:
#     logging.error(f"connaction error: {e}")


# cursor = conn.cursor()

# # 2-creating table of rooms

# try:
#     cursor.execute(''' 
#         CREATE TABLE IF NOT EXISTS rooms(
#                 id SERIAL PRIMARY KEY NOT NULL,
#                 name VARCHAR(50)
#                 )
#                 ''')
#     logging.info("Table is created successfully")
#     conn.commit()
# except Exception as e:
#     logging.error(f"error: {e}")
#     conn.rollback()



# # 3-creating students table

# try:
#     cursor.execute(''' 
#         CREATE TABLE IF NOT EXISTS students(
#                 id SERIAL PRIMARY KEY NOT NULL,
#                 name VARCHAR(50),
#                 birthday DATE,
#                 room INT REFERENCES rooms(id),
#                 sex CHAR(1)
#                 )
#                 ''')
#     logging.info('table is created')
#     conn.commit()
# except Exception as e:
#     logging.error(f"error: {e}")
#     conn.rollback()


# # 4-loading JSON file
    
# # print(sys.version)
# rooms_file = sys.argv[1]
# students_file = sys.argv[2]
# output_format = sys.argv[3]

# with open(rooms_file,"r", encoding= "utf-8") as file :
#         data_rooms = json.load(file)

# with open(students_file,"r", encoding= "utf-8") as file :
#         data_students = json.load(file)




# # 5-insert the data into the rooms's table
        
# try:
#     for item in data_rooms:
#         cursor.execute(''' 
#             INSERT INTO rooms(id, name)
#             VALUES(%s, %s)    
#             ON CONFLICT (id) DO NOTHING
#         ''', (item['id'], item['name']))
#     logging.info("insert")
#     conn.commit()
# except Exception as s:
#     logging.error(f"error: {e}")
#     conn.rollback()


# # 6-inserting the data into the students's table
# try:
#     for item in data_students:
#         cursor.execute(''' 
#             INSERT INTO students(id, name, birthday, room, sex)
#             VALUES(%s, %s, %s, %s, %s) 
#             ON CONFLICT (id) DO NOTHING
#         ''', (item['id'], item['name'], item['birthday'], item['room'], item['sex']))
#     logging.info("insert the data")
#     conn.commit()
# except Exception as s:
#     logging.error(f"error: {e}")
#     conn.rollback()


# # 7- adding indxes

# try:
#     cursor.execute(''' 
#             CREATE INDEX IF NOT EXISTS idx_students_room
#             ON students (room)
#         ''')
#     logging.info("indexes're created")
#     conn.commit()
# except Exception as e:
#     logging.error(f"error: {e}")


# try:
#     cursor.execute('''
#             CREATE INDEX IF NOT EXISTS idx_students_birthday
#             ON students (birthday)
#         ''')
#     logging.info("the index is created")
#     conn.commit()
# except Exception as e:
#     logging.error(f"error: {e}")

# # Query 1:
# # List of rooms and the number of students in each of them

# try:
#     cursor.execute(''' 
#         SELECT 
#             r.name,
#             COUNT(s.id) as number_of_students
#         FROM rooms r
#         JOIN students s ON r.id =  s.room
#         GROUP BY r.id
#         ORDER BY number_of_students 
#     ''')
#     res_1 = cursor.fetchall()
   
#     # for row in res_1:
#     #     print("amount of students: ",row[1])
#     #     print("room number: ",row[0])
#     #     print("\n")


#     # print(type(res_1))     # 'list'
#     # print(type(res_1[0]))  # 'tuple'

#     logging.info("Query_1 is completed")

# except Exception as e:
#     logging.error(f"error 'query': {e}")
    



# # Query 2:
# # 5 rooms with the smallest average age of students
# try:
#     cursor.execute(''' 
#         SELECT 
#             room,
#             FLOOR( AVG(EXTRACT(YEAR FROM age(NOW(), birthday)))) as avg_age
#         FROM students
#         GROUP BY room
#         ORDER BY avg_age
#         LIMIT 5
#     ''')
#     res_2 = cursor.fetchall()
#     # print(res_2)

#     logging.info("Query_2 is completed")

# except Exception as e:
#     logging.error(f"error 'query_2': {e}")
    
# # Query 3:
# # 5 rooms with the largest difference in the age of students
    
# try:
#     cursor.execute('''
#         SELECT 
#             room,
#             EXTRACT(YEAR FROM AGE(MAX(birthday),MIN(birthday))) AS difference_age
#         FROM students
#         GROUP BY room
#         ORDER BY difference_age DESC
#         LIMIT 5
#     ''')
#     res_3 = cursor.fetchall()
#     logging.info('Query_3 is completed')
# except Exception as e:
#     logging.error(f"error 'query_3': {e}")

#     # Query 4:
# # List of rooms where different-sex students live

# try:
#     cursor.execute(''' 
#         SELECT 
#             room
#         FROM students
#         GROUP BY room
#         HAVING COUNT(DISTINCT sex) > 1
#     ''')
#     res_4 = cursor.fetchall()
#     # for row in res_4:
#     #     print('room: ', row)
#     #     print("\n")
#     logging.info("Query_4 is completed")

# except Exception as e:
#     logging.error(f" error 'query_4': {e}")



# # n = len(sys.argv)
# # print(sys.argv[0])
# # print(sys.path)



# #======= 

# def transform_results(data,keys):
#         return [dict(zip(keys, row)) for row in data]

# result_query_1 = transform_results(res_1, ['room_name', 'students_count'])
# result_query_2 = transform_results(res_2, ['room_id', 'average_age of students'])
# result_query_3 = transform_results(res_3, ['room_id', 'age difference'])
# result_query_4 = transform_results(res_4, ['room_id'])

# # 

# results ={
#     'query_1': result_query_1,
#     'query_2': result_query_2,
#     'query_3': result_query_3,
#     'query_4': result_query_4
# }
# # saving  json file
# try:
#     with open('output.json', 'w', encoding='utf-8' )as f:
#         json.dump(results, f, indent=2, default=str, ensure_ascii=False)
#     logging.info('results are saved')

# except Exception as e:
#     logging.error(f'error: {e}')
        


# cursor.close()
# conn.close()



#!========================== OOP ===============================

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
            logging.info("Connected successfully")
            return self.conn
        except Exception as e:
            logging.error(f"connaction error: {e}")
            return False
        
    def close(self):
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()

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
        output_format = sys.argv[3]

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
            logging.info("insert the data")
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
            logging.info("indexes are created")
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
            logging.info("Queries are completed")
            
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
    main()

