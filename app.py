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
    # REGION FUNCTIONS USUARIOS
# Função para retornar os dados do usuário com base no ID do MongoDB
def get_user_by_id(user_id):
    user = client.db_ye.users.find_one({'_id': ObjectId(user_id)})
    if user:
        # Remover ObjectId para evitar erro de serialização JSON
        del user['_id']
        return user
    else:
        return None

def calculate_imc(peso, altura):
    print("peso -- ", peso)
    print("altura ----", altura)
    # Converte altura para metros
    altura_meters = float(altura) / 100.0  # Convertendo para float
    # Calcula IMC
    imc = int(peso) / (altura_meters ** 2)
    return imc

# FIM REGION FUNCTIONS UTILS USUARIO

# user@example.com
# password123

# REGION USUARIOS
@app.route('/insert_user', methods=['POST'])
def insert_user():
    print("BATI AQUI")
    # Obtém os dados do formulário
    full_name = request.json.get('full_name')
    email = request.json.get('email')
    password = request.json.get('password')
    peso = request.json.get('peso')
    altura = request.json.get('altura')
    last_bp_measurement = request.json.get('last_bp_measurement')
    last_glucose_measurement = request.json.get('last_glucose_measurement')

    # Verifica se todos os campos obrigatórios estão presentes
    if not (full_name and email and password and peso and altura):
        return jsonify({'message': 'Preencha todos os campos obrigatórios'}), 400

    # Verifica se o usuário já existe
    existing_user = client.db_ye.users.find_one({'email': email})
    if existing_user:
        return jsonify({'message': 'Usuário já existe'}), 400
    else:
        # Calcula IMC
        imc = calculate_imc(peso, altura)
        # Hash da senha
        hashed_password = generate_password_hash(password)
        # Insere o usuário na coleção
        user_data = {
            'full_name': full_name,
            'email': email,
            'password': hashed_password,
            'peso': peso,
            'altura': altura,
            'last_bp_measurement': last_bp_measurement,
            'last_glucose_measurement': last_glucose_measurement,
            'imc': imc,
            'created_at': datetime.now()
        }
        client.db_ye.users.insert_one(user_data)
        return jsonify({'message': 'Usuário inserido com sucesso'}), 200

@app.route('/all-users', methods=['GET'])
def get_users():
    users = list(client.db_ye.users.find())
    # Convertendo ObjectId para string
    for user in users:
        user['_id'] = str(user['_id'])
    return jsonify(users), 200

# Rota para retornar os dados do usuário com base no ID
@app.route('/users/<string:user_id>', methods=['GET'])
def get_user(user_id):
    user = get_user_by_id(user_id)
    if user:
        return jsonify(user), 200
    else:
        return jsonify({'error': 'Usuário não encontrado'}), 404
# FIM REGION USUARIOS 

# REGION EXAMES INFO BASICA 
@app.route('/grava_exames', methods=['POST'])
def adicionar_info_usuario():
    print("bati aqui dentro")
    global user_id_global
    print("user global ", user_id_global);

    dados_requisicao = request.json
    # Obter os dados do formulário
    user_id = user_id_global
    tipo_exame = dados_requisicao.get('tipo_exame')
    data_exame = dados_requisicao.get('data_exame')
    valor_exame = dados_requisicao.get('valor_exame')


    print(user_id, " ---- user-id ")
    # Verificar se o usuário existe na coleção de usuários
    user = client.db_ye.users.find_one({'_id': ObjectId(user_id)})

    # user = client.db_ye.users.find_one({'_id': user_id})
    # print(user)
    if not user:
        return jsonify({'mensagem': 'Usuário não encontrado'}), 404

    client.db_ye.exames_laboratoriais.insert_one({
        'user_id': user['_id'],
        'tipo_exame': tipo_exame,
        'data_exame': data_exame,
        'descricao_exame': valor_exame
    })
    
    return jsonify({'mensagem': 'Informações adicionadas com sucesso'}), 200


@app.route('/exames', methods=['GET'])
def listar_exames():
    # Verificar se o usuário está autenticado (você pode implementar essa lógica)
    global user_id_global
    print(user_id_global, "user_id_global")

    # Suponha que você tenha um campo 'user_id' no exame que se refere ao ID do usuário
    user_id = ObjectId(user_id_global)
    if user_id:
        # Consultar exames do usuário com base no user_id
        exames_cursor = client.db_ye.exames_laboratoriais.find({'user_id': user_id})
        print(exames_cursor, "exames cursor")
        
        # Converter os resultados em uma lista de dicionários
        exames_list = []
        for exame in exames_cursor:
            exame['_id'] = str(exame['_id'])
            exame['user_id'] = str(exame['user_id'])  # Convertendo ObjectId para string
            exames_list.append(exame)
        
        print(exames_list, "EXAMES LABORATORIAIS ")  # Para verificar no console
        
        # Retornar a lista de exames como JSON
        return jsonify(exames_list), 200
    else:
        return jsonify({'error': 'ID do usuário não fornecido'}), 400


@app.route('/grava_medicamentos', methods=['POST'])
def adicionar_medicamentos_usuario():
    print("bati aqui dentro")
    global user_id_global
    print("user global ", user_id_global);

    dados_requisicao = request.json
    # Obter os dados do formulário
    user_id = user_id_global
    nome_medicamento = dados_requisicao.get('nome_medicamento')
    horario_medicamento = dados_requisicao.get('horario_medicamento')
    periodo_medicamento = dados_requisicao.get('periodo_medicamento')


    print(user_id, " ---- user-id ")
    # Verificar se o usuário existe na coleção de usuários
    user = client.db_ye.users.find_one({'_id': ObjectId(user_id)})

    # user = client.db_ye.users.find_one({'_id': user_id})
    # print(user)
    if not user:
        return jsonify({'mensagem': 'Usuário não encontrado'}), 404
    
    # Adicionar informações na coleção info_usuarios
    client.db_ye.medicamentos_usuario.insert_one({
        'user_id': user['_id'],
        'nome_medicamento': nome_medicamento,
        'horario_medicamento': horario_medicamento,
        'periodo_medicamento': periodo_medicamento
    })
    
    return jsonify({'mensagem': 'Informações adicionadas com sucesso'}), 200


@app.route('/medicamentos', methods=['GET'])
def listar_medicamentos():
    print("BATI NA MEDICAMENTOS")
    # Verificar se o usuário está autenticado (você pode implementar essa lógica)
    global user_id_global
    print(user_id_global, "user_id_global")

    # Suponha que você tenha um campo 'user_id' no exame que se refere ao ID do usuário
    user_id = ObjectId(user_id_global)
    if user_id:
        # Consultar exames do usuário com base no user_id
        medicamentos_cursor = client.db_ye.medicamentos_usuario.find({'user_id': user_id})
        # Converter os resultados em uma lista de dicionários
        medicamento_list = []
        for medicamento in medicamentos_cursor:
            medicamento['_id'] = str(medicamento['_id'])
            medicamento['user_id'] = str(medicamento['user_id'])  # Convertendo ObjectId para string
            medicamento_list.append(medicamento)
        
        print(medicamento_list, "EXAMES LABORATORIAIS ")  # Para verificar no console
        
        # Retornar a lista de exames como JSON
        return jsonify(medicamento_list), 200
    else:
        return jsonify({'error': 'ID do usuário não fornecido'}), 400


# FIM REGION CONSULTAS
@app.route('/get_info_usuarios/<user_id>', methods=['GET'])
def get_info_usuarios(user_id):
    print("user_id", user_id)
    # Verificar se user_id é um ObjectId válido
    try:
        id_user = ObjectId(user_id)
    except Exception as e:
        return jsonify({'mensagem': 'ID de usuário inválido'}), 400

    # Encontrar o usuário na coleção users
    user = client.db_ye.users.find_one({"_id": id_user})
    if not user:
        return jsonify({'mensagem': 'Usuário não encontrado'}), 404
    else:
        print("Achei o usuario")
    
    print(user)

    merged_data = {
        'nome': user.get('full_name'),
        'email': user.get('email'),
        'last_bp_measurement': user.get('last_bp_measurement'),
        'last_glucose_measurement': user.get('last_glucose_measurement'),
        'imc': user.get('imc'),
    }
    print(merged_data)

    return jsonify(merged_data), 200


if _name_ == '_main_':
    app.run(debug=True, port=5000)


