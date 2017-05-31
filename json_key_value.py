
def count_data(data, key):
    return len(get_data_value(data, key))

def get_data_value(data, key):
    try:
        return data[key]
    except:
        return "NULL"
