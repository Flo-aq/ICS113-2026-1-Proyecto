from gurobipy import GRB, Model, quicksum
import gurobipy as gp
import numpy as np
import pandas as pd

#=============================
# Funciones 
#=============================

def load_index_csv(path: str) -> list:
  df = pd.read_csv(path)
  matrix = df.to_numpy()
  return [matrix[f][0] for f in range(len(matrix))]

# por mientras
def load_csv(path: str) -> dict:
  df = pd.read_csv(path)
  matrix = df.to_numpy()

  data_dict = {(fila[0]): fila[1] for fila in matrix}

  return data_dict

def process_results(model, vars: list, sets: list) -> None:
  
  with open("results.txt", "w", encoding="utf-8") as file:
    file.write(f"-------- Valor Óptimo -------\nEl valor óptimo de la función es: {model.ObjVal}\n")


# Definición del modelo
#-----------------------------------------------------------------------------------
model = Model()

#============
# Conjuntos
#============
# I = zonas de demanda (comunas)
zonas_demanda = load_index_csv("Datos/poblacion_comunas_censo2024_consolidado.csv")

# J = potenciales centros de triaje.
# [!] No sé si vamos a utilizar el indice (Ej. "1", "2", etc) o el nombre del recinto
centros_triaje = load_index_csv("Datos\infraestructura_deportiva_consolidada.csv")

# K = Hospitales de la red asistencial de la región de Valparaíso
#hospitales = load_index_csv()

# T = Horizonte de planificación
dias = range(1, 8)

# G = tipo de paciente.
# [!] Hay que ver si "grave" se deja o no
tipo_paciente = ["leve", "moderado", "grave"]




