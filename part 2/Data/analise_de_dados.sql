
-- progresso ortopedico
WITH progresso_ortopedico AS (
    SELECT 
        hp.ssn,
        p.nome AS nome_paciente,
        hp.chave,
        hp.data,
        LAG(hp.data) OVER (PARTITION BY hp.ssn, hp.chave ORDER BY hp.data) AS data_anterior
    FROM historial_paciente hp
    JOIN paciente p ON hp.ssn = p.ssn
    WHERE hp.tipo = 'observacao' 
        AND hp.especialidade = 'ortopedia' 
        AND hp.valor IS NULL
)

SELECT nome_paciente, ssn
FROM progresso_ortopedico
WHERE data - data_anterior = (SELECT MAX(data - data_anterior) FROM progresso_ortopedico);

--medicamentos cardiologia
SELECT 
    chave AS medicamento
FROM 
    historial_paciente
WHERE 
    especialidade = 'Cardiologia'
    AND data >= CURRENT_DATE - INTERVAL '1 year'
GROUP BY 
    medicamento, ssn
HAVING 
    COUNT(DISTINCT mes || '-' || ano) = 12
ORDER BY 
    medicamento;



--quantidades totais receitadas de cada medicamento em 2023
SELECT
    chave AS medicamento,
    SUM(valor) AS quantidade_total,
    localidade,
    hp.nome AS nome_clinica,
    mes,
    dia_do_mes,
    m.nome AS nome_medico,
    m.especialidade
FROM 
    historial_paciente hp
JOIN
    medico m USING(nif)
WHERE 
    tipo = 'receita' AND ano = 2023
GROUP BY GROUPING SETS(
    (chave),
    (chave, localidade),
    (chave, localidade, nome_clinica),
    (chave, mes),
    (chave, mes, dia_do_mes),
    (chave, m.especialidade),
    (chave, m.especialidade, nome_medico))
ORDER BY chave, localidade, nome_clinica, mes, dia_do_mes, m.especialidade, nome_medico;


--enviesamento na medição de algum parâmetros entre clínicas, especialidades médicas ou médicos
SELECT
    m.especialidade AS especialidade,
    m.nome AS nome_medico,
    c.nome AS nome_clinica,
    AVG(o.valor) AS media_valor,
    STDDEV(o.valor) AS desvio_padrao_valor
FROM 
    observacao o
JOIN 
    consulta c ON o.id = c.id
JOIN 
    medico m ON c.nif = m.nif
JOIN 
    clinica cl ON c.nome = cl.nome
WHERE 
    o.valor IS NOT NULL
GROUP BY GROUPING SETS(
    (),
    (m.especialidade),
    (m.especialidade, nome_medico),
    (nome_clinica),
    (m.especialidade, nome_medico, nome_clinica))
ORDER BY especialidade, nome_medico, nome_clinica;

