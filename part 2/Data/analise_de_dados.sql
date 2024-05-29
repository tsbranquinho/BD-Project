
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
SELECT ssn, nome_paciente
FROM progresso_ortopedico
WHERE data - data_anterior = (SELECT MAX(data - data_anterior) FROM progresso_ortopedico);

--medicamentos cardiologia
SELECT
    r.medicamento AS medicamento,
    COUNT(DISTINCT EXTRACT(MONTH FROM c.data) || '-' || EXTRACT(YEAR FROM c.data)) AS months_prescribed
FROM 
    receita r
JOIN 
    consulta c ON r.codigo_sns = c.codigo_sns
JOIN 
    medico m ON c.nif = m.nif
WHERE 
    m.especialidade = 'Cardiologia'
GROUP BY 
    r.medicamento
HAVING 
    COUNT(DISTINCT EXTRACT(MONTH FROM c.data) || '-' || EXTRACT(YEAR FROM c.data)) >= 12;



--quantidades totais receitadas de cada medicamento em 2023
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


--enviesamento na medição de algum parâmetros entre clínicas, especialidades médicas ou médicos
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


--uma versao diferente nenhuma delas esta bem uma juncao das duas estará bem
SELECT
    COALESCE(especialidade, 'Todas as Especialidades') AS especialidade,
    COALESCE(nome_médico, 'Todos os Médicos') AS nome_médico,
    COALESCE(nome_clinica, 'Todas as Clínicas') AS nome_clinica,
    o.parametro AS parametro,
    AVG(o.valor) AS valor_médio,
    STDDEV(o.valor) AS desvio_padrão
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
GROUP BY 
    CUBE(especialidade, nome_médico, nome_clinica),
    o.parametro
ORDER BY 
    especialidade, nome_médico, nome_clinica, parametro;


