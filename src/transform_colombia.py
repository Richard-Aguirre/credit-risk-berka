"""
read the Colombia Colombia loan portfolio from the raw schema, clean it and save it to the processed schema.
"""

import pandas as pd
from sqlalchemy import text
from src.load import get_engine

COLUMN_NAMES = {
    "tipo_entidad": "entity_type",
    "codigo_entidad": "entity_code",
    "nombreentidad": "entity_name",
    "fecha_corte": "cutoff_date",
    "unicap": "group_code",
    "descrip_uc": "group_name",
    "renglon": "product_code",
    "desc_renglon": "product_name",
    "_1_saldo_de_la_cartera_a": "total_balance",
    "_2_vigente": "current_balance",
    "_16_n_mero_de_clientes_mora": "clients_past_due",
    "_17_calificaci_n_de_riesgo": "risk_a_clients",
    "_18_calificaci_n_de_riesgo": "risk_a_balance",
    "_19_calificaci_n_de_riesgo": "risk_b_clients",
    "_20_calificaci_n_de_riesgo": "risk_b_balance",
    "_21_calificaci_n_de_riesgo": "risk_c_clients",
    "_22_calificaci_n_de_riesgo": "risk_c_balance",
    "_23_calificaci_n_de_riesgo": "risk_d_clients",
    "_24_calificaci_n_de_riesgo": "risk_d_balance",
    "_25_calificaci_n_de_riesgo": "risk_e_clients",
    "_26_calificaci_n_de_riesgo": "risk_e_balance"
}


CREDIT_TYPES = {
    "1": "consumer",
    "2": "consumer",
    "3": "consumer",
    "4": "consumer",
    "5": "consumer",
    "6": "consumer",
    "7": "microcredit",
    "8": "microcredit",
    "9": "housing",
    "10": "housing",
    "11": "housing",
    "12": "housing",
    "13": "housing",
    "14": "housing",
    "15": "housing",
    "16": "housing",
    "17": "housing",
    "18": "housing",
    "19": "commercial",
    "20": "commercial",
    "21": "commercial",
    "22": "commercial",
    "23": "commercial",
    "24": "commercial",
    "25": "commercial",
    "26": "commercial",
    "27": "commercial",
    "28": "commercial",
    "29": "consumer",
    "30": "consumer",
    "31": "housing",
    "32": "housing"
}


FINAL_COLUMNS = ['entity_type', 'entity_code', 'entity_name', 'cutoff_date',
       'credit_type', 'group_code', 'group_name',
       'total_balance', 'current_balance', 'past_due', 'npl_ratio', 'clients_past_due',
       'risk_a_clients', 'risk_a_balance', 'risk_b_clients', 'risk_b_balance',
       'risk_c_clients', 'risk_c_balance', 'risk_d_clients', 'risk_d_balance',
       'risk_e_clients', 'risk_e_balance']