Diaspora rss bot
================
Simple diaspora bot based on [feedDiasp](https://github.com/Debakel/feedDiasp).
This bot uses the SQLite database to store configuration and published feeds; therefore could be configured to use several bots in the same database and do not require multiple instances.

Installation
============
Run 
```
pip install feedparser
pip install facepy 
```
to install feedDiasp dependencies.

Run

```
git submodule update --init --recursive
```
to download [feedDiasp](https://github.com/fourier/feedDiasp) and its *diaspy* dependency.

Usage
=====
To add the bot
```
./rss_bot.py --add BOT_NAME http://example.com/rss https://diaspora.pod.com/ user_name user_password [--db filename]
```
where the BOT_NAME is the string identifying bot in the database (i.e. GOG or HN or whatever short name). To modify the bot use the add command with the same bot name.
Here ```--db filename``` is an optional argument specifying the database file. By default it is a **rss_bots.db** in the current directory.

To update the bot (download rss feeds and publish them as a user):
```
./rss_bot.py --update BOT_NAME [--db filename]
```
Run with the *-h* argument to read all command line arguments desriptions.



