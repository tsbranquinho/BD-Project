import random
import copy
import re

nifs_usados = []
nomes_usados = []
ssn_usados = []
dias_meses = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
dias_meses_2024 = [31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
primeiro_dia_semana_ano = [6, 0]
codigo_sns_usados = []
ruas = []

def dia_semana(data):
    # Separando a data em ano, mês e dia
    ano, mes, dia = map(int, data.split("-"))

    # Ajuste para janeiro e fevereiro
    if mes < 3:
        mes += 12
        ano -= 1

    # Algoritmo de Zeller para calcular o dia da semana
    K = ano % 100
    J = ano // 100
    dia_semana = (dia + 13*(mes+1)//5 + K + K//4 + J//4 - 2*J) % 7

    # Ajustando o resultado para considerar domingo como 0
    dia_semana = (dia_semana + 6) % 7
    
    return dia_semana

class Morada:
    def __init__(self, codigo, localidade):
        self.codigo = codigo
        self.localidade = localidade
        self.rua = random.choice(ruas)
        self.codigo_postal = codigo + "-" + str(random.randint(0, 999)).zfill(3)

    def print(self):
        return self.rua + ", " + self.codigo_postal + " " + self.localidade


class Clinica:
    def __init__(self, nome, telefone, localidade, codigo):
        self.nome = nome
        self.telefone = telefone
        self.enfermeiros = []
        self.medicos = [[] for _ in range(7)]
        self.morada = Morada(codigo, localidade)
        self.num_medicos = [0 for _ in range(7)]

    def add_enfermeiro(self, enfermeiro):
        self.enfermeiros.append(enfermeiro)

    def print(self):
        print("Nome: ", self.nome)
        print("Telefone: ", self.telefone)
        print("Morada: ", self.morada.print())

    def print_agenda_medicos(self, medicos):
        for dia in range(7):
            print("Dia", dia)
            for medico in self.medicos.keys():
                for aux in medicos:
                    if aux.nif == medico and aux.disponibilidade[dia] == 1 and dia in self.medicos[medico]:
                        print(aux.nome)
            print()

    def cria_registo(self):
        registo = {}
        for mes in range(12):
            for dia in range(dias_meses[mes]):
                registo[str(2023) + "-" + str(mes+1).zfill(2) + "-" + str(dia+1).zfill(2)] = 0
        for mes in range(12):
            for dia in range(dias_meses_2024[mes]):
                registo[str(2024) + "-" + str(mes+1).zfill(2) + "-" + str(dia+1).zfill(2)] = 0
        self.registo = registo

class Enfermeiro:
    def __init__(self, nome, nif, telefone, localidade, codigo, nome_clinica):
        self.nome = nome
        self.nif = nif
        self.telefone = telefone
        self.morada = Morada(codigo, localidade)
        self.nome_clinica = nome_clinica

    def print(self):
        print("Nome: ", self.nome)
        print("NIF: ", self.nif)
        print("Telefone: ", self.telefone)
        print("Morada: ", self.morada.print())
        print("Clinica: ", self.nome_clinica)

class Medico:
    def __init__(self, nome, nif, telefone, localidade, codigo, especialidade):
        self.nome = nome
        self.nif = nif
        self.telefone = telefone
        self.morada = Morada(codigo, localidade)
        self.especialidade = especialidade
        self.disponibilidade = [0 for _ in range(7)]
        self.num_clinicas = 0
        self.dias_trabalho = 0
        self.trabalho = {}
    
    def trabalha_na_clinica(self, clinica, dia_semana):
        if self.disponibilidade[dia_semana] == 1:
            return False
        clinica.medicos[dia_semana].append(self.nif)
        if clinica.nome in self.trabalho:
            self.trabalho[clinica.nome].append(dia_semana)
        else:
            self.trabalho[clinica.nome] = [dia_semana]
        self.disponibilidade[dia_semana] = 1
        self.dias_trabalho += 1

    def criar_registo(self):
        registos = {}
        consultas_diarias = {}
        for mes in range(12):
            for dia in range(dias_meses[mes]):
                data = str(2023) + "-" + str(mes+1).zfill(2) + "-" + str(dia+1).zfill(2)
                dia_week = dia_semana(data)
                if self.disponibilidade[dia_week] == 0:
                    continue
                dias = {}
                for hora in range(8,13):
                    for tempo in range(0, 60, 30):
                        horas = str(hora).zfill(2) + ":" + str(tempo).zfill(2) + ":00"
                        dias[horas] = None
                for hora in range(14, 19):
                    for tempo in range(0, 60, 30):
                        horas = str(hora).zfill(2) + ":" + str(tempo).zfill(2) + ":00"
                        dias[horas] = None
                registos[data] = dias
                consultas_diarias[data] = 0

        for mes in range(12):
            for dia in range(dias_meses_2024[mes]):
                data = str(2024) + "-" + str(mes+1).zfill(2) + "-" + str(dia+1).zfill(2)
                dia_week = dia_semana(data)
                if self.disponibilidade[dia_week] == 0:
                    continue
                dias = {}
                for hora in range(8,13):
                    for tempo in range(0, 60, 30):
                        horas = str(hora).zfill(2) + ":" + str(tempo).zfill(2) + ":00"
                        dias[horas] = None
                for hora in range(14, 19):
                    for tempo in range(0, 60, 30):
                        horas = str(hora).zfill(2) + ":" + str(tempo).zfill(2) + ":00"
                        dias[horas] = None
                registos[data] = dias
                consultas_diarias[data] = 0
        self.registos = registos
        self.consultas_diarias = consultas_diarias
    
    def print(self):
        print("Nome: ", self.nome)
        print("NIF: ", self.nif)
        print("Telefone: ", self.telefone)
        print("Morada: ", self.morada.print())
        print("Especialidade: ", self.especialidade)
        print("Dias de trabalho: ", self.dias_trabalho)
        for clinica in self.trabalho.keys():
            print("Clinica: ", clinica)
            print("Dias de trabalho: ", self.trabalho[clinica])

class Paciente:
    def __init__(self, nome, nif, ssn, telefone, codigo, localidade, data_nascimento):
        self.nome = nome
        self.nif = nif
        self.ssn = ssn
        self.telefone = telefone
        self.morada = Morada(codigo, localidade)
        self.data_nascimento = data_nascimento
        self.registo = {}

    def print(self):
        print("Nome: ", self.nome)
        print("NIF: ", self.nif)
        print("SSN: ", self.ssn)
        print("Telefone: ", self.telefone)
        print("Morada: ", self.morada.print())
        print("Data de nascimento: ", self.data_nascimento)

class Consulta:
    def __init__(self, id, ssn_paciente, nif_medico, nome_clinica, data, hora, codigo_sns):
        self.id = id
        self.ssn_paciente = ssn_paciente
        self.nif_medico = nif_medico
        self.nome_clinica = nome_clinica
        self.data = data
        self.hora = hora
        self.codigo_sns = codigo_sns
        self.receita = []
        self.sintomas = []

    def add_receita(self, receita):
        self.receita.append(receita)

    def regista_sintomas(self, sintomas):
        self.sintomas.append(sintomas)

class Receita:
    def __init__(self, codigo_sns, medicamento, quantidade):
        self.codigo_sns = codigo_sns
        self.medicamento = medicamento
        self.quantidade = quantidade

class Sintomas:
    def __init__(self, id_consulta):
        self.id_consulta = id_consulta
        
    def add_parametro(self, parametro):
        self.parametro = parametro
    
    def add_valor(self, valor):
        self.valor = valor

class Popula:
    def __init__(self, database):
        self.database = database
        self.populate()

    def populate(self):
        self.cria_clinicas()
        self.cria_enfermeiros()
        self.cria_medicos()
        self.coloca_medicos_nas_clinicas()
        self.cria_pacientes()
        self.cria_consultas()
        self.cria_registo_consulta()

    def cria_clinicas(self):
        self.localidades = ["Lisboa", "Amadora", "Sintra", "Oeiras", "Cascais", "Loures", "Odivelas", "Torres Vedras", "Vila Franca de Xira", "Mafra"]
        localidades_usadas = []
        self.codigos = ["1050", "2610", "2710", "2780", "2750", "2670", "2620", "2560", "2600", "2601", "2640"]
        nomes = ["Clínica Pública", "Clínica Privada", "Clínica Feliz", "Clínica do Povo", "Clínica Luís de Camões", "Clínica Especializada", "Clínica Velha", "Clínica Nova", "Clínica do Mar", "Clínica do Campo"]
        for _ in range(5):
            nome = random.choice(nomes)
            if len(localidades_usadas) < 3:
                while (num_localidade := random.randint(0, len(self.localidades) - 1)) in localidades_usadas:
                    continue
            else:
                num_localidade = random.randint(0, len(self.localidades) - 1)
            localidade = self.localidades[num_localidade]
            codigo = self.codigos[num_localidade]
            nome += " de " + localidade
            telefone = "2"
            for _ in range(8):
                telefone += str(random.randint(0, 9))
            clinica = Clinica(nome, telefone, localidade, codigo)
            self.database["clinicas"].append(clinica)
            localidades_usadas.append(num_localidade)
        self.check_clinicas()
        print("Clinicas criadas")

    def check_clinicas(self):
        for i in range(len(self.database["clinicas"])):
            for j in range(i + 1, len(self.database["clinicas"])):
                if self.database["clinicas"][i].nome == self.database["clinicas"][j].nome:
                    self.database["clinicas"][j].nome += random.choice([" A", " B", " C", " D", " E", " F", " G", " H", " I", " J", " K", " L", " M", " N", " O", " P", " Q", " R", " S", " T", " U", " V", " W", " X", " Y", " Z"])
                    self.check_clinicas()
                if self.database["clinicas"][i].morada.codigo_postal == self.database["clinicas"][j].morada.codigo_postal:
                    self.database["clinicas"][j].morada.codigo_postal = self.database["clinicas"][j].morada.codigo + "-" + str(random.randint(0, 999)).zfill(3)
                    self.check_clinicas()
                if self.database["clinicas"][i].telefone == self.database["clinicas"][j].telefone:
                    self.database["clinicas"][j].telefone = "2"
                    for _ in range(8):
                        self.database["clinicas"][j].telefone += str(random.randint(0, 9))
                    self.check_clinicas()
        
    def cria_enfermeiros(self):
        self.nomes_proprios = [line.strip() for line in open("nomes_proprios.txt", "r").readlines()]
        self.sobrenomes = []
        for line in open("sobrenomes.txt", "r").readlines():
            line = line.strip()
            result = re.split(r'[ \t]+', line)
            self.sobrenomes.append(result[0])
        for clinica in self.database["clinicas"]:
            for _ in range(random.randint(5,6)):
                nome = self.cria_nome()
                nif = self.cria_nif()
                telefone = self.cria_telefone()
                num_localidade = random.randint(0, len(self.localidades) - 1)
                enfermeiro = Enfermeiro(nome , nif, telefone, self.localidades[num_localidade], self.codigos[num_localidade], clinica.nome)
                clinica.add_enfermeiro(enfermeiro)
                self.database["enfermeiros"].append(enfermeiro)
        print("Enfermeiros criados")
        
    def cria_medicos(self):
        #vamos criar também a versao paciente deles
        for _ in range(20):
            nome = self.cria_nome()
            nif = self.cria_nif()
            telefone = self.cria_telefone()
            num_localidade = random.randint(0, len(self.localidades) - 1)
            especialidade = "clínica geral"
            medico = Medico(nome, nif, telefone, self.localidades[num_localidade], self.codigos[num_localidade], especialidade)
            self.database["medicos"].append(medico)
        for _ in range(40):
            nome = self.cria_nome()
            nif = self.cria_nif()
            telefone = self.cria_telefone()
            num_localidade = random.randint(0, len(self.localidades) - 1)
            especialidade = random.choice(["pediatria", "ortopedia", "cardiologia", "urologia", "neurologia"])
            medico = Medico(nome, nif, telefone, self.localidades[num_localidade], self.codigos[num_localidade], especialidade)
            self.database["medicos"].append(medico)
        print("Medicos criados")
    
    def coloca_medicos_nas_clinicas(self):

        for clinica in self.database["clinicas"]:
            for dia_semana in range(7):
                while clinica.num_medicos[dia_semana] < 8:
                    medico = random.choice(self.database["medicos"])
                    if medico.disponibilidade[dia_semana] == 0:
                        medico.trabalha_na_clinica(clinica, dia_semana)
                        clinica.num_medicos[dia_semana] += 1
                        medico.num_clinicas += 1

        for medico in self.database["medicos"]:
            last_clinica = None
            while medico.num_clinicas < 2:
                clinica = random.choice(self.database["clinicas"])
                if clinica == last_clinica:
                    continue
                last_clinica = clinica
                while medico.disponibilidade[(dia:=random.randint(0, 6))] == 1:
                    continue
                if medico.nif not in clinica.medicos[dia]:
                    medico.trabalha_na_clinica(clinica, dia)
                    clinica.num_medicos[dia] += 1
                    medico.num_clinicas += 1
            for dia in range(7):
                if medico.disponibilidade[dia] == 1:
                    continue
                while medico.nif in (clinica := random.choice(self.database["clinicas"])).medicos[dia]:
                    continue
                medico.trabalha_na_clinica(clinica, dia)
                clinica.num_medicos[dia] += 1
                medico.num_clinicas += 1
        print("Medicos colocados nas clinicas")

                
    def cria_pacientes(self):
        novas_localidades = ["Setúbal", "Almada", "Barreiro", "Montijo", "Palmela", "Seixal", "Sesimbra", "Santiago do Cacém", "Sines", "Grândola", "Alcácer do Sal", "Carregado", "Proença-a-Nova", "Fátima", "Tábua", "Santa Comba Dão", "Mangualde", "Viseu", "Coimbra", "Porto"]
        novos_codigos = ["2900", "2800", "2830", "2870", "2950", "2840", "2970", "7540", "7520", "7570", "7580", "2580", "6150", "2495", "3420", "3440", "3530", "3500", "3000", "4100"]
        for localidade in novas_localidades:
            self.localidades.append(localidade)
        for codigo in novos_codigos:
            self.codigos.append(codigo)
        for _ in range(5000):
            nome = self.cria_nome()
            nif = self.cria_nif()
            ssn = self.cria_ssn()
            telefone = self.cria_telefone()
            num_localidade = random.randint(0, len(self.localidades) - 1)
            data_nascimento = str(random.randint(1924, 2020)) + "-" + (mes := str(random.randint(1, 12)).zfill(2)) + "-" + str(random.randint(1,dias_meses[int(mes)-1])).zfill(2) 
            paciente = Paciente(nome, nif, ssn, telefone, self.codigos[num_localidade], self.localidades[num_localidade], data_nascimento)
            self.database["pacientes"].append(paciente)

    def cria_consultas(self):
        print("A criar consultas")
        clinicas_dict = {clinica.nome: clinica for clinica in self.database["clinicas"]}
        medicos_dict = {medico.nif: medico for medico in self.database["medicos"]}
        for clinica in self.database["clinicas"]:
            clinica.cria_registo()
        for medico in self.database["medicos"]:
            medico.criar_registo()
        for paciente in self.database["pacientes"]:
            #garantir 1 consulta por paciente
            medico = random.choice(self.database["medicos"])
            nome_clinica = random.choice(list(medico.trabalho.keys()))
            dias_possiveis = medico.trabalho[nome_clinica]
            while (dia_semana(data:=random.choice(list(medico.registos.keys())))) not in dias_possiveis:
                continue
            while medico.registos[data][(hora := random.choice(list(medico.registos[data].keys())))] != None:
                continue
            ssn = paciente.ssn
            nif = medico.nif
            codigo_sns = self.cria_codigo_sns()
            consulta = Consulta(0, ssn, nif, nome_clinica, data, hora, codigo_sns)
            medico.registos[data][hora] = consulta	
            clinica.registo[data] += 1
            medico.consultas_diarias[data] += 1
            paciente.registo[data] = consulta
            self.database["consultas"].append(consulta)
        for ano in range(2023, 2025):
            if ano == 2023:
                to_use = dias_meses
            else:
                to_use = dias_meses_2024
            for mes in range(12):
                for dia in range(to_use[mes]):
                    #garantir 20 consultas por clinica por dia e 2 consultas por medico por dia
                    data = str(ano) + "-" + str(mes+1).zfill(2) + "-" + str(dia+1).zfill(2)
                    dia_week = dia_semana(data)
                    for clinica in self.database["clinicas"]:
                        #20 por dia
                        medicos_on_call = []
                        for medico_nif in clinica.medicos[dia_week]:
                            #médicos a trabalhar nesse dia
                            medico = medicos_dict[medico_nif]
                            medicos_on_call.append(medico)
                        while clinica.registo[data] < 20:
                            #enquanto não houver 20 consultas
                            medico = random.choice(medicos_on_call)
                            hora = None
                            if medico.consultas_diarias[data] == 18:
                                #já não tem vagas nesse dia
                                medicos_on_call.remove(medico)
                                continue
                            for _ in range(30):
                                #30 tentativas de encontrar uma hora livre
                                horas = random.choice(list(medico.registos[data].keys()))
                                if medico.registos[data][horas] == None:
                                    hora = horas
                                    break
                            if hora == None:
                                #não encontrou hora livre por sorte, logo bruteforce
                                for horas in medico.registos[data].keys():
                                    if medico.registos[data][horas] == None:
                                        hora = horas
                                        break
                                if hora == None:
                                    #não há vagas nesse dia
                                    medicos_on_call.remove(medico)
                                    continue
                            while True:
                                paciente = random.choice(self.database["pacientes"])
                                if data not in paciente.registo.keys():
                                    #paciente sem consulta nesse dia (fiz uma consulta por paciente por dia)
                                    break
                            ssn = paciente.ssn
                            nif = medico.nif
                            codigo_sns = self.cria_codigo_sns()
                            consulta = Consulta(0, ssn, nif, clinica.nome, data, hora, codigo_sns)
                            medico.registos[data][hora] = consulta
                            clinica.registo[data] += 1
                            medico.consultas_diarias[data] += 1
                            paciente.registo[data] = consulta
                            self.database["consultas"].append(consulta)
                    for medico in self.database["medicos"]:
                        #2 por dia
                        if medico.disponibilidade[(dia_week := dia_semana(data))] == 0 or medico.consultas_diarias[data] >= 2:
                            #não trabalha nesse dia ou já tem 2 consultas
                            continue
                        while medico.consultas_diarias[data] < 2:
                            #enquanto não tiver 2 consultas
                            hora = None
                            for _ in range(20):
                                horas = random.choice(list(medico.registos[data].keys()))
                                if medico.registos[data][horas] == None:
                                    hora = horas
                                    break
                            if hora == None:
                                for horas in medico.registos[data].keys():
                                    if medico.registos[data][horas] == None:
                                        hora = horas
                                        break
                                if hora == None:
                                    #não há vagas nesse dia
                                    break
                                break
                            nome_clinica = next((nc for nc in medico.trabalho if dia_week in medico.trabalho[nc]), None)
                            clinica = clinicas_dict[nome_clinica]
                            while True:
                                paciente = random.choice(self.database["pacientes"])
                                if data not in paciente.registo.keys():
                                    #paciente sem consulta nesse dia (fiz uma consulta por paciente por dia)
                                    break
                            ssn = paciente.ssn
                            nif = medico.nif
                            codigo_sns = self.cria_codigo_sns()
                            consulta = Consulta(0, ssn, nif, clinica.nome, data, hora, codigo_sns)
                            medico.registos[data][hora] = consulta
                            clinica.registo[data] += 1
                            medico.consultas_diarias[data] += 1
                            paciente.registo[data] = consulta
                            self.database["consultas"].append(consulta)
                print("Mes {} de {}".format(mes+1, ano))
        print("Consultas criadas")
        self.ordena_consultas()                


    def ordena_consultas(self):
        #ordena consultas por data, hora
        self.database["consultas"].sort(key=lambda x: (x.data, x.hora))
        print("Consultas ordenadas")
        #atribui id a cada consulta
        id = 1
        for consulta in self.database["consultas"]:
            consulta.id = id
            id += 1

    def testa_consultas(self):
        for consulta in self.database["consultas"]:
            nif = consulta.nif_medico
            medico = self.encontra_medico(nif)
            nome_clinica = consulta.nome_clinica
            for clinica in self.database["clinicas"]:
                if clinica.nome == nome_clinica:
                    break
            try:
                if dia_semana(consulta.data) not in medico.trabalho[nome_clinica]:
                    print("Medico", medico.nome, "não trabalha na clinica", nome_clinica, "no dia", consulta.data)
            except:
                print("Medico", medico.nome, "não trabalha na clinica", nome_clinica, "no dia", consulta.data)
        

    def cria_registo_consulta(self):
        file = open("medicamentos.txt", "r").readlines()
        file2 = open("sintomas_sem_valor.txt").readlines()
        file3 = open("sintomas_com_valor.txt").readlines()
        medicamentos_totais = []
        sintomas_sem_valor = []
        sintomas_com_valor = []
        counter = 0
        for line in file:
            medicamentos_totais.append(line.strip())
        for line in file2:
            sintomas_sem_valor.append(line.strip())
        for line in file3:
            line = line.strip()
            result = line.split(", ")
            sintoma = result[0]
            valor_min = float(result[1])
            valor_max = float(result[2])
            sintomas_com_valor.append((sintoma, valor_min, valor_max))
        for consulta in self.database["consultas"]:
            if consulta.data == "2024-06-01":
                print("Final das receitas")
                break
            if counter == 4:
                num_medicamentos = 0
                counter = 0
            else:
                num_medicamentos = random.randint(1, 6)
                medicamentos = []
                counter += 1
            sintomas_s_v = []
            sintomas_c_v = []
            medicamentos = []
            for _ in range(num_medicamentos):
                while (medicamento:=random.choice(medicamentos_totais)) in medicamentos:
                    continue
                quantidade = random.randint(1, 3)
                receita = Receita(consulta.codigo_sns, medicamento, quantidade)
                consulta.add_receita(receita)
                medicamentos.append(medicamento)
            num_sintomas_sem_valor = random.randint(1, 5)
            num_sintomas_com_valor = random.randint(0, 3)
            for _ in range(num_sintomas_sem_valor):
                while (sintoma:=random.choice(sintomas_sem_valor)) in sintomas_s_v:
                    continue
                sintomas = Sintomas(consulta.id)
                sintomas.add_parametro(sintoma)
                consulta.regista_sintomas(sintomas)
                sintomas_s_v.append(sintoma)
            for _ in range(num_sintomas_com_valor):
                while (sintoma:=random.choice(sintomas_com_valor)) in sintomas_c_v:
                    continue
                valor = random.uniform(sintoma[1], sintoma[2])
                sintomas = Sintomas(consulta.id)
                sintomas.add_parametro(sintoma[0])
                sintomas.add_valor(valor)
                consulta.regista_sintomas(sintomas)
                sintomas_c_v.append(sintoma)
        print("Registo de consultas criado")


    def testa_medicos_clinicas(self):
        for medico in self.database["medicos"]:
            if medico.num_clinicas < 2:
                print("Medico", medico.nome, "não trabalha em duas clinicas")
        for clinica in self.database["clinicas"]:
            for dia_semana in range(7):
                if clinica.num_medicos[dia_semana] < 8:
                    print("Clinica", clinica.nome, "não tem 8 medicos no dia", dia_semana)
    
    def testa(self):
        nomes_teste = []
        nifs_teste = []
        for medico in self.database["medicos"]:
            if medico.nome in nomes_teste:
                print("Nome", medico.nome, "repetido")
            else:
                nomes_teste.append(medico.nome)
            if medico.nif in nifs_teste:
                print("NIF", medico.nif, "repetido")
            else:
                nifs_teste.append(medico.nif)
        for enfermeiro in self.database["enfermeiros"]:
            if enfermeiro.nome in nomes_teste:
                print("Nome", enfermeiro.nome, "repetido")
            else:
                nomes_teste.append(enfermeiro.nome)
            if enfermeiro.nif in nifs_teste:
                print("NIF", enfermeiro.nif, "repetido")
            else:
                nifs_teste.append(enfermeiro.nif)

        
    def cria_nome(self):
        while True:
            nome = random.choice(self.nomes_proprios)
            sobrenome = random.choice(self.sobrenomes)
            if nome + " " + sobrenome not in nomes_usados:
                nomes_usados.append(nome + " " + sobrenome)
                return nome + " " + sobrenome
            else:
                nome = random.choice(self.nomes_proprios)
                meio = random.choice(self.nomes_proprios)
                sobrenome = random.choice(self.sobrenomes)
                if nome + " " + meio + " " + sobrenome not in nomes_usados:
                    nomes_usados.append(nome + " " + meio + " " + sobrenome)
                    return nome + " " + meio + " " + sobrenome
                
    def encontra_medico(self, nif):
        for medico in self.database["medicos"]:
            if medico.nif == nif:
                return medico
        return None
    
    def is_medico(self, nif):
        for medico in self.database["medicos"]:
            if medico.nif == nif:
                return True
        return False
        
    @staticmethod
    def cria_nif():
        while True:
            nif = "2"
            for _ in range(8):
                nif += str(random.randint(0, 9))
            if nif not in nifs_usados:
                nifs_usados.append(nif)
                return nif
            
    @staticmethod
    def cria_ssn():
        while True:
            ssn = ""
            for _ in range(11):
                ssn += str(random.randint(0, 9))
            if ssn not in ssn_usados:
                ssn_usados.append(ssn)
                return ssn
            
    @staticmethod
    def cria_codigo_sns():
        while True:
            sns = ""
            for _ in range(12):
                sns += str(random.randint(0, 9))
            if sns not in codigo_sns_usados:
                codigo_sns_usados.append(sns)
                return sns
            
    @staticmethod
    def cria_telefone():
        telefone = "9"
        for _ in range(8):
            telefone += str(random.randint(0, 9))
        return telefone
    
    @staticmethod
    def print_clinicas(database):
        i = 1
        for clinica in database["clinicas"]:
            print("Clinica", i)
            clinica.print()
            print()
            i += 1

    @staticmethod
    def print_enfermeiros(database):
        i = 1
        for enfermeiro in database["enfermeiros"]:
            print("Enfermeiro", i)
            enfermeiro.print()
            print()
            i += 1

    @staticmethod
    def print_medicos(database):
        i = 1
        for medico in database["medicos"]:
            print("Medico", i)
            medico.print()
            print()
            i += 1

    @staticmethod
    def print_agenda_medicos(database):
        for clinica in database["clinicas"]:
            clinica.print_agenda_medicos(database["medicos"])
    
    @staticmethod
    def print_pacientes(database):
        i = 1
        for paciente in database["pacientes"]:
            print("Paciente", i)
            paciente.print()
            print()
            i += 1

def converte_para_sql(final, new_file):
    new_file.write("INSERT INTO clinica (nome, telefone, morada) VALUES")
    for clinica_num in range(len(final.database["clinicas"])):
        clinica = final.database["clinicas"][clinica_num]
        new_file.write("\n('" + clinica.nome + "', '" + clinica.telefone + "', '" + clinica.morada.print() + "')")
        if clinica_num != len(final.database["clinicas"]) - 1:
            new_file.write(",")
    new_file.write(";\n\n")
    new_file.write("INSERT INTO enfermeiro (nif, nome, telefone, morada, nome_clinica) VALUES")
    for enfermeiro_num in range(len(final.database["enfermeiros"])):
        enfermeiro = final.database["enfermeiros"][enfermeiro_num]
        new_file.write("\n('" + enfermeiro.nif + "', '" + enfermeiro.nome + "', '" + enfermeiro.telefone + "', '" + enfermeiro.morada.print() + "', '" + enfermeiro.nome_clinica + "')")
        if enfermeiro_num != len(final.database["enfermeiros"]) - 1:
            new_file.write(",")
    new_file.write(";\n\n")
    new_file.write("INSERT INTO medico (nif, nome, telefone, morada, especialidade) VALUES")
    for medico_num in range(len(final.database["medicos"])):
        medico = final.database["medicos"][medico_num]
        new_file.write("\n('" + medico.nif + "', '" + medico.nome + "', '" + medico.telefone + "', '" + medico.morada.print() + "', '" + medico.especialidade + "')")
        if medico_num != len(final.database["medicos"]) - 1:
            new_file.write(",")
    new_file.write(";\n\n")
    new_file.write("INSERT INTO paciente (ssn, nif, nome, telefone, morada, data_nasc) VALUES")
    for paciente_num in range(len(final.database["pacientes"])):
        paciente = final.database["pacientes"][paciente_num]
        new_file.write("\n('" + paciente.ssn + "', '" + paciente.nif + "', '" + paciente.nome + "', '" + paciente.telefone + "', '" + paciente.morada.print() + "', '" + paciente.data_nascimento + "')")
        if paciente_num != len(final.database["pacientes"]) - 1:
            new_file.write(",")
    new_file.write(";\n\n")
    new_file.write("INSERT INTO trabalha (nif, nome, dia_da_semana) VALUES")
    for medico_num in range(len(final.database["medicos"])):
        medico = final.database["medicos"][medico_num]
        for clinica_num in range(len(list(medico.trabalho.keys()))):
            clinica = list(medico.trabalho.keys())[clinica_num]
            for dia_num in range(len(medico.trabalho[clinica])):
                dia = medico.trabalho[clinica][dia_num]
                new_file.write("\n('" + medico.nif + "', '" + clinica + "', " + str(dia) + ")")
                if medico_num != len(final.database["medicos"]) - 1 or clinica_num != len(list(medico.trabalho.keys())) - 1 or dia_num != len(medico.trabalho[clinica]) - 1:
                    new_file.write(",")
    new_file.write(";\n\n")
    new_file.write("INSERT INTO consulta (id, ssn, nif, nome, data, hora, codigo_sns) VALUES")
    for consulta_num in range(len(final.database["consultas"])):
        consulta = final.database["consultas"][consulta_num]
        new_file.write("\n(" + str(consulta.id) + ", '" + consulta.ssn_paciente + "', '" + consulta.nif_medico + "', '" + consulta.nome_clinica + "', '" + consulta.data + "', '" + consulta.hora + "', '" + consulta.codigo_sns + "')")
        if consulta_num != len(final.database["consultas"]) - 1:
            new_file.write(",")
    new_file.write(";\n\n")
    new_file.write("INSERT INTO receita (codigo_sns, medicamento, quantidade) VALUES")

    valores_receitas = []
    for consulta in final.database["consultas"]:
        for receita in consulta.receita:
            valores_receitas.append(f"('{consulta.codigo_sns}', '{receita.medicamento}', {receita.quantidade})")

    if valores_receitas:
        new_file.write("\n" + ",\n".join(valores_receitas) + ";\n\n")
    else:
        new_file.write(";\n\n")
    new_file.write("INSERT INTO observacao (id, parametro, valor) VALUES")
    for consulta_num in range(len(final.database["consultas"])):
        consulta = final.database["consultas"][consulta_num]
        for sintoma_num in range(len(consulta.sintomas)):
            sintoma = consulta.sintomas[sintoma_num]
            if hasattr(sintoma, "valor"):
                new_file.write("\n(" + str(sintoma.id_consulta) + ", '" + sintoma.parametro + "', " + str(sintoma.valor) + ")")
            else:
                new_file.write("\n(" + str(sintoma.id_consulta) + ", '" + sintoma.parametro + "', NULL)")
            if consulta_num != len(final.database["consultas"]) - 1 or sintoma_num != len(consulta.sintomas) - 1:
                new_file.write(",")
    new_file.write(";\n\n")
    print("Ficheiro de data criado")
    new_file.close()

def main():
    global ruas
    with open("ruas.txt", "r") as file:
        for line in file:
            ruas.append(line.strip())
    database = {
        "clinicas" : [],
        "enfermeiros" : [],
        "medicos" : [],
        "pacientes" : [],
        "consultas" : []
    }
    final = Popula(database)
    final.testa_consultas()
    new_file = open("../Data/data.sql", "w")
    converte_para_sql(final, new_file)


main()
        