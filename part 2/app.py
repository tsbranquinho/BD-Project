#!/usr/bin/python3
# Copyright (c) BDist Development Team
# Distributed under the terms of the Modified BSD License.
import os
from datetime import datetime, timedelta
from logging.config import dictConfig
from flask import Flask, jsonify, request
from psycopg.rows import namedtuple_row
from psycopg_pool import ConnectionPool
import random

DATABASE_URL = os.environ.get("DATABASE_URL", "postgres://saude:saude@postgres/saude")

pool = ConnectionPool(
    conninfo=DATABASE_URL,
    kwargs={
        "autocommit": False,  # Use transactions for Atomicity
        "row_factory": namedtuple_row,
    },
    min_size=4,
    max_size=10,
    open=True,
    name="postgres_pool",
    timeout=5,
)

dictConfig(
    {
        "version": 1,
        "formatters": {
            "default": {
                "format": "[%(asctime)s] %(levelname)s in %(module)s:%(lineno)s - %(funcName)20s(): %(message)s",
            }
        },
        "handlers": {
            "wsgi": {
                "class": "logging.StreamHandler",
                "stream": "ext://flask.logging.wsgi_errors_stream",
                "formatter": "default",
            }
        },
        "root": {"level": "INFO", "handlers": ["wsgi"]},
    }
)

app = Flask(__name__)
app.config.from_prefixed_env()
log = app.logger

TIME_SLOTS = ["09:00:00", "09:30:00", "10:00:00", "10:30:00","11:00:00","11:30:00","12:00:00",
                "12:30:00","14:30:00","15:00:00","15:30:00","16:00:00","16:30:00",
                    "17:00:00","17:30:00","18:00:00","18:30:00"]

@app.route("/", methods=("GET",))
def list_all_clinics():
    """List all clinics (nome and morada)"""
    
    with pool.connection() as conn:
        with conn.cursor() as cur:
            clinics = cur.execute(
                """
                SELECT nome, morada
                FROM clinica;
                """
            ).fetchall()
            log.debug(f"Found {cur.rowcount} rows.")
    
    if not clinics:
        return jsonify({"message": "Nenhuma clínica encontrada."}), 404
    
    return jsonify(clinics)

@app.route("/c/<clinica>/", methods=("GET",))
def list_specialties(clinica):
    """List all specialties offered at a specific clinic"""
    with pool.connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT nome FROM clinica WHERE nome = %s;
                """,
                (clinica,)  
            )
            if cur.rowcount == 0:
                return jsonify({"message": "Clinica não encontrada."}), 404

            specialties = cur.execute(
                """
                SELECT DISTINCT especialidade
                FROM medico
                WHERE nif IN (
                    SELECT nif
                    FROM trabalha
                    WHERE nome = %s
                );
                """,
                (clinica,)  
            ).fetchall()
            log.debug(f"Found {cur.rowcount} specialties for clinic {clinica}.")
    
    if not specialties:
        return jsonify({"message": "Nenhuma especialidade encontrada."}), 404
    
    return jsonify(specialties)

@app.route("/c/<clinica>/<especialidade>/", methods=["GET"])
def list_doctors_and_consultation_times(clinica, especialidade):
    current_date = datetime.now().date()

    with pool.connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT DISTINCT m.nome AS nome_medico, m.nif
                FROM medico m
                JOIN trabalha t ON m.nif = t.nif
                WHERE t.nome = %s AND m.especialidade = %s;
                """,
                (clinica, especialidade)
            )
            doctors = cur.fetchall()

            available_times = {}
            for doctor in doctors:
                doctor_name, nif_medico = doctor

                cur.execute(
                    """
                    SELECT data, hora
                    FROM consulta
                    WHERE nif = %s AND nome = %s AND data >= %s
                    ORDER BY data, hora;
                    """,
                    (nif_medico, clinica, current_date)
                )
                consultations = cur.fetchall()

                available_times[doctor_name] = []
                available_slots = TIME_SLOTS.copy()
                
                for cons in consultations:
                    for consulta in consultations:
                        if consulta[0] == cons[0]:
                            if consulta[1] in available_slots:
                                available_slots.remove(consulta[1])
                    
                    for slot in available_slots:
                        slot_time = datetime.strptime(slot, "%H:%M:%S").time() 
                        slot_date = cons[0]

                        if cons[1] != slot_time:
                            date = datetime.combine(slot_date, slot_time)
                            formatted_date = date.strftime("%d-%m-%Y %H:%M:%S")
                            available_times[doctor_name].append(formatted_date)

                        if len(available_times[doctor_name]) == 3:
                            break
                    
                    if len(available_times[doctor_name]) == 3:
                        break
                    
                    available_slots = TIME_SLOTS.copy()

                if not consultations or len(available_times[doctor_name]) == 0:
                    available_times[doctor_name] = "Não há horários disponíveis"

    return jsonify(available_times)


def generate_sns_code():
    return str(random.randint(100000000000, 999999999999))

def sns_code_exists(code, cur):
    cur.execute("SELECT COUNT(*) FROM consulta WHERE codigo_sns = %s;", (code,))  
    count = cur.fetchone()[0]
    return count > 0

@app.route("/a/<clinica>/registar/", methods=["POST"])
def registrar_consulta(clinica):
    data = request.json
    paciente = data.get("paciente")
    nome_medico = data.get("medico")
    data_hora = data.get("data_hora")

    if not (paciente and nome_medico and data_hora):
        return jsonify({"error": "Todos os campos (paciente, medico, data_hora) são necessários."}), 400

    try:
        data_hora = datetime.strptime(data_hora, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        return jsonify({"error": "Formato de data/hora inválido. Use 'YYYY-MM-DD HH:MM:SS'."}), 400

    if data_hora <= datetime.now():
        return jsonify({"error": "A data/hora deve ser posterior ao momento de agendamento."}), 400

    try:
        with pool.connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT nif
                    FROM medico
                    WHERE nome = %s;
                    """,
                    (nome_medico,)  
                )
                result = cur.fetchone()
                if not result:
                    return jsonify({"error": "Médico não encontrado."}), 404
                nif_medico = result.nif

        with pool.connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT MAX(id) FROM consulta;")
                last_id = cur.fetchone()[0] or 0
                next_id = last_id + 1

        with pool.connection() as conn:
            with conn.cursor() as cur:
                try:
                    sns_code = generate_sns_code()
                    while sns_code_exists(sns_code, cur):
                        sns_code = generate_sns_code()

                    cur.execute(
                        """
                        INSERT INTO consulta (id, ssn, nif, nome, data, hora, codigo_sns)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                        """,
                        (next_id, paciente, nif_medico, clinica, data_hora.date(), data_hora.time(), sns_code)  
                    )
                    conn.commit() 
                    return jsonify({"success": "Consulta agendada com sucesso."}), 201
                except Exception as e:
                    conn.rollback()  
                    return jsonify({"error": "Consulta já existe"}), 500
    except Exception as e:
        return jsonify({"error": "Erro ao processar requisição."}), 500

@app.route("/a/<clinica>/cancelar/", methods=["DELETE"])
def cancelar_consulta(clinica):
    data = request.json
    paciente = data.get("paciente")
    data_hora = data.get("data_hora")
   
    if not (paciente and data_hora):
        return jsonify({"error": "Os campos 'paciente' e 'data_hora' são necessários."}), 400

    try:
        data_hora = datetime.strptime(data_hora, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        return jsonify({"error": "Formato de data/hora inválido. Use 'YYYY-MM-DD HH:MM:SS'."}), 400

    if data_hora <= datetime.now():
        return jsonify({"error": "A data/hora da consulta deve ser posterior ao momento atual."}), 400

    try:
        with pool.connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    DELETE FROM consulta 
                    WHERE ssn = %s 
                    AND nome = %s 
                    AND data = %s 
                    AND hora = %s;
                    """,
                    (paciente, clinica, data_hora.date(), data_hora.time())  
                )
                
                if cur.rowcount > 0:
                    conn.commit()  
                    return jsonify({"success": "Consulta cancelada com sucesso."}), 200
                else:
                    conn.rollback()  
                    return jsonify({"error": "Nenhuma consulta encontrada."}), 404
    except Exception as e:
        return jsonify({"error": "Ocorreu um erro ao cancelar a consulta."}), 500

if __name__ == "__main__":
    app.run()
