-- RI 1
ALTER TABLE consulta
ADD CONSTRAINT check_hora
CHECK (
  EXTRACT(MINUTE FROM hora) IN (0, 30) AND 
  (
    (EXTRACT(HOUR FROM hora) BETWEEN 8 AND 12) OR 
    (EXTRACT(HOUR FROM hora) BETWEEN 14 AND 19)
  )
  OR RAISE EXCEPTION 'Os horários das consultas devem ser em horas exatas ou meia hora, entre 8h e 12h e entre 14h e 19h.'
);


--RI 2
CREATE OR REPLACE FUNCTION check_self_consult() RETURNS TRIGGER AS $$
BEGIN
  IF NEW.nif = (SELECT nif FROM paciente WHERE ssn = NEW.ssn) THEN
    RAISE EXCEPTION 'Um médico não pode marcar uma consulta consigo mesmo.';
  END IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER self_consult_trigger
BEFORE INSERT OR UPDATE ON consulta
FOR EACH ROW EXECUTE PROCEDURE check_self_consult();


--RI 3
CREATE OR REPLACE FUNCTION check_work_day() RETURNS TRIGGER AS $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 
    FROM trabalha 
    WHERE nif = NEW.nif AND nome = NEW.nome AND dia_da_semana = EXTRACT(DOW FROM NEW.data)
  ) THEN
    RAISE EXCEPTION 'Um doutor só pode dar consultas na clinica nos dias em que trabalha.'; --esta frase é um bocado confusa
  END IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER work_day_trigger
BEFORE INSERT OR UPDATE ON consulta
FOR EACH ROW EXECUTE PROCEDURE check_work_day();