from flask import Flask, jsonify, make_response, request
from flask_cors import CORS
from pymongo import MongoClient
import config
import pandas as pd
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from bson import ObjectId

# Configurações do MongoDB
client = MongoClient("mongodb://localhost:27017/")  # Altere para o URI de conexão do seu MongoDB

app = Flask(_name_)
CORS(app)
# Sua variável global
user_id_global = None 

@app.route('/')
def hello_world():
    response = make_response(jsonify(message="Hello, World!"), 200)
    return response


@app.route('/remedios', methods=['GET'])
def obter_remedios():
    # Buscar todos os documentos na coleção 'remedios'
    remedios = list(colecaoRemedios.find({}, {'_id': 0}))  # Exclui o campo '_id' dos resultados
    
    return jsonify(remedios)


@app.route('/login', methods=['POST'])
def login():
    
    login_data = request.json
    email = login_data.get('email')
    password = login_data.get('password')

    user = client.db_ye.users.find_one({"email": email})

    if user and check_password_hash(user['password'], password):
        user['_id'] = str(user['_id'])
        global user_id_global
        user_id_global = user['_id']
        # Login bem-sucedido, retornar dados do usuário
        print("Login bem-sucedido")
        return jsonify(user)
    else:
        # Login falhou
        return jsonify({'error': 'Login failed'}), 401