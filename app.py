from flask import Flask, jsonify, request
from flask_cors import CORS
import psycopg2

conn = psycopg2.connect(database="mydb",
                        host="db",
                        user="myuser",
                        password="mypassword",
                        port="5432")

cursor = conn.cursor()

app = Flask(__name__)
CORS(app)

cursor.execute("create table if not exists movies (id SERIAL primary key, name text not null);")
conn.commit()

@app.route('/movies', methods=['GET', 'POST'])
def movies():
    if request.method == 'GET':
        cursor.execute("select * from movies;")
        data = cursor.fetchall()
        if data == None:
            return jsonify(data), 200
        else:
            return jsonify(convert(data)), 200
    else:
        name = request.get_json().get('name')
        cursor.execute("INSERT INTO movies (name) VALUES ('%s') RETURNING *;" % (name))
        conn.commit()
        data = cursor.fetchall()
        return jsonify(convertToDictionary(data, 0)), 201

@app.route('/movies/id/<id>', methods=['GET', 'DELETE'])
def searchByID(id):
    if request.method == 'DELETE':
        cursor.execute("delete from movies where id = '%s' RETURNING id" % id)
        conn.commit()
        data = cursor.fetchone()
        if (data != None):
            if data[0] == int(id):
                return jsonify(), 204
            else:
                return jsonify(), 404
        else:
            return jsonify(), 404
    else:
        cursor.execute("select * from movies where id = %s;" % id)
        data = cursor.fetchall()
        if len(data) <= 0:
            return jsonify(), 404
        else:
            return jsonify(convertToDictionary(data, 0)), 200

@app.route('/movies/name/<name>', methods=['GET'])
def searchByName(name):
    cursor.execute("select * from movies where LOWER(\"name\") = LOWER('%s');" % name)
    data = cursor.fetchall()
    return jsonify(convert(data)), 200

def convertToDictionary(liste, index):
    return {"id": liste[index][0], "name": liste[index][1]}

def convert(liste):
   new_list = liste
   for i in range(0, len(liste)):
        new_list[i] = convertToDictionary(new_list, i)
   return new_list

if __name__ == "__main__":
    app.run()