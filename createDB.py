"""
File name: createDB.py
Author: Yixin Zhang
Version: 04/12/17

This script creates a schema in Postgres based on the input json file.
Change username and password to your Postgres in user_definition.py

"""
import json
import postgres_function
import user_definition
import sys
reload(sys)
sys.setdefaultencoding('utf8')


FILE_NAME = "data.json"
TABLE_NAME = "yelpData"

def create_schema(cursor, file_name, table_name):
    """
    Create schema in database
    :param cursor: curor that connects your postgres db
    :param file_name: a json file of yelp data
    :param table_name: a string to name your schema
    """
    with open(file_name) as json_data:
        data = json.load(json_data, strict=False)
    postgres_function.creatTable(cursor, data, TABLE_NAME)
    db_conn.commit()

def drop_shema(cursor, table_name):
    """
        Create schema in database
        :param cursor: curor that connects your postgres db
        :param table_name: a string of a schema name that you want to drop from db
        """
    postgres_function.drop_table(cursor, TABLE_NAME)
    db_conn.commit()

# main
# connect db
db_conn = postgres_function.connectdb(user_definition.dbname, user_definition.usr_name,
                                          user_definition.password, user_definition.port,
                                          user_definition.host)
cursor = postgres_function.db_cursor(db_conn)

create_schema(cursor, FILE_NAME, TABLE_NAME) #create schema
# drop_shema(cursor, TABLE_NAME) #drop shcema

# close cursor & db
cursor.close()
db_conn.close()
