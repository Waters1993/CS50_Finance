import mysql.connector

db_aws = mysql.connector.connect(
  host="database-1.cjaaudlyizww.us-east-2.rds.amazonaws.com",
  user="admin",
  password="password",
  database="table1",
  buffered = True
)
mycursor = db_aws.cursor()

mycursor.execute("show tables")
#mycursor.execute("SELECT symbol, name, price, SUM(shares) as totalShares FROM transactions WHERE user_id = %s GROUP BY symbol", (user_id,))

stocks = mycursor.fetchall()

#stocks_price = float(stocks[7])
#stocks_totalshares = float(stocks[3])

#print(stocks_price)
#print(stocks_totalshares)
print(stocks)
