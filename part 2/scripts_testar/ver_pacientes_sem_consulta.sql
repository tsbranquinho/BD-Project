SELECT p.ssn, p.nome
FROM paciente p
LEFT JOIN consulta c ON p.ssn = c.ssn
WHERE c.id IS NULL;