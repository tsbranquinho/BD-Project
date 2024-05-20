WITH progresso_ortopedico AS (
    SELECT 
        ssn,
        chave,
        data,
        LAG(data) OVER (PARTITION BY ssn, chave ORDER BY data) AS data_anterior
    FROM historial_paciente
    WHERE tipo = 'observacao' AND especialidade = 'ortopedia' AND valor IS NULL
)
SELECT ssn
FROM progresso_ortopedico
WHERE data - data_anterior = (SELECT MAX(data - data_anterior) FROM progresso_ortopedico);


SELECT DISTINCT chave AS medicamento
FROM historial_paciente
WHERE tipo = 'receita' AND especialidade = 'cardiologia'
GROUP BY ssn, chave
HAVING COUNT(DISTINCT EXTRACT(YEAR FROM data) * 12 + EXTRACT(MONTH FROM data)) >= 12;

SELECT
    chave AS medicamento,
    SUM(valor) AS quantidade_total,
    localidade,
    nome,
    EXTRACT(MONTH FROM data) AS mes,
    dia_do_mes,
    especialidade,
    nif AS nif_medico
FROM historial_paciente
WHERE tipo = 'receita' AND EXTRACT(YEAR FROM data) = 2023
GROUP BY chave, localidade, nome, EXTRACT(MONTH FROM data), dia_do_mes, especialidade, nif_medico;



SELECT
    COALESCE(hp.especialidade, 'Total') AS especialidade,
    COALESCE(m.nome, 'Total') AS nome_medico,
    COALESCE(hp.nome, 'Total') AS clinica,
    AVG(hp.valor) AS media_valor,
    STDDEV_POP(hp.valor) AS desvio_padrao_valor
FROM historial_paciente hp
JOIN medico m ON hp.nif = m.nif
WHERE hp.tipo = 'observacao' AND hp.valor IS NOT NULL
GROUP BY ROLLUP(m.nome, hp.especialidade, hp.nome);


