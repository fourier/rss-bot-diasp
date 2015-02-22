#! /usr/bin/python

import sqlite3

class BotsDB(object):
  SELECT_TABLES = "SELECT name FROM sqlite_master WHERE type='table' AND name='rss_bot'"
  CREATE_RSS_BOT_TABLE = """
  CREATE TABLE rss_bot (
       id INTEGER PRIMARY KEY,
       name TEXT,
       rss_url TEXT,
       pod_url TEXT,
       username TEXT,
       password TEXT
);
"""
  CREATE_RSS_FEED_POSTS_TABLE = """
  CREATE TABLE rss_feed_posts (
       id INTEGER PRIMARY KEY,
       rss_bot_id INTEGER,
       post_id TEXT,
       published DATETIME DEFAULT CURRENT_TIMESTAMP
);
  """
  INSERT_BOT_ENTRY = """
  INSERT OR REPLACE INTO rss_bot (id, name, rss_url, pod_url, username, password) VALUES ((SELECT id FROM rss_bot WHERE name = ?), ?, ?, ?, ?, ?)
  """
  SELECT_ALL_BOTS = "SELECT * FROM rss_bot"
  SELECT_BOT_ID = "SELECT id FROM rss_bot WHERE name = ?"
  REMOVE_RSS_FOR_BOT = """
  DELETE FROM rss_feed_posts WHERE rss_bot_id in
  (SELECT id FROM rss_bot WHERE name = ?)
  """
  REMOVE_RSS_BOT = "DELETE FROM rss_bot WHERE name = ?"
  def __init__(self, filename):
    self.open(filename)
    
  def __enter__(self):
    return self
  
  def __exit__(self, type, value, traceback):
    self.close()

  def open(self, filename):
    """
    Opens or creates the database specified in filename and
    if it was not exists creates the necessary tables
    """
    self.db = sqlite3.connect(filename)
    c = self.db.cursor()
    # verify if rss_bot table already exists
    c.execute(BotsDB.SELECT_TABLES)
    result = c.fetchone()
    if result == None:
      c.execute(BotsDB.CREATE_RSS_BOT_TABLE)
      c.execute(BotsDB.CREATE_RSS_FEED_POSTS_TABLE)

  def close(self):
    """
    Closes the database. From this point all operations will be invalid
    unless the open(filename) is called
    """
    self.db.commit()
    self.db.close()

  def add_bot(self, name, rss_url, pod_url, username, password):
    c = self.db.cursor()
    c.execute(BotsDB.INSERT_BOT_ENTRY, [name, name, rss_url, pod_url, username, password])
    self.db.commit()

  def remove_bot(self, name):
    if not(self.has_bot(name)):
      print "Not found bot " + name
      return
    c = self.db.cursor()
    c.execute(BotsDB.REMOVE_RSS_FOR_BOT, [name])
    c.execute(BotsDB.REMOVE_RSS_BOT, [name])
    self.db.commit()

  def has_bot(self, name):
    c = self.db.cursor()
    c.execute(BotsDB.SELECT_BOT_ID, [name])
    result = c.fetchone()
    return not(result == None)

  def print_bots(self):
    """
    Print all bots configured in the DB
    """
    # TODO: CSV output
    c = self.db.cursor()
    for row in c.execute(BotsDB.SELECT_ALL_BOTS):
      print "Bot:" + row[1] + " RSS: " + row[2] + " Pod: " + row[3] + " User: " + row[4] + " password: " + row[5]

  def create_posts_db(self, botname):
    """
    Creates an instance of PostDB wrapper based on botname
    """
    c = self.db.cursor()
    c.execute(BotsDB.SELECT_BOT_ID, [botname])
    result = c.fetchone()
    if result == None:
      return None
    return PostDBWrapper(self.db, result[0])

class PostDBWrapper(object):
  INSERT_POST = """
  INSERT INTO rss_feed_posts(rss_bot_id, post_id) 
  VALUES (?, ?)
  """
  FIND_POST = "SELECT * FROM rss_feed_posts WHERE rss_bot_id = ? AND post_id = ?"
  SELECT_BOT_WITH_ID = """
  SELECT name, rss_url, pod_url, username, password FROM rss_bot
  WHERE id = ?
  """

  def __init__(self, db, bot_id):
    self.db = db
    self.bot_id = bot_id

  def get_bot(self):
    c = self.db.cursor()
    c.execute(PostDBWrapper.SELECT_BOT_WITH_ID, [self.bot_id])
    return c.fetchone()

  def mark_as_posted(self, post_id):
    c = self.db.cursor()
    c.execute(PostDBWrapper.INSERT_POST, [self.bot_id, post_id])
    self.db.commit()

  def is_published(self, post_id):
    c = self.db.cursor()
    c.execute(PostDBWrapper.FIND_POST, [self.bot_id, post_id])
    result = c.fetchone()
    return not(result == None)

