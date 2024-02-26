from flask import Flask, send_from_directory, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api, Resource, reqparse, fields, marshal_with
from flask_swagger_ui import get_swaggerui_blueprint
from sqlalchemy.exc import IntegrityError
from datetime import datetime
from flasgger import Swagger
from flasgger.utils import swag_from
import re

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://projeto_final_qnuq_user:RILa2bNqeRRoxtsLoZapj7bWo6IRlZNw@dpg-cne8ji5jm4es739o2uu0-a.oregon-postgres.render.com/projeto_final_qnuq'
db = SQLAlchemy(app)
api = Api(app)

# Rota para servir o arquivo swagger.json
@app.route('/api-docs/swagger.json')
def send_swagger_json():
    return send_from_directory('.', 'swagger.json')

# Modelo de Usuário
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), nullable=False, unique=True)
    foto = db.Column(db.String(100))
    postagens = db.relationship('Postagem', backref='autor', lazy=True)

# Modelo de Postagem
class Postagem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(100), nullable=False)
    texto = db.Column(db.Text, nullable=False)
    data = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    usuario_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    tema_id = db.Column(db.Integer, db.ForeignKey('tema.id'), nullable=False)

# Modelo de Tema
class Tema(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    descricao = db.Column(db.String(50), nullable=False)
    postagens = db.relationship('Postagem', backref='tema', lazy=True)

# Parser para validar entrada de dados do Usuário
user_parser = reqparse.RequestParser()
user_parser.add_argument('nome', type=str, required=True, help='Nome do usuário é obrigatório')
user_parser.add_argument('email', type=str, required=True, help='E-mail do usuário é obrigatório')
user_parser.add_argument('foto', type=str)

# Parser para validar entrada de dados da Postagem
post_parser = reqparse.RequestParser()
post_parser.add_argument('titulo', type=str, required=True, help='Título da postagem é obrigatório')
post_parser.add_argument('texto', type=str, required=True, help='Texto da postagem é obrigatório')
post_parser.add_argument('usuario_id', type=int, required=True, help='ID do usuário é obrigatório')
post_parser.add_argument('tema_id', type=int, required=True, help='ID do tema é obrigatório')

# Parser para validar entrada de dados do Tema
tema_parser = reqparse.RequestParser()
tema_parser.add_argument('descricao', type=str, required=True, help='Descrição do tema é obrigatória')

# Serializer para formatar a saída da Postagem
postagem_fields = {
    'id': fields.Integer,
    'titulo': fields.String,
    'texto': fields.String,
    'data': fields.DateTime(dt_format='iso8601'),
    'usuario_id': fields.Integer,
    'tema_id': fields.Integer,
}

# Serializer para formatar a saída do Usuário
user_fields = {
    'id': fields.Integer,
    'nome': fields.String,
    'email': fields.String,
    'foto': fields.String,
    'postagens': fields.Nested(postagem_fields),
}

# Serializer para formatar a saída do Tema
tema_fields = {
    'id': fields.Integer,
    'descricao': fields.String,
    'postagens': fields.Nested(postagem_fields),
}

# Endpoint para Usuários
class UserResource(Resource):
    @swag_from('swagger/user_get.yml', methods=['GET'])
    @marshal_with(user_fields)
    def get(self, user_id=None):
        if user_id:
            user = User.query.get(user_id)
            if user:
                return user
            else:
                return {'message': 'Usuário não encontrado'},   404
        else:
            users = User.query.all()
            return users

    @swag_from('swagger/user_post.yml', methods=['POST'])
    @marshal_with(user_fields)  # Adicione o decorador marshal_with
    def post(self):
        data = user_parser.parse_args()
        if len(data['nome']) <   3:
            return {'message': 'Nome deve ter no mínimo   3 caracteres'},   400
        if len(data['email']) <   5:
            return {'message': 'E-mail deve ter no mínimo   5 caracteres'},   400
        if not re.match(r"[^@]+@[^@]+\.[^@]+", data['email']):
            return {'message': 'E-mail inválido'},   400
        existing_user = User.query.filter_by(email=data['email']).first()
        if existing_user:
            return {'message': 'E-mail já cadastrado'},   400
        try:
            new_user = User(nome=data['nome'], email=data['email'], foto=data['foto'])
            db.session.add(new_user)
            db.session.commit()
            return {'message': 'Usuário criado com sucesso', 'user': new_user},   201
        except IntegrityError:
            db.session.rollback()
            return {'message': 'E-mail já cadastrado'},   400

    @swag_from('swagger/user_put.yml', methods=['PUT'])
    @marshal_with(user_fields)  # Adicione o decorador marshal_with
    def put(self, user_id):
        user = User.query.get(user_id)
        if not user:
            return {'message': 'Usuário não encontrado'},   404
        data = user_parser.parse_args()
        user.nome = data['nome']
        user.email = data['email']
        user.foto = data['foto']
        db.session.commit()
        return {'message': 'Usuário atualizado com sucesso', 'user': user},   200

    @swag_from('swagger/user_delete.yml', methods=['DELETE'])
    def delete(self, user_id):
        user = User.query.get(user_id)
        if not user:
            return {'message': 'Usuário não encontrado'},   404
        db.session.delete(user)
        db.session.commit()
        return {'message': 'Usuário removido com sucesso'},   200

# Endpoint para Postagens
class PostagemResource(Resource):
    @swag_from('swagger/postagem_get.yml', methods=['GET'])
    @marshal_with(postagem_fields)
    def get(self, postagem_id=None):
        if postagem_id:
            postagem = Postagem.query.get(postagem_id)
            if postagem:
                return postagem
            else:
                return {'message': 'Postagem não encontrada'},   404
        else:
            postagens = Postagem.query.all()
            return postagens

    @swag_from('swagger/postagem_post.yml', methods=['POST'])
    @marshal_with(postagem_fields)  # Adicione o decorador marshal_with
    def post(self):
        data = post_parser.parse_args()
        try:
            new_postagem = Postagem(
                titulo=data['titulo'],
                texto=data['texto'],
                usuario_id=data['usuario_id'],
                tema_id=data['tema_id']
            )
            db.session.add(new_postagem)
            db.session.commit()
            return {'message': 'Postagem criada com sucesso', 'postagem': new_postagem},   201
        except IntegrityError:
            db.session.rollback()
            return {'message': 'Erro ao criar postagem'},   400

    @swag_from('swagger/postagem_put.yml', methods=['PUT'])
    @marshal_with(postagem_fields)  # Adicione o decorador marshal_with
    def put(self, postagem_id):
        postagem = Postagem.query.get(postagem_id)
        if not postagem:
            return {'message': 'Postagem não encontrada'},   404
        data = post_parser.parse_args()
        postagem.titulo = data['titulo']
        postagem.texto = data['texto']
        postagem.usuario_id = data['usuario_id']
        postagem.tema_id = data['tema_id']
        db.session.commit()
        return {'message': 'Postagem atualizada com sucesso', 'postagem': postagem},   200

    @swag_from('swagger/postagem_delete.yml', methods=['DELETE'])
    def delete(self, postagem_id):
        postagem = Postagem.query.get(postagem_id)
        if not postagem:
            return {'message': 'Postagem não encontrada'},   404
        db.session.delete(postagem)
        db.session.commit()
        return {'message': 'Postagem removida com sucesso'},   200

# Endpoint para Temas
class TemaResource(Resource):
    @swag_from('swagger/tema_get.yml', methods=['GET'])
    @marshal_with(tema_fields)
    def get(self, tema_id=None):
        if tema_id:
            tema = Tema.query.get(tema_id)
            if tema:
                return tema
            else:
                return {'message': 'Tema não encontrado'},   404
        else:
            temas = Tema.query.all()
            return temas

    @swag_from('swagger/tema_post.yml', methods=['POST'])
    @marshal_with(tema_fields)  # Adicione o decorador marshal_with
    def post(self):
        data = tema_parser.parse_args()
        try:
            new_tema = Tema(descricao=data['descricao'])
            db.session.add(new_tema)
            db.session.commit()
            return {'message': 'Tema criado com sucesso', 'tema': new_tema},   201
        except IntegrityError:
            db.session.rollback()
            return {'message': 'Erro ao criar tema'},   400

    @swag_from('swagger/tema_put.yml', methods=['PUT'])
    @marshal_with(tema_fields)  # Adicione o decorador marshal_with
    def put(self, tema_id):
        tema = Tema.query.get(tema_id)
        if not tema:
            return {'message': 'Tema não encontrado'},   404
        data = tema_parser.parse_args()
        tema.descricao = data['descricao']
        db.session.commit()
        return {'message': 'Tema atualizado com sucesso', 'tema': tema},   200

    @swag_from('swagger/tema_delete.yml', methods=['DELETE'])
    def delete(self, tema_id):
        tema = Tema.query.get(tema_id)
        if not tema:
            return {'message': 'Tema não encontrado'},   404
        db.session.delete(tema)
        db.session.commit()
        return {'message': 'Tema removido com sucesso'},   200

@app.route('/')
def index():
    return redirect('/api-docs')

# Adicionando recursos de Usuário, Postagem e Tema ao API
api.add_resource(UserResource, '/users', '/users/<int:user_id>')
api.add_resource(PostagemResource, '/postagens', '/postagens/<int:postagem_id>')
api.add_resource(TemaResource, '/temas', '/temas/<int:tema_id>')

# Configurando a documentação Swagger
swaggerui_blueprint = get_swaggerui_blueprint(
    '/api-docs',
    '/api-docs/swagger.json',  # Alterado o caminho para apontar para o arquivo swagger.json
    config={
        'app_name': "API de Usuários, Postagens e Temas"
    }
)
app.register_blueprint(swaggerui_blueprint, url_prefix='/api-docs')

# Criação das tabelas do banco de dados
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)