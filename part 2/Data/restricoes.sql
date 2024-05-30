-- RI 1
ALTER TABLE consulta
ADD CONSTRAINT check_hora_consulta
CHECK (
    (EXTRACT(HOUR FROM hora) BETWEEN 8 AND 12 OR EXTRACT(HOUR FROM hora) BETWEEN 14 AND 18) 
    AND (EXTRACT(MINUTE FROM hora) IN (0, 30)));


--RI 2
DROP TRIGGER IF EXISTS self_consult_trigger ON consulta;

CREATE OR REPLACE FUNCTION check_medico_paciente() RETURNS TRIGGER AS 
$$
BEGIN
  IF NEW.nif = (SELECT nif FROM paciente WHERE ssn = NEW.ssn) THEN
    RAISE EXCEPTION 'Um médico não pode marcar uma consulta consigo mesmo.';
  END IF;
  RETURN NEW;
END;
$$ 
LANGUAGE plpgsql;

CREATE TRIGGER self_consult_trigger
BEFORE INSERT OR UPDATE ON consulta
FOR EACH ROW EXECUTE PROCEDURE check_medico_paciente();


--RI 3
DROP TRIGGER IF EXISTS dia_trabalho_trigger ON consulta;

CREATE OR REPLACE FUNCTION check_dia_trabalho() RETURNS TRIGGER AS 
$$
BEGIN
  IF NOT EXISTS (
    SELECT 1 
    FROM trabalha 
    WHERE nif = NEW.nif AND nome = NEW.nome AND dia_da_semana = EXTRACT(DOW FROM NEW.data)
  ) THEN
    RAISE EXCEPTION 'Um medico só pode dar consultas na clinica nos dias em que trabalha.';
  END IF; 
  RETURN NEW;
END;
$$ 
LANGUAGE plpgsql;

CREATE TRIGGER dia_trabalho_trigger
BEFORE INSERT OR UPDATE ON consulta
FOR EACH ROW EXECUTE PROCEDURE check_dia_trabalho();