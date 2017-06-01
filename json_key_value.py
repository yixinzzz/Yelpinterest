"""
File name: json_key_value.py
Author: Yixin Zhang
Version: 11/03/16

helper functions of postgres_functiopn.py
"""

def count_data(data, key):
    return len(get_data_value(data, key))

def get_data_value(data, key):
    try:
        return data[key]
    except:
        return "NULL"
