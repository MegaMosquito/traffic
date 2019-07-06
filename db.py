#!/usr/bin/python3


import json
import sys
import time
import datetime
import traceback


# Don't forget to `pip install couchdb`
import couchdb


from machine import Machine




# A class for our database of "machine" documents
class DB:

  def __init__(self, address, port, user, password, database, time_format):
    self.db = None
    self.name = database
    self.time_format = time_format

    # Try forever to connect
    while True:
      print("Attempting to connect to CouchDB server at " + address + ":" + str(port) + "...")
      couchdbserver = couchdb.Server('http://%s:%s@%s:%d/' % ( \
        user, \
        password, \
        address, \
        port))
      if couchdbserver:
        break
      print("CouchDB server not accessible. Will retry...")
      time.sleep(10)

    # Connected!
    print("Connected to CouchDB server.")

    # Open or create our database
    print("Attempting to open the \"" + database + "\" DB...")
    if database in couchdbserver:
      self.db = couchdbserver[database]
    else:
      self.db = couchdbserver.create(database)

    # Done!
    print('CouchDB database "' + database + '" is open and ready for use.')
    sys.stdout.flush()

  # Instance method to get all the DB "machine" documents
  def get_all(self):
    return self.db.view('_all_docs')

  # Instance method to delete a "machine" document from DB using IP as '_id'
  def delete(self, ip):
    h = self.db.get(ip)
    if h:
      # print("DB.delete():  ip=" + ip + " *X* " + str(doc))
      self.db.delete(h)
    else:
      # print("DB.delete():  ip=" + ip + " <-- NOT FOUND! **********")
      pass

  # Reset the traffic DB (delete all "machine" documents)
  def reset(self):









    pass

  # Instance method to read a DB "machine" document using IP as '_id'
  def get(self, ip):
    doc = None
    try:
      doc = self.db.get(ip)
      if doc:
        # print("DB.get():  ip=" + ip + " --> " + json.dumps(doc))
        pass
      else:
        # print("DB.get():  ip=" + ip + " <-- NOT FOUND! **********")
        doc = None
    except Exception as e:
      print("*** Exception during DB.get(" + ip + "):")
      traceback.print_exc()
      doc = None
    return doc

  # Instance method to write one DB "machine" document using IP as '_id'
  def put(self, ip, machine):
    try:
      doc = machine
      doc['_id'] = ip
      # Does it exist in the DB already?
      existing = self.get(ip)
      if existing:
        doc['_rev'] = existing['_rev']
        # print("DB.put: [update] " + json.dumps(doc))
        self.db[ip] = doc
      else:
        # print("DB.put: [new] " + json.dumps(doc))
        self.db.save(doc)
    except Exception as e:
      print("*** Exception during DB.put(" + machine['_id'] + "):")
      traceback.print_exc()
      doc = None

  # Instance method for stringification
  def __str__(self):
    return "DB( name:" + self.name + ", docs:" + str(len(self.db.view('_all_docs'))) + " )"



