import psycopg2
import json 
import sys
import logging
import os
from queries import (
                    ALL_QUERIES as queries,
                    QUERIES_ROOMS as query_rooms,
                    QUERIES_STUDENTS as query_students,
                    QUERY_INSERT_ROOMS as query_insert_rooms,
                    QUERY_INSERT_STUDENTS as query_insert_students,
                    CREATE_INDEX_1 as create_index_1,
                    CREATE_INDEX_2 as create_index_2
                    )


class DatabaseConnection:
    '''The DatabaseConnection with context manager support'''

    def __init__(self, dbname: str, user: str, password: str, host: str, port: str)-> None:
        self.conn = None
        self.cursor = None
        self.config = {
            'dbname' :os.getenv(dbname, 'my_db'),
            'user' : os.getenv(user,'postgres'),
            'password': os.getenv(password, ''),
            'host': os.getenv(host, 'localhost'),
            'port': os.getenv(port, '5432')
        }
    
    def __enter__(self):
        '''Enter context manager and establish database connection'''
        
        self.connect()
        logging.info('entering context manager')
        
        return self

    def __exit__(self, exc_type, exc_val, exc_tb)-> bool:
        '''Exit context manager and close connection'''
        
        if exc_type is not None:
            logging.error(f"Error occurred: {exc_val}")
            self.conn.rollback()
        else:
            self.conn.commit()

        self.close()
        
        return False
    
    def connect(self)-> psycopg2.extensions.connection:
        '''Establish database connection using stored configuration'''
        
        try:
            self.conn = psycopg2.connect(**self.config)
            logging.info("Database connection established")
            return self.conn
        except psycopg2.OperationalError as e:
            logging.error(f"connection error: {e}")
            raise 
        
    def close(self)-> None:
        '''Close database cursor and connection'''
        
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()

    def commit(self)-> None:
        '''Commit current transaction to the database'''
        
        self.conn.commit()

    def get_cursor(self)-> psycopg2.extensions.cursor:
        '''Create and return database cursor'''
        
        self.cursor = self.conn.cursor()
        return self.cursor
    

class TableCreator:
    '''Create tables in the database'''
    
    def __init__(self,cursor: psycopg2.extensions.cursor)-> None:
        self.cursor = cursor 

    def create_table(self)-> bool:
        '''Create rooms and students tables in the database'''
        
        try:
            self.cursor.execute(query_rooms)
            self.cursor.execute(query_students)
            logging.info("Tables created successfully")
            return True
        except psycopg2.Error as e:
            logging.error(f"Error creating tables: {e}")
            raise


class DataInserter:
    '''Handles data insertion from JSON files into the database'''
    
    def __init__(self, cursor: psycopg2.extensions.cursor)-> None:
        self.cursor = cursor
    
    @staticmethod
    def get_data()-> list:
        '''Load and parse JSON data from room and student files'''
        
        rooms_file = sys.argv[1]
        students_file = sys.argv[2]

        with open(rooms_file, "r", encoding= "utf-8") as file :
            data_rooms = json.load(file)

        with open(students_file, "r", encoding= "utf-8") as file :
            data_students = json.load(file)
        
        return data_rooms, data_students

    def insert_rooms(self, data_rooms: list[dict])-> bool:
        '''Insert room records into the database '''
        
        try:
            args = ((item['id'], item['name']) for item in data_rooms)
            self.cursor.executemany(query_insert_rooms , args)
            logging.info("Room data inserted successfully")
            return True
        except psycopg2.Error as e:
            logging.error(f"Error inserting room: {e}")
            raise
        
    def insert_students(self, data_students: list[dict])-> bool:
        '''Insert student records into the database'''
        
        try:
            args = ((item['id'], item['name'], item['birthday'], item['room'], item['sex']) for item in data_students)
            self.cursor.executemany(query_insert_students, args)
            logging.info("Student data inserted successfully")
            return True
        except psycopg2.Error as e:
            logging.error(f"Error inserting students: {e}")
            raise
        

class IndexCreator:
    '''Creates database indexes'''
    
    def __init__(self,cursor: psycopg2.extensions.cursor)-> None:
        self.cursor = cursor
    
    def create_index(self)-> bool:
        try:
            self.cursor.execute(create_index_1)
            self.cursor.execute(create_index_2)
            logging.info("Indexes created successfully")
            return True
        except psycopg2.Error as e:
            logging.error(f"Error creating indexes: {e}")
            raise
            

class QueryExecutor:
    '''Executes analytical queries on the database'''
    
    def __init__(self, cursor: psycopg2.extensions.cursor)-> None:
        '''Initialize QueryExecutor with database cursor and connection'''
        
        self.cursor = cursor 

    def execute_all_queries(self)-> list[list[tuple]]:
        '''Execute all queries and collect resullt'''
        
        try:
            result = []
            for item in queries:
                self.cursor.execute(item)
                description = self.cursor.description  
                column_names = [col.name for col in description]
                res = self.cursor.fetchall()
                result.append((column_names,res))
            logging.info("Queries executed successfully")
        except psycopg2.Error as e:
            logging.error(f"Error executing queries: {e}")
            raise
        
        return result


class ResultTransformer:
    '''Transform query results into structured dictionary format'''
    
    def __init__(self, result:list[tuple])-> None:
        '''Initialize ResultTransformer with database and query results'''
        
        self.result =result
        
    @staticmethod 
    def transform(data: list[tuple], description: tuple)-> list[dict]:
        '''Transform a list of tuples into a list of dictionaries'''
        
        try:
            if not data:
                return []
            else:
                column_names = [item for item in description]
                result_list = [dict(zip(column_names, row)) for row in data]
                return result_list
        except TypeError as e:
            logging.error(f'Type error during transform: {e}')
            raise

    def transform_all(self, result_list:list)-> dict[list[dict]]:
        '''Transform all query results into named dictionary structure'''
        
        try:
            results ={}
            for i in range(len(self.result)):
                key = f'query_{i+1}'
                results[key] = self.transform(self.result[i],result_list[i])
            return results
        except TypeError as e:
            logging.error(f'Type Error during transform all results: {e}')


class JsonSaver:
    '''Saved transformed results to JSON file'''
    
    @staticmethod
    def save_json_file(results: dict[list[dict]])-> bool:
        '''Save transformed results to output.json file'''

        try:
            with open('output.json', 'w', encoding='utf-8' )as f:
                json.dump(results, f, indent=2, default=str, ensure_ascii=False)
            logging.info('Results saved to output.json file')
            return True
        except TypeError as e:
            logging.error(f'Non-serializable data in results: {e}')
            raise


def main()->None:
    '''Main execution function'''

    if len(sys.argv) < 3:
        logging.error('Please provide both JSON files')
        sys.exit()

    logging.basicConfig(level=logging.INFO)

    try:
        with DatabaseConnection('DB_NAME','DB_USER', 'DB_PASSWORD', 'DB_HOST', 'DB_PORT') as db:
            cursor =db.get_cursor()

            '''Create tables'''
            table_creator = TableCreator(cursor)
            table_creator.create_table()

            '''Insert data'''

            data_inserter = DataInserter(cursor)
            data_rooms, data_students = data_inserter.get_data()
            data_inserter.insert_rooms(data_rooms)
            data_inserter.insert_students(data_students)

            '''Create indexes'''

            index_creator = IndexCreator(cursor)
            index_creator.create_index()

            '''Execute queries'''

            query_executor = QueryExecutor(cursor)
            query_results = query_executor.execute_all_queries()

            '''Transform results'''

            if query_results:
                data = [item[1] for item in query_results]
                description = [item[0] for item in query_results]

                transformer = ResultTransformer(data)
                transformed_results = transformer.transform_all(description)

                '''Save to JSON'''
                
                JsonSaver.save_json_file(transformed_results)

    except psycopg2.OperationalError:
        logging.info('Database connection error')
        sys.exit(1)


if __name__ == "__main__":
    main()

