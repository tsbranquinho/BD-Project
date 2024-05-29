-- RI 1
CREATE OR REPLACE FUNCTION check_consulta_hora() RETURNS TRIGGER AS $$
BEGIN
  IF NOT (
    EXTRACT(MINUTE FROM NEW.hora) IN (0, 30) AND 
    (
      (EXTRACT(HOUR FROM NEW.hora) BETWEEN 8 AND 13) OR 
      (EXTRACT(HOUR FROM NEW.hora) BETWEEN 14 AND 19)
    )
  ) THEN
    RAISE EXCEPTION 'Os horários das consultas devem ser em horas exatas ou meia hora, entre 8h e 12h e entre 14h e 19h.';
  END IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER check_consulta_hora_trigger
BEFORE INSERT OR UPDATE ON consulta
FOR EACH ROW EXECUTE FUNCTION check_consulta_hora();


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
DECLARE
    dia_da_semana_2 INTEGER;
    data_consulta DATE;
    nif_medico VARCHAR(80);
BEGIN
    -- Extract the day of the week from the date of the new consultation
    dia_da_semana_2 := EXTRACT(DOW FROM NEW.data);
    data_consulta := NEW.data;
    nif_medico := NEW.nif;

    
    -- Check if the doctor is scheduled to work on the extracted day of the week
    IF NOT EXISTS (
        SELECT 1 
        FROM trabalha 
        WHERE nif = NEW.nif AND nome = NEW.nome AND dia_da_semana = dia_da_semana_2
    ) THEN
        -- If not scheduled to work, raise an exception
        RAISE NOTICE 'Data da consulta: %', data_consulta;
        RAISE NOTICE 'Dia da semana: %', dia_da_semana_2;
        RAISE NOTICE 'NIF do medico: %', nif_medico;
        RAISE EXCEPTION 'Um medico só pode dar consultas na clinica nos dias em que trabalha.';
    END IF; 

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER work_day_trigger
BEFORE INSERT OR UPDATE ON consulta
FOR EACH ROW EXECUTE PROCEDURE check_work_day();