--indice 1
DROP INDEX IF EXISTS para_val_x;
CREATE INDEX para_val_x ON observacao(parametro, valor);


--indice 2
DROP INDEX IF EXISTS data_x;
DROP INDEX IF EXISTS esp_x;

CREATE INDEX data_x ON consulta(data);
CREATE INDEX esp_x ON medico(especialidade);