#!/usr/bin/env python2.7

"""
Columbia W4111 Intro to databases
Example webserver

To run locally

    python server.py

Go to http://localhost:8111 in your browser


A debugger such as "pdb" may be helpful for debugging.
Read about it online.
"""

import os
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)



# XXX: The Database URI should be in the format of:
#
#     postgresql://USER:PASSWORD@<IP_OF_POSTGRE_SQL_SERVER>/<DB_NAME>
#
# For example, if you had username ewu2493, password foobar, then the following line would be:
#
#     DATABASEURI = "postgresql://ewu2493:foobar@<IP_OF_POSTGRE_SQL_SERVER>/postgres"
#
# For your convenience, we already set it to the class database

# Use the DB credentials you received by e-mail
DB_USER = "st3185"
DB_PASSWORD = "xo9AGrNiHw"

DB_SERVER = "w4111.cisxo09blonu.us-east-1.rds.amazonaws.com"

DATABASEURI = "postgresql://"+DB_USER+":"+DB_PASSWORD+"@"+DB_SERVER+"/w4111"


#
# This line creates a database engine that knows how to connect to the URI above
#
engine = create_engine(DATABASEURI)


# Here we create a test table and insert some values in it
engine.execute("""DROP TABLE IF EXISTS test;""")
engine.execute("""CREATE TABLE IF NOT EXISTS test (
  id serial,
  name text
);""")
engine.execute("""INSERT INTO test(name) VALUES ('grace hopper'), ('alan turing'), ('ada lovelace');""")



@app.before_request
def before_request():
  """
  This function is run at the beginning of every web request
  (every time you enter an address in the web browser).
  We use it to setup a database connection that can be used throughout the request

  The variable g is globally accessible
  """
  try:
    g.conn = engine.connect()
  except:
    print "uh oh, problem connecting to database"
    import traceback; traceback.print_exc()
    g.conn = None

@app.teardown_request
def teardown_request(exception):
  """
  At the end of the web request, this makes sure to close the database connection.
  If you don't the database could run out of memory!
  """
  try:
    g.conn.close()
  except Exception as e:
    pass


#
# @app.route is a decorator around index() that means:
#   run index() whenever the user tries to access the "/" path using a GET request
#
# If you wanted the user to go to e.g., localhost:8111/foobar/ with POST or GET then you could use
#
#       @app.route("/foobar/", methods=["POST", "GET"])
#
# PROTIP: (the trailing / in the path is important)
#
# see for routing: http://flask.pocoo.org/docs/0.10/quickstart/#routing
# see for decorators: http://simeonfranklin.com/blog/2012/jul/1/python-decorators-in-12-steps/
#
@app.route('/')
def index():
  """
  request is a special object that Flask provides to access web request information:

  request.method:   "GET" or "POST"
  request.form:     if the browser submitted a form, this contains the data in the form
  request.args:     dictionary of URL arguments e.g., {a:1, b:2} for http://localhost?a=1&b=2

  See its API: http://flask.pocoo.org/docs/0.10/api/#incoming-request-data
  """

  # DEBUG: this is debugging code to see what request looks like
  print request.args


  #
  # example of a database query
  #
  cursor = g.conn.execute("SELECT p_id FROM building JOIN property ON building.bldg_id = property.bldg_id WHERE year_built >2000")
  p_id = []
  for result in cursor:
    p_id.append(result['p_id'])  # can also be accessed using result[0]
  cursor.close()

  #
  # Flask uses Jinja templates, which is an extension to HTML where you can
  # pass data to a template and dynamically generate HTML based on the data
  # (you can think of it as simple PHP)
  # documentation: https://realpython.com/blog/python/primer-on-jinja-templating/
  #
  # You can see an example template in templates/index.html
  #
  # context are the variables that are passed to the template.
  # for example, "data" key in the context variable defined below will be
  # accessible as a variable in index.html:
  #
  #     # will print: [u'grace hopper', u'alan turing', u'ada lovelace']
  #     <div>{{data}}</div>
  #
  #     # creates a <div> tag for each element in data
  #     # will print:
  #     #
  #     #   <div>grace hopper</div>
  #     #   <div>alan turing</div>
  #     #   <div>ada lovelace</div>
  #     #
  #     {% for n in data %}
  #     <div>{{n}}</div>
  #     {% endfor %}
  #
  context = dict(data = p_id)


  #
  # render_template looks in the templates/ folder for files.
  # for example, the below file reads template/index.html
  #
  return render_template("homepage.html", **context)

#
# This is an example of a different path.  You can see it at
#
#     localhost:8111/another
#
# notice that the functio name is another() rather than index()
# the functions for each app.route needs to have different names
#
@app.route('/to_addBuyer')
def to_addBuyer():
  return render_template("addBuyer.html")

@app.route('/to_addSeller')
def to_addSeller():
   return render_template("addSeller.html")

@app.route('/to_login')
def to_login():
   return render_template("Login.html")

@app.route('/homepage')
def homepage():
  return render_template("homepage.html")

@app.route('/to_buyerprofile')
def to_buyerprofile():
    cursor = g.conn.execute("SELECT property.p_id,prop_type, lot_size, bathroom_n, bedroom_n, furnished, garage, address, city, state, building.zipcode, neighborhood, year_built, description FROM property JOIN building ON property.bldg_id = building.bldg_id JOIN Zipcodes ON building.zipcode = Zipcodes.zipcode")
    info = []
    for result in cursor:
        dic = dict()
        dic['p_id'] = result[0]
        dic['prop_type'] = result[1]
        dic['lot_size'] = result[2]
        dic['bathroom_n'] = result[3]
        dic['bedroom_n'] = result[4]
        dic['furnished'] = result[5]
        dic['garage'] = result[6]
        dic['address'] = result[7]
        dic['city'] = result[8]
        dic['state'] = result[9]
        dic['zipcode'] = result[10]
        dic['neighborhood'] = result[11]
        dic['year_built'] = result[12]
        dic['description'] = result[13]
        info.append(dic)
    cursor.close()
    cursor = g.conn.execute("SELECT p_id FROM likes WHERE b_id = 1")
    info2 = []
    for result in cursor:
      dic = dict()
      dic['p_id'] = result[0]
      info2.append(dic)
    cursor.close()
    context = dict(Property = info, Liked = info2)
    return render_template("buyerprofile.html", **context)


# Example of adding new data to the database

@app.route('/addBuyer', methods=['POST'])
def addBuyer():
  b_username = request.form['b_username']
  b_password = request.form['b_password']
  b_email = request.form['b_email']
  #print name
  #users_id need to be different from each other
  result1 = g.conn.execute(text('SELECT max(b_id) from buyer'))
  b_id=0
  for i in result1:
      b_id =i[0]+1
  result = g.conn.execute(text('SELECT b_username from buyer'))
  buyer_username_list = []
  for r in result:
      buyer_username_list.append(str(r[0]))
  if b_username in buyer_username_list:
      return render_template('useriderror.html')
  else:
      cmd = 'INSERT INTO buyer(b_id,b_username,b_password,b_email) VALUES (:b_id,:b_username,:b_password,:b_email)';
      g.conn.execute(text(cmd), b_id = b_id, b_username = b_username,  b_password =b_password,b_email =b_email);
      return render_template("successfulcreate.html")

@app.route('/addSeller', methods=['POST'])
def addSeller():
  s_username = request.form['s_username']
  s_password = request.form['s_password']
  s_email = request.form['s_email']
  phone_number = request.form['phone_number']
  #print name
  #users_id need to be different from each other
  result = g.conn.execute(text('SELECT max(s_id) from seller'))
  s_id=0
  for i in result:
      s_id =i[0]+1
  result1 = g.conn.execute(text('SELECT s_username from seller'))
  seller_username_list = []
  for r in result1:
      seller_username_list.append(str(r[0]))
  if s_username in seller_username_list:
      return render_template('useriderror.html')
  else:
      cmd = 'INSERT INTO seller(s_id,s_username,s_password,s_email,phone_number) VALUES (:s_id,:s_username,:s_password,:s_email,:phone_number)';
      g.conn.execute(text(cmd), s_id = s_id, s_username = s_username,  s_password =s_password,s_email =s_email, phone_number =phone_number);
      return render_template("successfulcreate.html")

@app.route('/Login', methods=['POST'])
def Login():
  username = request.form['username']
  password = request.form['password']
  value = request.form['identity']
  if username =="" or password =="":
      return render_template("loginerror.html")
  #print name
  #users_id need to be different from each other
  if value == "Buyer":
      result1 = g.conn.execute(text('SELECT b_username from buyer'))
      buyer_username_list = []
      for r in result1:
          buyer_username_list.append(str(r[0]))
      result2 = g.conn.execute(text('SELECT b_password from buyer'))
      buyer_password_list = []
      for r in result2:
          buyer_password_list.append(str(r[0]))
      if username not in buyer_username_list or password not in buyer_password_list:
          return render_template('loginerror.html')
      if username =="b1" and password !="b1":
          return render_template('loginerror.html')
      cursor = g.conn.execute("SELECT property.p_id,prop_type, lot_size, bathroom_n, bedroom_n, furnished, garage, address, city, state, building.zipcode, neighborhood, year_built, description FROM property JOIN building ON property.bldg_id = building.bldg_id JOIN Zipcodes ON building.zipcode = Zipcodes.zipcode")
      info = []
      for result in cursor:
        dic = dict()
        dic['p_id'] = result[0]
        dic['prop_type'] = result[1]
        dic['lot_size'] = result[2]
        dic['bathroom_n'] = result[3]
        dic['bedroom_n'] = result[4]
        dic['furnished'] = result[5]
        dic['garage'] = result[6]
        dic['address'] = result[7]
        dic['city'] = result[8]
        dic['state'] = result[9]
        dic['zipcode'] = result[10]
        dic['neighborhood'] = result[11]
        dic['year_built'] = result[12]
        dic['description'] = result[13]
        info.append(dic)
      cursor.close()
      context = dict(Property = info)
      cursor = g.conn.execute("SELECT p_id FROM likes WHERE b_id = 1")
      info2 = []
      for result in cursor:
        dic = dict()
        dic['p_id'] = result[0]
        info2.append(dic)
      cursor.close()
      context = dict(Property = info, Liked = info2)
      return render_template('buyerprofile.html', **context)
  else:
      result1 = g.conn.execute(text('SELECT s_username from seller'))
      seller_username_list = []
      for r in result1:
          seller_username_list.append(str(r[0]))
      result2 = g.conn.execute(text('SELECT s_password from seller'))
      seller_password_list = []
      for r in result2:
          seller_password_list.append(str(r[0]))
      if username not in seller_username_list or password not in seller_password_list:
          return render_template('loginerror.html')
      if username =="s5" and password !="s5":
          return render_template('loginerror.html')
      cursor = g.conn.execute("SELECT property.p_id, prop_type, lot_size, bathroom_n, bedroom_n, furnished, garage, address, city, state, building.zipcode, neighborhood, year_built, description FROM property JOIN building ON property.bldg_id = building.bldg_id JOIN Zipcodes ON building.zipcode = Zipcodes.zipcode JOIN listing ON listing.p_id = property.p_id WHERE s_id = 5")
      info = []
      for result in cursor:
        dic = dict()
        dic['p_id'] = result[0]
        dic['prop_type'] = result[1]
        dic['lot_size'] = result[2]
        dic['bathroom_n'] = result[3]
        dic['bedroom_n'] = result[4]
        dic['furnished'] = result[5]
        dic['garage'] = result[6]
        dic['address'] = result[7]
        dic['city'] = result[8]
        dic['state'] = result[9]
        dic['zipcode'] = result[10]
        dic['neighborhood'] = result[11]
        dic['year_built'] = result[12]
        dic['description'] = result[13]
        info.append(dic)
      cursor.close()
      cursor = g.conn.execute("SELECT  p_id, b_username, b_email FROM likes JOIN buyer ON likes.b_id = buyer.b_id WHERE p_id IN (SELECT p_id FROM listing WHERE s_id = 5) ORDER BY p_id")
      info2 = []
      for result in cursor:
        dic = dict()
        dic['p_id'] = result[0]
        dic['b_username'] = result[1]
        dic['b_email'] = result[2]
        info2.append(dic)
      cursor.close()
      context = dict(Property = info, Liked = info2)
      return render_template('sellerprofile.html', **context)

@app.route('/productList',methods=['GET'])
def productList():

  return render_template("productList.html", **context)
PRO_ID=['a','b']

# delete data from the databases
@app.route('/Delete', methods=['POST'])
def Delete():
    p_id = request.form['p_id']
    cmd = 'DELETE FROM property WHERE p_id = :p_id'
    g.conn.execute(text(cmd),p_id=p_id)
    cursor = g.conn.execute("SELECT property.p_id, prop_type, lot_size, bathroom_n, bedroom_n, furnished, garage, address, city, state, building.zipcode, neighborhood, year_built, description FROM property JOIN building ON property.bldg_id = building.bldg_id JOIN Zipcodes ON building.zipcode = Zipcodes.zipcode JOIN listing ON listing.p_id = property.p_id WHERE s_id = 5")
    info = []
    for result in cursor:
        dic = dict()
        dic['p_id'] = result[0]
        dic['prop_type'] = result[1]
        dic['lot_size'] = result[2]
        dic['bathroom_n'] = result[3]
        dic['bedroom_n'] = result[4]
        dic['furnished'] = result[5]
        dic['garage'] = result[6]
        dic['address'] = result[7]
        dic['city'] = result[8]
        dic['state'] = result[9]
        dic['zipcode'] = result[10]
        dic['neighborhood'] = result[11]
        dic['year_built'] = result[12]
        dic['description'] = result[13]
        info.append(dic)
    cursor.close()
    cursor = g.conn.execute("SELECT  p_id, b_username, b_email FROM likes JOIN buyer ON likes.b_id = buyer.b_id WHERE p_id IN (SELECT p_id FROM listing WHERE s_id = 5) ORDER BY p_id")
    info2 = []
    for result in cursor:
      dic = dict()
      dic['p_id'] = result[0]
      dic['b_username'] = result[1]
      dic['b_email'] = result[2]
      info2.append(dic)
    cursor.close()
    context = dict(Property = info, Liked = info2)
    return render_template("sellerprofile.html", **context)


@app.route('/Like', methods=['POST'])
def Like():
    p_id = request.form['p_id']
    result = g.conn.execute(text('SELECT p_id from property'))
    p_id_list = []
    for r in result:
        p_id_list.append(str(r[0]))
    if p_id not in p_id_list:
        return render_template('piderror.html')
    result2 = g.conn.execute("SELECT p_id FROM likes WHERE b_id = 1")
    p_id_list2 = []
    for result in result2:
        p_id_list2.append(str(result[0]))
    if p_id not in p_id_list2:
        cmd = 'INSERT INTO likes(b_id, p_id) VALUES (1,:p_id)'
        g.conn.execute(text(cmd),p_id=p_id)
    cursor = g.conn.execute("SELECT property.p_id,prop_type, lot_size, bathroom_n, bedroom_n, furnished, garage, address, city, state, building.zipcode, neighborhood, year_built, description FROM property JOIN building ON property.bldg_id = building.bldg_id JOIN Zipcodes ON building.zipcode = Zipcodes.zipcode")
    info = []
    for result in cursor:
        dic = dict()
        dic['p_id'] = result[0]
        dic['prop_type'] = result[1]
        dic['lot_size'] = result[2]
        dic['bathroom_n'] = result[3]
        dic['bedroom_n'] = result[4]
        dic['furnished'] = result[5]
        dic['garage'] = result[6]
        dic['address'] = result[7]
        dic['city'] = result[8]
        dic['state'] = result[9]
        dic['zipcode'] = result[10]
        dic['neighborhood'] = result[11]
        dic['year_built'] = result[12]
        dic['description'] = result[13]
        info.append(dic)
    cursor.close()
    cursor = g.conn.execute("SELECT p_id FROM likes WHERE b_id = 1")
    info2 = []
    for result in cursor:
      dic = dict()
      dic['p_id'] = result[0]
      info2.append(dic)
    cursor.close()
    context = dict(Property = info, Liked = info2)
    return render_template("buyerprofile.html", **context)


@app.route('/Add_P', methods=['POST'])
def Add_P():
    result = g.conn.execute(text('SELECT max(p_id) from property'))
    p_id=0
    for i in result:
        p_id =i[0]+1
    prop_type = request.form['prop_type']
    lot_size = request.form['lot_size']
    bathroom_n = request.form['bathroom_n']
    bedroom_n = request.form['bedroom_n']
    furnished = request.form['furnished']
    garage = request.form['garage']
    bldg_id = request.form['bldg_id']
    s_id =5
    cmd = 'INSERT INTO property(p_id,prop_type,bldg_id,lot_size,bathroom_n,bedroom_n, furnished, garage) \
    VALUES(:p_id,:prop_type,:bldg_id,:lot_size,:bathroom_n,:bedroom_n,:furnished,:garage)'
    g.conn.execute(text(cmd),p_id=p_id,prop_type =prop_type,bldg_id = bldg_id,lot_size=lot_size,bathroom_n=bathroom_n,bedroom_n =bedroom_n,furnished=furnished,garage=garage)
    cmd = 'INSERT INTO listing(s_id,p_id) VALUES(:s_id,:p_id)'
    g.conn.execute(text(cmd),s_id=s_id,p_id=p_id)


    cursor = g.conn.execute("SELECT property.p_id, prop_type, lot_size, bathroom_n, bedroom_n, furnished, garage, address, city, state, building.zipcode, neighborhood, year_built, description FROM property JOIN building ON property.bldg_id = building.bldg_id JOIN Zipcodes ON building.zipcode = Zipcodes.zipcode JOIN listing ON listing.p_id = property.p_id WHERE s_id = 5")
    info = []
    for result in cursor:
        dic = dict()
        dic['p_id'] = result[0]
        dic['prop_type'] = result[1]
        dic['lot_size'] = result[2]
        dic['bathroom_n'] = result[3]
        dic['bedroom_n'] = result[4]
        dic['furnished'] = result[5]
        dic['garage'] = result[6]
        dic['address'] = result[7]
        dic['city'] = result[8]
        dic['state'] = result[9]
        dic['zipcode'] = result[10]
        dic['neighborhood'] = result[11]
        dic['year_built'] = result[12]
        dic['description'] = result[13]
        info.append(dic)
    cursor.close()
    cursor = g.conn.execute("SELECT  p_id, b_username, b_email FROM likes JOIN buyer ON likes.b_id = buyer.b_id WHERE p_id IN (SELECT p_id FROM listing WHERE s_id = 5) ORDER BY p_id")
    info2 = []
    for result in cursor:
      dic = dict()
      dic['p_id'] = result[0]
      dic['b_username'] = result[1]
      dic['b_email'] = result[2]
      info2.append(dic)
    cursor.close()
    context = dict(Property = info, Liked = info2)
    return render_template("sellerprofile.html", **context)



if __name__ == "__main__":
  import click

  @click.command()
  @click.option('--debug', is_flag=True)
  @click.option('--threaded', is_flag=True)
  @click.argument('HOST', default='0.0.0.0')
  @click.argument('PORT', default=8111, type=int)
  def run(debug, threaded, host, port):
    """
    This function handles command line parameters.
    Run the server using

        python server.py

    Show the help text using

        python server.py --help

    """

    HOST, PORT = host, port
    print "running on %s:%d" % (HOST, PORT)
    app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)


  run()
