import os
import mysql.connector
import sys
import logging

logging.basicConfig(filename='errorlog.txt', level=logging.DEBUG)

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from mysql.connector.abstracts import MySQLCursorAbstract
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True


# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
#db = SQL("sqlite:///finance.db")

# Configure AWS RDS
db_aws = mysql.connector.connect(
  host="database-1.cjaaudlyizww.us-east-2.rds.amazonaws.com",
  user="admin",
  password="password",
  database="table1",
  buffered = True
)
db = db_aws.cursor()

# Make sure API key is set

if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""
    user_id = session["user_id"]
    
     
    db.execute("SELECT symbol, name, price, SUM(shares) as totalShares FROM transactions WHERE user_id = %s GROUP BY symbol", (user_id,))
    stocks = db.fetchall()

    stocks_2 = stocks 

    stocks_price = float(stocks[0][2])
    print(type(stocks_price))
    stocks_totalshares = float(stocks_2[0][3])
  
    db.execute("SELECT cash FROM users WHERE id = %s", ( user_id,))
    pre_cash = db.fetchall()[0]
    cash = float(pre_cash[0])

    total = float(cash)

    for stock in stocks:
        total += stocks_price * stocks_totalshares

    app.logger.info("got through sql querys")
    return render_template("index.html", stocks=stocks, cash=cash, usd=usd, total=total)


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        symbol = request.form.get("symbol").upper()
        # use the helper function look up which returns a dictionary of info about the symbl
        item = lookup(symbol)
        print(item)

        if not symbol:
            return apology("Please enter a symbol!")
        elif not item:
            return apology("Invalid symbol!")

        try:
            shares = int(request.form.get("shares"))
        except:
            return apology("Shares must be an integer")

        if shares <= 0:
            return apology("Shares must be a positive integer")

        user_id = session["user_id"]
        #cash = db.execute("SELECT cash FROM users WHERE id = ?", user_id)[0]["cash"]
        db.execute("SELECT cash FROM users WHERE id = %s", (user_id,))
        pre_cash = db.fetchall()[0]
        cash = float(pre_cash[0])
        app.logger.info(type(cash))
        
        item_name = item["name"]
        item_price = item["price"]
        total_price = item_price * shares
        app.logger.info(type(total_price))

        if cash < total_price:
            return apology("You do not have enough cash to make this purchase")
        else:
            # Update the users table and subtract the price he has paid
            
            ## Insert the transaction into the transaction table

            #db.execute("UPDATE users SET cash = ? WHERE id = ?", cash - total_price, user_id)
            db.execute("UPDATE users SET cash = %s WHERE id = %s", (cash - total_price, user_id))

            #db.execute("INSERT INTO transactions (user_id, name, shares, price, type, symbol) VALUES (?, ? , ?, ?, ?, ?)",
             #          user_id, item_name, shares, item_price, 'BUY', symbol)

            db.execute("INSERT INTO transactions (user_id, name, shares, price, type, symbol) VALUES (%s, %s, %s, %s, %s, %s)",(user_id, item_name, shares, item_price, 'BUY', symbol))
            db_aws.commit()
        app.logger.info("Completed SQL queries of the buy section")
        return redirect('/')
    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("buy.html")


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""

    user_id = session["user_id"]

    purchases = db.execute("SELECT * FROM transactions WHERE user_id = ?", user_id)
    print(purchases)
    return render_template("history.html", purchases=purchases, usd=usd)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        print("Execute query")
        db.execute("SELECT * FROM users WHERE username = %s", (request.form.get("username"),))
       # db.execute("insert into users (username, hash) values (%s , %s)", (request.form.get("username"), hashkey))
        rows = db.fetchall()
        # Ensure username exists and password is correct
        if db.rowcount != 1 or not check_password_hash(rows[0][2], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0][0]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        print("Made it to login")
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        if not request.form.get("symbol"):
            return apology("Stock ticker must be populated", 400)

        stock = lookup(request.form.get("symbol"))

        try:
            stock['name']
        except:
            return apology("This is not a valid stock ticker")

        return render_template("quoted.html", stockName={
            'name': stock['name'],
            'symbol': stock['symbol'],
            'price': usd(stock['price'])

        })

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("quote.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 400)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 400)

        # Ensure that the passwords match
        elif request.form.get("password") != request.form.get("confirmation"):
            return apology("Password must match", 400)

        else:
            # Insert the new user into the database

            # Generate a hash key to be placed in the data base instead of the password
            hashkey = generate_password_hash(request.form.get("password"), method='pbkdf2:sha256', salt_length=8)
            try:
                db.execute("insert into users (username, hash) values (%s , %s)", (request.form.get("username"), hashkey))
                db_aws.commit()
            except:
                return apology("this user name already exists")

            print("redirected to index")
            return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        print("register")
        return render_template("register.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    user_id = session["user_id"]

    if request.method == "POST":
        symbol = request.form.get("symbol")
        shares = int(request.form.get("shares"))

        if shares < 0:
            return apology("Shares must be a positve number")

        item_price = lookup(symbol)["price"]
        item_name = lookup(symbol)["name"]
        price = shares * item_price

        current_shares = db.execute(
            "SELECT shares FROM transactions WHERE user_id = ? AND symbol = ? GROUP BY symbol", user_id, symbol)[0]["shares"]
        if current_shares < shares:
            return apology("You do not own enough shares")

        current_cash = db.execute("SELECT cash FROM users WHERE id = ?", user_id)[0]["cash"]

        db.execute("UPDATE users SET cash = ? WHERE id = ?", current_cash + price, user_id)
        db.execute(
            "INSERT into TRANSACTIONS (user_id, name, shares, price, type, symbol) VALUES( ?, ?, ?, ?, ?, ?)",
            user_id, item_name, -shares, item_price, "SELL", symbol)
        return redirect('/')

    else:
        symbols = db.execute("SELECT symbol FROM transactions WHERE user_id = ? GROUP BY symbol", user_id)

        return render_template("sell.html", symbols=symbols)


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
