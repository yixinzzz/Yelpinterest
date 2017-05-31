import psycopg2
import json_key_value

def connectdb(db_name, user_name, password, port, host):
    try:
        db_conn = psycopg2.connect(dbname=db_name, user=user_name, password = password, port = port, host=host)
    except:
        print("Not able to connect to " + db_name)
    return db_conn

def db_cursor(db_conn):
    cursor = db_conn.cursor()  # open a cursor to perform db operations.
    return cursor

def execute(db_cursor, query):
    db_cursor.execute(query)

def create_table(db_cursor, table_name, column_and_type_list):
    create_table_query = 'CREATE TABLE ' + table_name + "(" + column_and_type_list + ");"
    execute(db_cursor, create_table_query) #Uncomment later

def drop_table(db_cursor, table_name):
    drop_table_query = "DROP TABLE " + table_name + ";"
    execute(db_cursor, drop_table_query)

def insert_into_table(db_cursor, table_name, column_names, values):
    insert_into_table_query =  'INSERT INTO ' + table_name + "("+ column_names + ") values (" + values + ");"
    execute(db_cursor, insert_into_table_query) #Uncomment later

def select_data(db_cursor, table_name, column_name, constraint):
    select_data_query =  "SELECT " + column_name + " FROM " + table_name + " WHERE " + constraint + ";"
    execute(db_cursor, select_data_query)

# create table
def creatTable(cursor, jdata):
    print "Createing table...."
    create_table(cursor, "yelpData", "yelp_id varchar(70), name varchar(200),\
                                                        website varchar(400), phone varchar(12) , \
                                                        rating float, review_count numeric, \
                                                        address varchar(70), yelp_deals varchar(100),\
                                                        reviews varchar(300), photos varchar(300)")
    items = json_key_value.get_data_value(jdata, "data")
    colname = ", ".join(jdata['headers'])
    for i in range(len(items)):
        values = ""
        for j in colname.split(", "):
            v = json_key_value.get_data_value(items[i], j)
            if j == 'yelp_id':
                values += "'" + v + "'"
            else:
                if isinstance(v, unicode):
                    v = v.encode("utf-8")
                if isinstance(v, str) and v != "NULL":
                    v = v.replace("'", "''")
                    v = "'" + v + "'"
                else:
                    v = str(v)
                values += ", " + v
        # print values
        insert_into_table(cursor, "yelpData", colname, values)
    print "Table has been created successfully"
