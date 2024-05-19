DROP TABLE IF EXISTS clinica CASCADE;
DROP TABLE IF EXISTS enfermeiro CASCADE;
DROP TABLE IF EXISTS medico CASCADE;
DROP TABLE IF EXISTS trabalha CASCADE;
DROP TABLE IF EXISTS paciente CASCADE;
DROP TABLE IF EXISTS receita CASCADE;
DROP TABLE IF EXISTS consulta CASCADE;
DROP TABLE IF EXISTS observacao CASCADE;

CREATE TABLE clinica(
    nome VARCHAR(80) PRIMARY KEY,
    telefone VARCHAR(15) UNIQUE NOT NULL CHECK (telefone ~ '^[0-9]+$'),
    morada VARCHAR(255) UNIQUE NOT NULL
);

CREATE TABLE enfermeiro(
    nif CHAR(9) PRIMARY KEY CHECK (nif ~ '^[0-9]+$'),
    nome VARCHAR(80) UNIQUE NOT NULL,
    telefone VARCHAR(15) NOT NULL CHECK (telefone ~ '^[0-9]+$'),
    morada VARCHAR(255) NOT NULL,
    nome_clinica VARCHAR(80) NOT NULL REFERENCES clinica (nome)
);

CREATE TABLE medico(
    nif CHAR(9) PRIMARY KEY CHECK (nif ~ '^[0-9]+$'),
    nome VARCHAR(80) UNIQUE NOT NULL,
    telefone VARCHAR(15) NOT NULL CHECK (telefone ~ '^[0-9]+$'),
    morada VARCHAR(255) NOT NULL,
    especialidade VARCHAR(80) NOT NULL
);

CREATE TABLE trabalha(
    nif CHAR(9) NOT NULL REFERENCES medico,
    nome VARCHAR(80) NOT NULL REFERENCES clinica,
    dia_da_semana SMALLINT,
    PRIMARY KEY (nif, dia_da_semana)
);

CREATE TABLE paciente(
    ssn CHAR(11) PRIMARY KEY CHECK (ssn ~ '^[0-9]+$'),
    nif CHAR(9) UNIQUE NOT NULL CHECK (nif ~ '^[0-9]+$'),
    nome VARCHAR(80) NOT NULL,
    telefone VARCHAR(15) NOT NULL CHECK (telefone ~ '^[0-9]+$'),
    morada VARCHAR(255) NOT NULL,
    data_nasc DATE NOT NULL
);
