import psycopg2
from flask import Flask, jsonify, request
from flask_cors import CORS

from config import load_config


def connect(config):
    """ Connect to the PostgreSQL database server """
    try:
        # connecting to the PostgreSQL server
        with psycopg2.connect(**config) as conn:
            print('Connected to the PostgreSQL server.')
            return conn
    except (psycopg2.DatabaseError, Exception) as error:
        print(error)
        return None


def tryReconnect(conn_local):
    try:
        cursor = conn_local.cursor()
        return conn_local
    except Exception as e:
        if conn_local:
            conn_local.close()
        conn_local = None
        conn_local = connect(load_config())
        return conn_local


conn = connect(load_config())

app = Flask(__name__)
CORS(app, support_credentials=True)


@app.route('/')
def hello_world():
    return 'Hello World!'


@app.get('/api/get_all_recipes')
def get_all_recipes():
    global conn
    conn = tryReconnect(conn)
    if conn is None:
        return jsonify(False), 500
    cursor = conn.cursor()
    try:
        cursor.execute('''SELECT id, title, category_id, people, time, description, ingredients, instructions
        --, c.name as category
            FROM recipes
                -- JOIN categories c on c.id = recipes.category_id
                ''')
        array = cursor.fetchall()
        new_array = []
        for elem in array:
            new_array.append({
                "id": elem[0],
                "title": elem[1],
                "category": elem[2],
                "people": elem[3],
                "time": elem[4],
                "description": elem[5],
                "ingredients": elem[6],
                "instructions": elem[7],
            })
        cursor.close()
        return jsonify(new_array), 201
    except Exception as e:
        print(e)
        cursor.close()
        return jsonify(False), 500


@app.post('/api/add_new_recipe')
def add_new_recipe():
    global conn
    conn = tryReconnect(conn)
    if conn is None:
        return jsonify(False), 500
    cursor = conn.cursor()
    data = request.json
    try:
        cursor.execute(f'''INSERT INTO recipes (title, category_id, people, time, description, ingredients, instructions) 
                    VALUES (%(title)s,
                            %(category)s,
                            %(people)s,
                            %(time)s,
                            %(description)s,
                            %(ingredients)s,
                            %(instructions)s)''',
                       {
                           'title': data['title'],
                           'category': data['category'],
                           'people': data['people'],
                           'time': data['time'],
                           'description': data['description'],
                           'ingredients': "{" + ",".join(data['ingredients']) + "}",
                           'instructions': data['instructions'],
                       })
        conn.commit()
        cursor.close()
        return jsonify(True), 201
    except Exception as e:
        print(e)
        cursor.close()
        return jsonify(False), 500


@app.post('/api/update_recipe')
def update_recipe():
    global conn
    conn = tryReconnect(conn)
    if conn is None:
        return jsonify(False), 500
    cursor = conn.cursor()
    data = request.json
    # try:
    cursor.execute(f'''UPDATE recipes SET title=%(title)s,
                                                 category_id=%(category)s,
                                                 people=%(people)s,
                                                 time=%(time)s,
                                                 description=%(description)s,
                                                 ingredients=%(ingredients)s,
                                                 instructions=%(instructions)s
                                  WHERE id=%(id)s''',
                   {
                       'id': data['id'],
                       'title': data['title'],
                       'category': data['category'],
                       'people': data['people'],
                       'time': data['time'],
                       'description': data['description'],
                       'ingredients': "{" + ",".join(data['ingredients']) + "}",
                       'instructions': data['instructions'],
                   })
    conn.commit()
    cursor.close()
    return jsonify(True), 201
    # except Exception as e:
    #     print(e)
    #     cursor.close()
    #     return jsonify(False), 500


if __name__ == '__main__':
    cursor = conn.cursor()
    cursor.execute('''SELECT * FROM categories''')
    print(cursor.fetchall())
    # app.run(port=10000, debug=True)
