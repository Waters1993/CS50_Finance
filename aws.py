import mysql.connector

db_aws = mysql.connector.connect(
  host="database-1.cjaaudlyizww.us-east-2.rds.amazonaws.com",
  user="admin",
  password="password",
  database="table1",
  buffered = True
)
mycursor = db_aws.cursor()

mycursor.execute("SELECT * FROM transactions where user_id = 17 ")
#mycursor.execute("SELECT symbol, name, price, SUM(shares) as totalShares FROM transactions WHERE user_id = %s GROUP BY symbol", (user_id,))

#stocks = mycursor.fetchall()[0]

#stocks_price = float(stocks[7])
#stocks_totalshares = float(stocks[3])

#print(stocks_price)
#print(stocks_totalshares)
a = mycursor.fetchall()
b = a
data = float(a[0][7])
data_2 = float(b[0][3])


print(data)
print(data_2)
