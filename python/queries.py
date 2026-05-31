
ALL_QUERIES = [
        '''
        SELECT 
                r.name as room_name,
                COUNT(s.id) as number_of_students
        FROM rooms  r
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

QUERIES_ROOMS = ''' 
        CREATE TABLE IF NOT EXISTS rooms(
                id SERIAL PRIMARY KEY NOT NULL,
                name VARCHAR(50)
                )
        '''
QUERIES_STUDENTS = '''
        CREATE TABLE IF NOT EXISTS students(
                id SERIAL PRIMARY KEY NOT NULL,
                name VARCHAR(50),
                birthday DATE,
                room INT REFERENCES rooms(id),
                sex CHAR(1)
                )
        '''

QUERY_INSERT_ROOMS = '''
        INSERT INTO rooms(id, name)
        VALUES(%s, %s)    
        ON CONFLICT (id) DO NOTHING
    '''
QUERY_INSERT_STUDENTS = '''
        INSERT INTO students(id, name, birthday, room, sex)
        VALUES(%s, %s, %s, %s, %s) 
        ON CONFLICT (id) DO NOTHING
    '''

CREATE_INDEX_1 = '''
        CREATE INDEX IF NOT EXISTS idx_students_room
        ON students (room)
        '''
    
CREATE_INDEX_2 = '''
        CREATE INDEX IF NOT EXISTS idx_students_birthday
        ON students (birthday)
        '''