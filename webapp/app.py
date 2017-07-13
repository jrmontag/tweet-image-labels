import logging
import sys

from flask import Flask, render_template, request, jsonify, json
import pymysql.cursors

app = Flask(__name__)

# nb: this still doesn't log at INFO level unless the app
#   is run in DEBUG mode  
app.logger.setLevel(logging.INFO)

# testing or "prod"?
# this test table can be created as shown in create_schema.sql 
#   - test_class* has ~30 rows
#   - class* has ~10k rows 
testing = False 

table = 'test_classifications' if testing else 'classifications' 
app.logger.info('querying against table: {}'.format(table))

# establish db connection 
#   - this user/pwd combo should match create_schema.sql_
connection = pymysql.connect(host='localhost',
                             user='imgapp',
                             password='apassword',
                             db='image_labels',
                             charset='utf8mb4',
                             autocommit=True,
                             cursorclass=pymysql.cursors.DictCursor)

@app.route('/')
def hello_world():
    """Main landing page"""
    return render_template('index.html')

@app.route('/labels.json')
def labels():
    with connection.cursor() as cursor:
        sql = "select * from labels"
        cursor.execute(sql) 
        result = cursor.fetchall()
        return jsonify(result)
        
@app.route('/data/')
def data():
    limit = request.args.get("limit", 1)
    offset = request.args.get("offset", 0)

    filter = request.args.get("filter", None)
    where_clause = "WHERE label_id IS NULL" if filter else ""

    # intro random sampling to accomodate large n 
    # note: this is the slowest, but easiest way http://jan.kneschke.de/projects/mysql/order-by-rand/
    rand_clause = "order by rand()"
    
    with connection.cursor() as cursor:
        sql = "select * from {} {} {} limit {} offset {}".format(table, where_clause, rand_clause, limit, offset)
        cursor.execute(sql) 
        response = cursor.fetchall()
        app.logger.info("queried with where_clause={}, limit={}, rand_clause={} offset={}".format(where_clause, limit, rand_clause, offset))
        result = []
        for r in response:
            result.append( {'id': r['id'], 
                            'link':r['link'],   
                            'tweet_id':r['tweet_id'],
                            'label_id':r['label_id'], 
                            'predictions': [    
                                            [r['keyword1'], r['score1']],
                                            [r['keyword2'], r['score2']],
                                            [r['keyword3'], r['score3']],
                                            [r['keyword4'], r['score4']],
                                            [r['keyword5'], r['score5']]
                            ]})
            app.logger.info("returned data with id={}, tweet_id={}, label_id={}".format(r['id'],
                                                                                        r['tweet_id'],
                                                                                        r['label_id']))
        if len(result) == 0: 
            app.logger.info("********** result is empty; are there any non-NULL entries left in the DB? ***********")
        return jsonify(result)

# TODO: should the two /data/ endpoints be the same function with stacked @app.route decorators?
#   cf: http://flask.pocoo.org/docs/0.11/quickstart/#rendering-templates
@app.route('/data/<int:img_id>.json', methods=['PUT','GET'])
def label(img_id):
    """
    GET: return the current label for <img_id>
    POST: update the current label for <img_id>
    """
    if request.method == 'PUT':
        #TODO: figure out how to get `request` to properly parse json on PUT
        req_dict = json.loads(request.data.decode())

        with connection.cursor() as cursor:
            label_id = req_dict['label_id']
            sql = "update {} set label_id={} where id={}".format(table, label_id, img_id)
            cursor.execute(sql) 
            app.logger.info("updated id={} to label_id={}".format(img_id, label_id))
            return jsonify(status='ok')
    else: 
        with connection.cursor() as cursor:
            sql = "select * from {} where id={}".format(table, img_id)
            cursor.execute(sql) 
            app.logger.info("queried for id={}".format(img_id))
            result = cursor.fetchone()
            return jsonify(result)

