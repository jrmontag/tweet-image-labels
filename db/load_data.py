#!/usr/bin/env python
# -*- coding: UTF-8 -*-
__author__="Josh Montague"
__license__="MIT License"

"""
Reads db data from stdin: 
$ cat datafile.csv | python load_data.py
"""

import pymysql.cursors
import sys

# connect to the database
connection = pymysql.connect(host='localhost',
                             user='imgapp',
                             password='apassword',
                             db='image_labels',
                             charset='utf8mb4',
                             autocommit=True,
                             cursorclass=pymysql.cursors.DictCursor)

try:
    with connection.cursor() as cursor:
        for line in sys.stdin:
            # fields ~ [ tweet_id, url, kw1, p1, ..., kw5, p5 ]
            fields = line.split(',')

            # create a new record
            cols = ["`tweet_id`",
                    "`link`",
                    "`keyword1`",
                    "`score1`",
                    "`keyword2`",
                    "`score2`",
                    "`keyword3`",
                    "`score3`",
                    "`keyword4`",
                    "`score4`",
                    "`keyword5`",
                    "`score5`",
                    ]

            # generate + execute command string
            sql = "INSERT INTO `classifications` ( {} ) VALUES ( {} )".format(','.join(cols), ','.join(["%s"]*len(cols)))
            cursor.execute(sql, fields)
finally:
    connection.close()
