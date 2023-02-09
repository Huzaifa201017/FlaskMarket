from google.cloud.sql.connector import Connector
import sqlalchemy
from sqlalchemy import text

INSTANCE_CONNECTION_NAME = "flaskmarket:us-central1:sem4project"
DB_USER = "sqlserver"
DB_PASS = "Muhammad167"
DB_NAME = "market"

connector = Connector()


def getconn():

    conn = connector.connect(
        INSTANCE_CONNECTION_NAME,
        "pytds",
        user=DB_USER,
        password=DB_PASS,
        db=DB_NAME
    )
    return conn


pool = sqlalchemy.create_engine(
    "mssql+pytds://localhost",
    creator=getconn,
)


# connect to connection pool
with pool.connect() as db_conn:
    # query database and fetch results

    results = db_conn.execute(text("SELECT * FROM [User]")).fetchall()

    # show results
    for row in results:
        print(row)
    db_conn.close()


# cleanup connector
# cursor = conn.cursor()

with pool.connect() as db_conn:
    # query database and fetch results

    results = db_conn.execute(text("SELECT * FROM [User]")).fetchall()

    # show results
    for row in results:
        print(row)
    db_conn.close()


with pool.connect() as cursor:
    n = "yu"
    query = f'SELECT * FROM itemDetails where name  LIKE {"%" +n+"%"}'
    print(query)
    results = cursor.execute(text(query)).fetchall()

    cursor.close()


# customerAllDetails = []
# cursor.execute("select * from [User]")
# for row in cursor:
#     print(row[0])
