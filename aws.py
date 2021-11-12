import mysql.connector

db_aws = mysql.connector.connect(
  host="database-1.cjaaudlyizww.us-east-2.rds.amazonaws.com",
  user="admin",
  password="password",
  database="table1",
  buffered = True
)
mycursor = db_aws.cursor()

#mycursor.execute("CREATE TABLE users (id INTEGER PRIMARY KEY AUTO_INCREMENT, username VARCHAR(200) NOT NULL, hash TEXT NOT NULL, cash NUMERIC NOT NULL DEFAULT 10000.00)")
#mycursor.execute("insert into users (username, hash) values(%s, %s)",("mollie", 1234))
#db_aws.commit()
#mycursor.execute("delete from users")
mycursor.execute("SELECT * FROM users where username = 'q' ")


data = mycursor.fetchall()


for row in data:
      print(row[0]['id'])
