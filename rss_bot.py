#! /usr/bin/env python

import os,inspect
import argparse
from sys import exit
from argparse import RawTextHelpFormatter

from feedDiasp import RSSParser
from feedDiasp import FeedDiasp
from botsdb import BotsDB

DEFAULT_DB_NAME = "rss_bots.db"

HELP_DESCRIPTION = """
Diaspora RSS bot. Supports different bots in the same database.
"""
HELP_ADD_CMDARG = """Add the bot to the database.
bot_name - text bot name (like HN or GOG) to use later
rss_url - URL of the RSS feed
pod_url - address of the pod, like https://joindiaspora.com/
username - name of the user on this pod which will post RSS feed news
password - password of this user on the pod"""

HELP_REMOVE_CMDARG = "Removes the bot and its data from the database"

HELP_UPDATE_CMDARG = """Updates the bot: download feeds and post them.
bot_name - name of the bot in the database"""

HELP_LIST_CMDARG = "List bots in the database"

HELP_DB_CMDARG = "Specify the database file. If not specified: " + \
  DEFAULT_DB_NAME + \
  "\nfilename file with the database"


def process_cmdargs():
  parser = argparse.ArgumentParser(formatter_class = RawTextHelpFormatter,
                                   description = HELP_DESCRIPTION)
  group = parser.add_mutually_exclusive_group(required = True)
  group.add_argument("--add",
                      nargs = 5,
                      metavar = ('bot_name','rss_url', 'pod_url', 'username', 'password'),
                      dest = 'add_bot',
                      help = HELP_ADD_CMDARG)
  group.add_argument("--remove",
                      metavar = 'bot_name',
                      dest = 'remove_bot',
                      help = HELP_REMOVE_CMDARG)
  group.add_argument("--update",
                      metavar = 'bot_name',
                      dest = 'update_bot',
                      help = HELP_UPDATE_CMDARG)
  group.add_argument("--list",
                      action="store_true",
                      help = HELP_LIST_CMDARG)
  parser.add_argument("--db",
                      metavar = 'filename',
                      dest = 'dbfile',
                      default = DEFAULT_DB_NAME,
                      help = HELP_DB_CMDARG)
  
  args = parser.parse_args()
  return args

def main():
  # process command line arguments
  args = process_cmdargs()
  # open the database
  db = BotsDB(args.dbfile)

  # process the add bot command
  if not(args.add_bot == None):
    name = args.add_bot[0]
    rss_url = args.add_bot[1]
    pod_url = args.add_bot[2]
    username = args.add_bot[3]
    password = args.add_bot[4]
    db.add_bot(name, rss_url, pod_url, username, password)
    print "Done"
  elif args.list == True:
    db.print_bots()
  elif not(args.remove_bot == None):
    db.remove_bot(args.remove_bot)
  elif not(args.update_bot == None):
    # create wrapper for FeedDiasp
    postdb = db.create_posts_db(args.update_bot)
    if postdb == None:
      print "Not found bot named " + name
      exit(1)
    # get the bot
    bot = postdb.get_bot()
    name = bot[0]
    rss_url = bot[1]
    pod_url = bot[2]
    username = bot[3]
    password = bot[4]
    # create RSS parser
    rss = RSSParser(url=rss_url)
    # create the feeder and publish changes
    bot = FeedDiasp(parser=rss, pod=pod_url, username=username, password=password, db=postdb)
    bot.publish()


if __name__ == '__main__':
    main()
