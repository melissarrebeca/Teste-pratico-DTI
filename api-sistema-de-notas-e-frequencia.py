from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

import psycopg2
from psycopg2 import sql
from psycopg2.extras import RealDictCursor

import logging
import traceback

import os

app = Flask(__name__, static_folder="C:/Users/melis/Teste-prático-DTI-v2")
CORS(app)

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    if path != "" and os.path.exists(app.static_folder + '/' + path):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index-com-bootstrap.html')

logging.basicConfig(level=logging.DEBUG)

parametros = {
    "host": "localhost",
    "database": "sistema-de-notas-e-frequencia-banco-de-dados",
    "user": "postgres",
    "password": "1234"
}

def conectarBd():
    try:
        conectar = psycopg2.connect(**parametros)
        logging.info("Conexão com o banco de dados estabelecida com sucesso")
        return conectar
    except Exception as e:
        logging.error(f"Erro ao conectar ao banco de dados: {e}")
        return None

def criar_tabela():
    conectar = conectarBd()
    if not conectar:
        logging.error("Não foi possível conectar ao banco de dados para criar a tabela")
        return
    
    cursor = conectar.cursor()
    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS alunos (
                id SERIAL PRIMARY KEY,
                nome VARCHAR(100) NOT NULL,
                notaDisciplina01 NUMERIC(5,2),
                notaDisciplina02 NUMERIC(5,2),
                notaDisciplina03 NUMERIC(5,2),
                notaDisciplina04 NUMERIC(5,2),
                notaDisciplina05 NUMERIC(5,2),
                frequencia NUMERIC(5,2)
            )
        """)
        conectar.commit()
        logging.info("Tabela 'alunos' criada ou já existente.")
    except Exception as e:
        logging.error(f"Erro ao criar tabela: {e}")
        logging.error(traceback.format_exc())
    finally:
        cursor.close()
        conectar.close()

@app.route('/api/alunos', methods=['POST'])
def adicionarAluno():
    dados = request.json
    conectar = conectarBd()
    cursor = conectar.cursor(cursor_factory = RealDictCursor)

    try:
        cursor.execute("""
            INSERT INTO alunos (nome, notaDisciplina01, notaDisciplina02, notaDisciplina03, notaDisciplina04, notaDisciplina05, frequencia) 
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (dados['nome'], dados['notaDisciplina01'], dados['notaDisciplina02'], dados['notaDisciplina03'], dados['notaDisciplina04'], dados['notaDisciplina05'], dados['frequencia'])
        )

        novo_id = cursor.fetchone()['id']
        conectar.commit()

        return jsonify({"mensagem": "Aluno cadastrado com sucesso!", "id": novo_id}), 201
    
    except Exception as e:
        conectar.rollback()

        return jsonify({"erro": str(e)}), 400
    
    finally:
        cursor.close()
        conectar.close()

@app.route('/api/alunos', methods=['GET'])
def listarAlunos():
    try:
        conectar = conectarBd()
        if not conectar:
            return jsonify({"erro": "Não foi possível conectar ao banco de dados"}), 500

        cursor = conectar.cursor(cursor_factory=RealDictCursor)
        cursor.execute("""
            SELECT 
                id, 
                nome, 
                notaDisciplina01, 
                notaDisciplina02, 
                notaDisciplina03, 
                notaDisciplina04, 
                notaDisciplina05, 
                frequencia,
                (notaDisciplina01 + notaDisciplina02 + notaDisciplina03 + notaDisciplina04 + notaDisciplina05) / 5 as media_geral
            FROM alunos
        """)
        alunos = cursor.fetchall()

        alunos_formatados = []
        for aluno in alunos:
            aluno_formatado = {
                "id": aluno['id'],
                "nome": aluno['nome'],
                "notas": {
                    "Disciplina 1": aluno['notadisciplina01'],
                    "Disciplina 2": aluno['notadisciplina02'],
                    "Disciplina 3": aluno['notadisciplina03'],
                    "Disciplina 4": aluno['notadisciplina04'],
                    "Disciplina 5": aluno['notadisciplina05']
                },
                "media_geral": round(aluno['media_geral'], 2),
                "frequencia": aluno['frequencia']
            }
            alunos_formatados.append(aluno_formatado)

        return jsonify(alunos_formatados), 200

    except Exception as e:
        logging.error(f"Erro ao listar alunos: {str(e)}")
        return jsonify({"erro": "Ocorreu um erro ao listar os alunos"}), 500

    finally:
        if cursor:
            cursor.close()
        if conectar:
            conectar.close()

@app.route('/api/media-turma', methods=['GET'])
def mediasTurma():
    try:
        conectar = conectarBd()
        if not conectar:
            return jsonify({"erro": "Não foi possível conectar ao banco de dados"}), 500

        cursor = conectar.cursor(cursor_factory=RealDictCursor)
        cursor.execute("SELECT COUNT(*) FROM alunos")
        count = cursor.fetchone()['count']
        
        if count == 0:
            return jsonify({"mensagem": "Não há registros de alunos no banco de dados"}), 200

        cursor.execute("""
            SELECT 
                ROUND(AVG(notaDisciplina01)::numeric, 2) as media_disciplina01,
                ROUND(AVG(notaDisciplina02)::numeric, 2) as media_disciplina02,
                ROUND(AVG(notaDisciplina03)::numeric, 2) as media_disciplina03,
                ROUND(AVG(notaDisciplina04)::numeric, 2) as media_disciplina04,
                ROUND(AVG(notaDisciplina05)::numeric, 2) as media_disciplina05
            FROM alunos
        """)
        medias = cursor.fetchone()

        medias_formatadas = {
            "Disciplina 1": medias['media_disciplina01'],
            "Disciplina 2": medias['media_disciplina02'],
            "Disciplina 3": medias['media_disciplina03'],
            "Disciplina 4": medias['media_disciplina04'],
            "Disciplina 5": medias['media_disciplina05']
        }

        return jsonify(medias_formatadas), 200

    except Exception as e:
        logging.error(f"Erro ao calcular médias da turma: {str(e)}")
        return jsonify({"erro": "Ocorreu um erro ao calcular as médias da turma"}), 500

    finally:
        if cursor:
            cursor.close()
        if conectar:
            conectar.close()

@app.route('/api/alunos-acima-media', methods=['GET'])
def alunosAcimaMedia():
    try:
        conectar = conectarBd()
        if not conectar:
            return jsonify({"erro": "Não foi possível conectar ao banco de dados"}), 500

        cursor = conectar.cursor(cursor_factory=RealDictCursor)
        
        cursor.execute("""
            SELECT AVG((notaDisciplina01 + notaDisciplina02 + notaDisciplina03 + notaDisciplina04 + notaDisciplina05) / 5) as media_geral_turma
            FROM alunos
        """)
        media_geral_turma = cursor.fetchone()['media_geral_turma']

        cursor.execute("""
            SELECT 
                id, 
                nome, 
                (notaDisciplina01 + notaDisciplina02 + notaDisciplina03 + notaDisciplina04 + notaDisciplina05) / 5 as media_aluno
            FROM alunos
            WHERE (notaDisciplina01 + notaDisciplina02 + notaDisciplina03 + notaDisciplina04 + notaDisciplina05) / 5 > %s
            ORDER BY media_aluno DESC
        """, (media_geral_turma,))
        
        alunos_acima_media = cursor.fetchall()

        resultado = {
            "media_geral_turma": round(media_geral_turma, 2),
            "alunos": [{
                "id": aluno['id'],
                "nome": aluno['nome'],
                "media": round(aluno['media_aluno'], 2)
            } for aluno in alunos_acima_media]
        }

        return jsonify(resultado), 200

    except Exception as e:
        logging.error(f"Erro ao buscar alunos acima da média: {str(e)}")
        return jsonify({"erro": "Ocorreu um erro ao buscar os alunos acima da média"}), 500

    finally:
        if cursor:
            cursor.close()
        if conectar:
            conectar.close()

@app.route('/api/alunos-baixa-frequencia', methods=['GET'])
def alunosBaixaFrequencia():
    try:
        conectar = conectarBd()
        if not conectar:
            return jsonify({"erro": "Não foi possível conectar ao banco de dados"}), 500

        cursor = conectar.cursor(cursor_factory=RealDictCursor)
        
        cursor.execute("""
            SELECT 
                id, 
                nome, 
                frequencia
            FROM alunos
            WHERE frequencia < 75
            ORDER BY frequencia ASC
        """)
        
        alunos_baixa_frequencia = cursor.fetchall()

        resultado = [{
            "id": aluno['id'],
            "nome": aluno['nome'],
            "frequencia": aluno['frequencia']
        } for aluno in alunos_baixa_frequencia]

        return jsonify(resultado), 200

    except Exception as e:
        logging.error(f"Erro ao buscar alunos com baixa frequência: {str(e)}")
        return jsonify({"erro": "Ocorreu um erro ao buscar os alunos com baixa frequência"}), 500

    finally:
        if cursor:
            cursor.close()
        if conectar:
            conectar.close()

@app.route('/api/alunos/<int:aluno_id>', methods=['PUT'])
def atualizarAluno(aluno_id):
    try:
        conectar = conectarBd()
        if not conectar:
            logging.error("Falha na conexão com o banco de dados")
            return jsonify({"erro": "Não foi possível conectar ao banco de dados"}), 500

        cursor = conectar.cursor(cursor_factory=RealDictCursor)
        
        dados = request.json
        logging.info(f"Dados recebidos para atualização do aluno {aluno_id}: {dados}")

        dados_atualizacao = {
            'nome': dados['nome'],
            'frequencia': dados['frequencia'],
            'notaDisciplina01': dados['notas']['Disciplina 1'],
            'notaDisciplina02': dados['notas']['Disciplina 2'],
            'notaDisciplina03': dados['notas']['Disciplina 3'],
            'notaDisciplina04': dados['notas']['Disciplina 4'],
            'notaDisciplina05': dados['notas']['Disciplina 5']
        }

        campos = list(dados_atualizacao.keys())
        valores = list(dados_atualizacao.values())
        placeholders = [f"{campo} = %s" for campo in campos]
        query = f"UPDATE alunos SET {', '.join(placeholders)} WHERE id = %s RETURNING *"
        
        valores.append(aluno_id)

        logging.info(f"Executando query: {query}")
        logging.info(f"Valores: {valores}")

        cursor.execute(query, valores)
        aluno_atualizado = cursor.fetchone()
        
        if not aluno_atualizado:
            logging.warning(f"Aluno com ID {aluno_id} não encontrado")
            return jsonify({"mensagem": "Aluno não encontrado"}), 404

        aluno_formatado = {
            "id": aluno_atualizado['id'],
            "nome": aluno_atualizado['nome'],
            "notas": {
                "Disciplina 1": float(aluno_atualizado['notadisciplina01']),
                "Disciplina 2": float(aluno_atualizado['notadisciplina02']),
                "Disciplina 3": float(aluno_atualizado['notadisciplina03']),
                "Disciplina 4": float(aluno_atualizado['notadisciplina04']),
                "Disciplina 5": float(aluno_atualizado['notadisciplina05']),
            },
            "frequencia": float(aluno_atualizado['frequencia'])
        }

        conectar.commit()
        logging.info(f"Aluno com ID {aluno_id} atualizado com sucesso. Dados atualizados: {aluno_formatado}")
        return jsonify({
            "mensagem": f"Dados do aluno atualizados com sucesso",
            "aluno": aluno_formatado
        }), 200

    except Exception as e:
        conectar.rollback()
        logging.error(f"Erro ao atualizar aluno {aluno_id}: {str(e)}")
        logging.error(f"Traceback: {traceback.format_exc()}")
        return jsonify({"erro": f"Ocorreu um erro ao atualizar os dados do aluno: {str(e)}"}), 500

    finally:
        if cursor:
            cursor.close()
        if conectar:
            conectar.close()

@app.route('/api/alunos/<int:aluno_id>', methods=['DELETE'])
def deletarAluno(aluno_id):
    try:
        conectar = conectarBd()
        if not conectar:
            return jsonify({"erro": "Não foi possível conectar ao banco de dados"}), 500

        cursor = conectar.cursor()
        
        cursor.execute("DELETE FROM alunos WHERE id = %s", (aluno_id,))
        
        if cursor.rowcount == 0:
            return jsonify({"mensagem": "Aluno não encontrado"}), 404
        
        conectar.commit()
        return jsonify({"mensagem": f"Aluno com ID {aluno_id} deletado com sucesso"}), 200

    except Exception as e:
        conectar.rollback()
        logging.error(f"Erro ao deletar aluno: {str(e)}")
        return jsonify({"erro": "Ocorreu um erro ao deletar o aluno"}), 500

    finally:
        if cursor:
            cursor.close()
        if conectar:
            conectar.close()

if __name__ == '__main__':
    app.run(debug=True)
