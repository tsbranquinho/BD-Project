SELECT cl.nome, COUNT(c.id) AS num_consultas, c.data
FROM clinica cl
LEFT JOIN consulta c ON cl.nome = c.nome
GROUP BY cl.nome, c.data
HAVING COUNT(c.id) < 20;