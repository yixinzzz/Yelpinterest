import json
import json_key_value
import postgres_function
import user_definition
import sys
reload(sys)
sys.setdefaultencoding('utf8')

# create table
def creatTable(cursor, jdata):
    print "Createing table...."
    postgres_function.create_table(cursor, "yelpData", "yelp_id varchar(70), name varchar(200),\
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
        postgres_function.insert_into_table(cursor, "yelpData", colname, values)
    print "Table has been created successfully"

def get_photos(keyword):
    print "Searching for " + keyword + " ..."
    constraint = "reviews like '% " + keyword + " %'"
    postgres_function.select_data(cursor, "yelpData", 'photos', constraint)
    return cursor.fetchall()

with open('data.json') as json_data:
    data = json.load(json_data, strict=False)

# connect db
db_conn = postgres_function.connectdb(user_definition.dbname, user_definition.usr_name,
                                          user_definition.password, user_definition.port,
                                          user_definition.host)
cursor = postgres_function.db_cursor(db_conn)

# drop table
# postgres_function.drop_table(cursor, "yelpData")

# create table
creatTable(cursor, data)
db_conn.commit()

print get_photos("hot pot")

cursor.close()
db_conn.close()