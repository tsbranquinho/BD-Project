SELECT m.nif, m.nome, COUNT(c.id) AS num_consultas, c.data
FROM medico m
LEFT JOIN consulta c ON m.nif = c.nif
GROUP BY m.nif, m.nome, c.data
HAVING COUNT(c.id) < 2;