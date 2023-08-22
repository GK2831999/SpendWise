# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

from flask import Flask, render_template, request, redirect, session 
from flask_session import Session
from flask_mysqldb import MySQL
import datetime
import re
from cryptography.fernet import Fernet
import smtplib
from flask_mail import Mail, Message
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


check = False



app = Flask(__name__)



app.secret_key = 'default-secret-key'
app.config['SESSION_TYPE'] = 'filesystem'  # Or other storage type  
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'test'
mysql = MySQL(app)




def encrypt(password):
    key = Fernet.generate_key()

    cursor = mysql.connection.cursor()
    fernet = Fernet(key)
    encMessage= fernet.encrypt(password.encode())

    #insert_query = "INSERT INTO expenses (Session_id, date, expensename, amount, paymode, category) VALUES (%s,%s, %s, %s, %s, %s)"

    return [encMessage,key]







#HOME--PAGE
@app.route("/home")
def home():
    return render_template("homepage.html")






@app.route("/")
def add():
    return render_template("home.html")





#SIGN--UP--OR--REGISTER
@app.route("/signup")
def signup():
    return render_template("signup.html")





@app.route('/register', methods=['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        arr = encrypt(password)
        


        mysql.connection.commit()

        cursor = mysql.connection.cursor()
        cursor1 = mysql.connection.cursor()
        cursor.execute('SELECT * FROM register1 WHERE email = %s', (email,))
        cursor1.execute('SELECT * FROM register1 WHERE username = %s', (username,))
        
        account = cursor.fetchone()

        account1 =  cursor1.fetchone()
        
        
        if account:
            msg = 'Account already exists!'
        elif account1:
            msg = 'Username taken!'    
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Name must contain only characters and numbers!'
        else:
            cursor.execute('INSERT INTO encrypted_data (session, hash, key_value) VALUES (%s,%s,%s)', (username,arr[0], arr[1]))

            cursor.execute('INSERT INTO register1 (username, email, password) VALUES (%s, %s, %s)', (username, email, arr[0]))
            mysql.connection.commit()
            msg = 'You have successfully registered!'

    return render_template('signup.html', msg=msg)
        
        
 
        



#LOGIN--PAGE    
@app.route("/signin")
def signin():
    return render_template("login.html")



@app.route('/login',methods =['GET', 'POST'])
def login():
    global userid
    msg = ''
    
    key = Fernet.generate_key()
  

    if request.method == 'POST' :
        username = request.form['username']
        password = request.form['password']
        
       # password = fernet.encrypt(password.encode())

        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM register1 WHERE username = % s', (username,))
        account =cursor.fetchone()
        
        print(username)
        if account:
            print(decrypt(username))
            if decrypt(username) == password:
                session['loggedin'] = True
                session['id'] = account[0]
                userid=  account[0]
                session['username'] = account[1]
                
                return redirect('/home')
            else:
                msg = 'Incorrect password !'

        else: msg = "Username does not exist!"        
    return render_template('login.html', msg = msg)



       





#ADDING----DATA
@app.route("/add")
def adding():
    return render_template('add.html')





#(NULL,  % s, % s, % s, % s, % s, % s)
@app.route('/addexpense',methods=['GET', 'POST'])
def addexpense():
    global check
    date = request.form['date']
    expensename = request.form['expensename']
    amount = request.form['amount']
    paymode = request.form['paymode']
    category = request.form['category']
    
    cursor = mysql.connection.cursor()

    insert_query = "INSERT INTO expenses (Session_id, date, expensename, amount, paymode, category) VALUES (%s,%s, %s, %s, %s, %s)"

    # Data to be inserted
    data = (session['id'],date, expensename, amount, paymode, category)

    # Execute the query with data using cursor.execute() with parameterized query
    cursor.execute(insert_query, data)
    mysql.connection.commit()

    check = False

    
    return redirect("/display")









#DISPLAY---graph 

@app.route("/display")
def display():
    global check
    
    cursor = mysql.connection.cursor()
    query1 = f"SELECT * FROM expenses WHERE Session_id='{session['id']}'"
    
    # Execute the query
    cursor.execute(query1)

    expense = cursor.fetchall()

    query2 = f"SELECT SUM(amount) AS total_amount FROM expenses WHERE Session_id='{session['id']}'"

    
    # Execute the query
    cursor.execute(query2)

    total= cursor.fetchall()
    query3 = f"SELECT SUM(amount) AS total_amount FROM expenses WHERE category = 'Food' AND Session_id='{session['id']}' "

    
    # Execute the query
    cursor.execute(query3)

    total_food= cursor.fetchall()

    
    query4 = f"SELECT SUM(amount) AS total_amount FROM expenses WHERE category = 'entertainment' AND Session_id='{session['id']}'"

    
    # Execute the query
    cursor.execute(query4)

    total_Entertainment= cursor.fetchall()


    query5 = f"SELECT SUM(amount) AS total_amount FROM expenses WHERE category = 'Business' AND Session_id='{session['id']}'"

    
    # Execute the query
    cursor.execute(query5)

    total_Business= cursor.fetchall()


    query6 = f"SELECT SUM(amount) AS total_amount FROM expenses WHERE category = 'other' AND Session_id='{session['id']}'"

    
    # Execute the query
    cursor.execute(query6)

    total_other= cursor.fetchall()

    query7 = f"SELECT SUM(amount) AS total_amount FROM expenses WHERE category = 'Rent' AND Session_id='{session['id']}'"

    
    # Execute the query
    cursor.execute(query7)

    total_Rent= cursor.fetchall()

    query8 = f"SELECT SUM(amount) AS total_amount FROM expenses WHERE category = 'EMI' AND Session_id='{session['id']}'"
    
    
    # Execute the query
    cursor.execute(query8)
    total_EMI= cursor.fetchall()
    

    arr = []

    email, limit,total_l = check_expenditure()
    
    try:
        sum_total = 0
        row= limit[0]
        

        for i in row[1:]:
            sum_total+=int(i)
        print(sum_total)
        print("total")
        print(total_food)
        arr_expense = [total_l, total_food[0][0],total_Entertainment[0][0],total_Rent[0][0],total_EMI[0][0],total_Business[0][0],total_other[0][0]]
        
        if total_l>sum_total:
            arr.append("Total")
        print(total_food[0][0], "t")

        if total_food[0][0] and total_food[0][0]>int(row[1]):
            arr.append("Food")
        if total_Entertainment[0][0] and  total_Entertainment[0][0]>int(row[2]):
            arr.append("Entertainment")

        if total_Rent[0][0] and total_Rent[0][0]>int(row[3]):
            arr.append( "Rent")


        if total_Business[0][0] and total_Business[0][0]> int(row[4]):
            arr.append("Business")

        if total_EMI[0][0] and total_EMI[0][0]>int(row[5]):
            arr.append("EMI")
        if total_other[0][0] and total_other[0][0]>int(row[6]):
            arr.append("Other")

    except:
        pass

    print(arr)
    if arr and check == False: 
        send_email_if_exceeded(arr,arr_expense,email)
        check = True
  
       
    return render_template('display.html' ,expense = expense, total=total[0],total_food=total_food,total_Entertainment=total_Entertainment,total_Business=total_Business,total_other=total_other,total_Rent=total_Rent,total_EMI=total_EMI)
                          



#delete---the--data
@app.route('/delete/<id>', methods = ['POST', 'GET' ])
def delete(id):
     global check
     cursor = mysql.connection.cursor()

     query = f"DELETE FROM expenses WHERE  id = {id}"
     cursor.execute(query)



     mysql.connection.commit()
     check = False
     return redirect("/display")
 
    



#UPDATE---DATA
@app.route('/edit/<id>', methods = ['POST', 'GET' ])
def edit(id):
    global check
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM expenses WHERE  id = %s', (id,))
    row = cursor.fetchall()
    check = False

    return render_template('edit.html', expenses = row[0])







@app.route('/update/<id>',methods = ['POST', 'GET' ])
def update(id):
  global check
  if request.method == 'POST' :
   
      date = request.form['date']
      expensename = request.form['expensename']
      amount = request.form['amount']
      paymode = request.form['paymode']
      category = request.form['category']
    
      cursor = mysql.connection.cursor()
       
      cursor.execute("UPDATE `expenses` SET `date` = % s , `expensename` = % s , `amount` = % s, `paymode` = % s, `category` = % s WHERE `expenses`.`id` = % s ",(date, expensename, amount, str(paymode), str(category),id))
      mysql.connection.commit()
      check = False
      return redirect("/display")
     
      

            
 
         



            
#limit
@app.route("/limit" )
def limit():
       return redirect('/limitn')

@app.route("/limitnum" , methods = ['POST' ])
def limitnum():


    if request.method == 'POST':
        limitss_val1 = request.form['number1']
        limitss_val2 = request.form['number2']
        limitss_val3 = request.form['number3']
        limitss_val4 = request.form['number4']
        limitss_val5 = request.form['number5']
        limitss_val6 = request.form['number6']


        
        cursor = mysql.connection.cursor()
        insert_query = "INSERT INTO limits (session, limit1, limit2, limit3, limit4, limit5, limit6) VALUES (%s, %s, %s, %s, %s, %s, %s)"
        data = (session['id'], limitss_val1,limitss_val2,limitss_val3,limitss_val4,limitss_val5,limitss_val6)
        cursor.execute(insert_query, data)
        mysql.connection.commit()
        cursor.close()
        
        return redirect('/limitn')
         
@app.route("/limitn") 
def limitn():
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM limits WHERE session = %s',(session['id'],))
    row = cursor.fetchall()
    print("row")
    
    print(row)
    if row:
        row = row[0]
        return render_template("limit_display.html", x1 = row[1], x2 = row[2],x3 = row[3],x4 = row[4],x5 = row[5],x6 = row[6])
    else:
        return render_template("limit.html") 




@app.route('/delete1')
def delete1():
    cursor = mysql.connection.cursor()


    cursor.execute('DELETE FROM limits WHERE session=%s',(session['id'],))


    

    mysql.connection.commit()
    
    return render_template("/limit.html")
  

#REPORT
@app.route('/today')
def today():
      cursor = mysql.connection.cursor()
      cursor.execute('SELECT TIME(date)   , amount FROM expenses  WHERE Session_id = %s AND DATE(date) = DATE(NOW()) ',(session['id'],))
      texpense = cursor.fetchall()

      
      cursor = mysql.connection.cursor()
      cursor.execute('SELECT * FROM expenses WHERE Session_id = % s AND DATE(date) = DATE(NOW()) AND date ORDER BY `expenses`.`date` DESC',(session['id'],))
      expense = cursor.fetchall()



  
      total=0
      t_food=0
      t_entertainment=0
      t_business=0
      t_rent=0
      t_EMI=0
      t_other=0
 
     
      for x in expense:
          total += x[4]
          if x[6] == "food":
              t_food += x[4]
            
          elif x[6] == "entertainment":
              t_entertainment  += x[4]
        
          elif x[6] == "business":
              t_business  += x[4]
          elif x[6] == "rent":
              t_rent  += x[4]
           
          elif x[6] == "EMI":
              t_EMI  += x[4]
         
          elif x[6] == "other":
              t_other  += x[4]


      
      return render_template("today.html", texpense = texpense, expense = expense,  total = total ,
                           t_food = t_food,t_entertainment =  t_entertainment,
                           t_business = t_business,  t_rent =  t_rent, 
                           t_EMI =  t_EMI,  t_other =  t_other )
     



@app.route("/month")
def month():
      cursor = mysql.connection.cursor()
      cursor.execute('SELECT DATE(date), SUM(amount) FROM expenses WHERE Session_id= %s AND MONTH(DATE(date))= MONTH(now()) GROUP BY DATE(date) ORDER BY DATE(date) ',(session['id'],))
      texpense = cursor.fetchall()
      

      
      cursor = mysql.connection.cursor()
      cursor.execute('SELECT * FROM expenses WHERE Session_id = % s AND MONTH(DATE(date))= MONTH(now()) AND date ORDER BY `expenses`.`date` DESC',(session['id'],))
      expense = cursor.fetchall()
  
      total=0
      t_food=0
      t_entertainment=0
      t_business=0
      t_rent=0
      t_EMI=0
      t_other=0
 
     
      for x in expense:
          total += x[4]
          if x[6] == "food":
              t_food += x[4]
            
          elif x[6] == "entertainment":
              t_entertainment  += x[4]
        
          elif x[6] == "business":
              t_business  += x[4]
          elif x[6] == "rent":
              t_rent  += x[4]
           
          elif x[6] == "EMI":
              t_EMI  += x[4]
         
          elif x[6] == "other":
              t_other  += x[4]
            


      return render_template("month.html", texpense = texpense, expense = expense,  total = total ,
                           t_food = t_food,t_entertainment =  t_entertainment,
                           t_business = t_business,  t_rent =  t_rent, 
                           t_EMI =  t_EMI,  t_other =  t_other )
         





@app.route("/year")
def year():
      cursor = mysql.connection.cursor()
      cursor.execute('SELECT MONTH(date), SUM(amount) FROM expenses WHERE Session_id= %s AND YEAR(DATE(date))= YEAR(now()) GROUP BY MONTH(date) ORDER BY MONTH(date) ',(session['id'],))
      texpense = cursor.fetchall()
      print(texpense)
      
      cursor = mysql.connection.cursor()
      cursor.execute('SELECT * FROM expenses WHERE Session_id = % s AND YEAR(DATE(date))= YEAR(now()) AND date ORDER BY `expenses`.`date` DESC',(session['id'],))
      expense = cursor.fetchall()
  
      total=0
      t_food=0
      t_entertainment=0
      t_business=0
      t_rent=0
      t_EMI=0
      t_other=0
 
     
      for x in expense:
          total += x[4]
          if x[6] == "food":
              t_food += x[4]
            
          elif x[6] == "entertainment":
              t_entertainment  += x[4]
        
          elif x[6] == "business":
              t_business  += x[4]
          elif x[6] == "rent":
              t_rent  += x[4]
           
          elif x[6] == "EMI":
              t_EMI  += x[4]
         
          elif x[6] == "other":
              t_other  += x[4]
            



     
      return render_template("year.html", texpense = texpense, expense = expense,  total = total ,
                           t_food = t_food,t_entertainment =  t_entertainment,
                           t_business = t_business,  t_rent =  t_rent, 
                           t_EMI =  t_EMI,  t_other =  t_other )

#log-out



def send_email_if_exceeded(arr,err_expense, email):
  
    app.config['MAIL_SERVER']='smtp.gmail.com'
    app.config['MAIL_PORT'] = 465
    app.config['MAIL_USERNAME'] = 'spendwiseteam2006@gmail.com'
    app.config['MAIL_PASSWORD'] = 'hflnxziaijepceyd'
    app.config['MAIL_USE_TLS'] = False
    app.config['MAIL_USE_SSL'] = True
    mail = Mail(app)



    
    str1  =f"""Username: {session['id']}
    Total Expense: {err_expense[0]}
    Expense on Food: {err_expense[1]}
    Expense on Entertainment: {err_expense[2]}
    Expense on Rent: {err_expense[3]}
    Expense on EMI: {err_expense[4]}
    Expense on Business: {err_expense[5]}
    Expense on Other: {err_expense[6]}\n**************************************\n**************************************\n
    """

    str2 = ""
    print(str1)
    print(arr)
    for i in arr:
        str2 += f"Exceeded expenditure:{i}"+"\n"
    print(str2)
    string = str1 + "\n"+ str2    
    print(string)
    print(email)
    try:

        msg = Message(
        'SpendWise Team ----WARNING!',
        sender ='spendwiseteam2006@gmail.com',
        recipients = [email[0][0]]
                            )
        msg.body = string
        mail.send(msg)
        print('Sent')

    except Exception as e:
        print(f"Error sending email: {str(e)}")
        







def check_expenditure():
    

    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM expenses WHERE Session_id = % s AND MONTH(DATE(date))= MONTH(now()) AND date ORDER BY `expenses`.`date` DESC',(session['id'],))
    expense = cursor.fetchall()
    total = 0
    for x in expense:
          total += x[4]

    cursor.execute('SELECT * FROM limits WHERE session = %s',(session['id'],))
    row = cursor.fetchall()


    
    cursor.execute('SELECT email FROM register1 WHERE username = %s',(session['id'],))
    email = cursor.fetchall()
    
    return email,row, total

    







@app.route('/logout')

def logout():
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('username', None)
   return render_template('home.html')



def decrypt(username):
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM encrypted_data WHERE session= % s',(username,))
    hash_val = cursor.fetchall()
    print(hash_val)
    key = hash_val[0][2]
    msg = hash_val[0][1]

    print(key)
    print(msg)
    fernet = Fernet(key)


    #encMessage1 = fernet.encrypt(message.encode())
    

    decMessage = fernet.decrypt(msg).decode()
    print(decMessage)
    return decMessage




































             

if __name__ == "__main__":
    app.run(debug=False, host = '0.0.0.0')
