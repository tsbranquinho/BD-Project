SELECT cl.nome, COUNT(DISTINCT t.nif) AS num_medicos
FROM clinica cl
LEFT JOIN trabalha t ON cl.nome = t.nome
GROUP BY cl.nome
HAVING COUNT(DISTINCT t.nif) < 8;