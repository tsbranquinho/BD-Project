#!/usr/bin/python3
import os
import logging
import psycopg

from logging.config import dictConfig

from flask import Flask, jsonify
from datetime import datetime, timedelta
from itertools import product

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

# Database URL
DATABASE_URL = "postgresql://saude:saude@localhost:5432/saude"
#nao faco ideia oq é suposto por no database url TODO


@app.route("/", methods=("GET",))
def list_all_clinics():
    """List all clinics (nome and morada)"""
    with psycopg.connect(conninfo=DATABASE_URL) as conn:
        with conn.cursor() as cur:
            clinics = cur.execute(
                """
                SELECT nome, morada
                FROM clinica;
                """
            ).fetchall()
            log.debug(f"Found {cur.rowcount} rows.")
    
    # Return the clinics data as JSON
    return jsonify(clinics)

@app.route("/c/<clinica>/", methods=("GET",))
def list_specialties(clinica):
    """List all specialties offered at a specific clinic"""
    with psycopg.connect(conninfo=DATABASE_URL) as conn:
        with conn.cursor() as cur:
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
    
    # Return the specialties data as JSON
    return jsonify(specialties)

@app.route("/c/<clinica>/<especialidade>/", methods=["GET"])
def list_doctors_and_consultation_times(clinica, especialidade):

    # Definir a data inicial como a data atual
    start_date = datetime.now()
    end_date = datetime(2024, 12, 31)
    
    # Criar a tabela de horários disponíveis para consulta
    create_consultation_schedule(start_date, end_date)
    
    with psycopg.connect(conninfo=DATABASE_URL) as conn:
        with conn.cursor() as cur:
            # Consulta para listar os médicos e os primeiros três horários disponíveis para consulta de cada um
            cur.execute(
                """
                SELECT nome_medico, date, hora_consulta
                FROM (
                    SELECT nome_medico, date, hora_consulta,
                        ROW_NUMBER() OVER (PARTITION BY nome_medico, date, hora_consulta ORDER BY date, hora_consulta) AS row_num
                    FROM (
                        SELECT m.nome AS nome_medico, c.date, unnest(c.consultation_times) AS hora_consulta
                        FROM medico m
                        JOIN trabalha t ON m.nif = t.nif
                        JOIN (
                            SELECT date, consultation_times
                            FROM consultation_schedule
                            WHERE date BETWEEN %s AND %s
                        ) c ON true
                        LEFT JOIN consulta con ON m.nif = con.nif AND c.date = con.data AND to_char(con.hora, 'HH24:MI:SS') = ANY(c.consultation_times)
                        WHERE t.nome = %s AND m.especialidade = %s AND con.id IS NULL
                    ) AS subquery
                ) AS subquery_with_row_numbers
                WHERE row_num <= 3;
                """,
                (start_date, end_date, clinica, especialidade)
            )
            rows = cur.fetchall()
    
    # Group consultation times by doctor
    doctor_consultation_times = {}
    for row in rows:
        doctor_name = row[0]
        consultation_data = {"data": row[1].strftime("%Y-%m-%d"), "hora_consulta": row[2]}
        if doctor_name in doctor_consultation_times:
            doctor_consultation_times[doctor_name].append(consultation_data)
        else:
            doctor_consultation_times[doctor_name] = [consultation_data]
    
    # Return the data grouped by doctor as JSON
    return jsonify(doctor_consultation_times)


# Função para gerar os horários de consulta para um dia específico
def generate_consultation_times(date):
    start_time_morning = datetime.combine(date, datetime.min.time()) + timedelta(hours=8)  # Início das consultas: 8h
    end_time_morning = datetime.combine(date, datetime.min.time()) + timedelta(hours=13)  # Fim das consultas: 13h
    start_time_afternoon = datetime.combine(date, datetime.min.time()) + timedelta(hours=14)  # Início das consultas: 14h
    end_time_afternoon = datetime.combine(date, datetime.min.time()) + timedelta(hours=19)  # Fim das consultas: 19h
    time_step = timedelta(minutes=30)  # Intervalo de consulta: 30 minutos
    
    # Gera todos os horários de consulta para o dia, a cada 30 minutos
    consultation_times = []
    current_time = start_time_morning
    while current_time < end_time_morning:
        consultation_times.append(current_time.time().strftime("%H:%M:00"))
        current_time += time_step

    current_time = start_time_afternoon
    while current_time < end_time_afternoon:
        consultation_times.append(current_time.time().strftime("%H:%M:00"))
        current_time += time_step
    
    return consultation_times

# Função para criar uma tabela de horários disponíveis para consulta
def create_consultation_schedule(start_date, end_date):
    # Lista de todos os dias entre start_date e end_date, inclusive
    all_dates = [start_date + timedelta(days=i) for i in range((end_date - start_date).days + 1)]
    
    with psycopg.connect(conninfo=DATABASE_URL) as conn:
        with conn.cursor() as cur:
            # Excluir a tabela se já existir
            cur.execute("DROP TABLE IF EXISTS consultation_schedule;")
            
            # Criar a tabela com os horários disponíveis para consulta
            cur.execute(
                """
                CREATE TABLE consultation_schedule (
                    date DATE PRIMARY KEY,
                    consultation_times TEXT[]
                );
                """
            )
            
            # Inserir os horários disponíveis para consulta para cada dia
            for date in all_dates:
                consultation_times = generate_consultation_times(date)
                cur.execute(
                    "INSERT INTO consultation_schedule (date, consultation_times) VALUES (%s, %s);",
                    (date, consultation_times)
                )
                
            # Confirmar a transação
            conn.commit()


if __name__ == "__main__":
    app.run()