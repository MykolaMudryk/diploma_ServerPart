import pymysql.cursors

# establish connection with database
def get_connection():
    conn = pymysql.connect(host='127.0.0.1',
                           user='nicolas',
                           password='111111',
                           db='microclimate_system',
                           charset='utf8mb4',
                           cursorclass=pymysql.cursors.DictCursor)
    return conn
