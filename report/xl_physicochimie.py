from tools import QueryScript
import pandas as pd
from calcul.exposure_conditions.exposure_conditions import conditions

def test_chimie_superieur_repro(list_mp):
    list_test = []
    output = QueryScript(
        f"SELECT date FROM key_dates WHERE date_id IN (1, 4, 6, 7) and measurepoint_fusion_id IN {tuple(list_mp)}"
    ).execute()

    n = len(list_mp)
    for i in range(n):
        [R0, RN, debut_chimie, fin_chimie] = output[i:i+4]

        if RN == None or R0 == None:
            delta_repro = None
        else:
            delta_repro = (RN - R0).days

        if debut_chimie == None or fin_chimie == None:
            delta_chimie = None
        else:
            delta_chimie = (fin_chimie - debut_chimie).days

        try:
            boolean = delta_chimie > delta_repro
        except TypeError:
            boolean = (delta_chimie != None)

        list_test.append(boolean)

    return list_test

def temperatures_dataframe(list_mp):
    list_test = test_chimie_superieur_repro(list_mp)
    output = QueryScript(
        f"SELECT sensor2_min, sensor2_moy, sensor2_max, sensor3_min, sensor3_moy, sensor3_max FROM average_temperature WHERE measurepoint_fusion_id IN {tuple(list_mp)}"
    ).execute()

    matrix = []
    n = len(list_mp)
    for i in range(n):
        test = list_test[i]
        [sensor2_min, sensor2_moy, sensor2_max, sensor3_min, sensor3_moy, sensor3_max] = output[i]

        moyenne = sensor3_moy if test else sensor2_moy

        try:
            minimum = min(sensor2_min, sensor3_min)
        except TypeError:
            if sensor3_min == None and sensor2_min == None:
                minimum = None
            else:
                minimum = sensor2_min if sensor3_min == None else sensor3_min

        try:
            maximum = max(sensor2_max, sensor3_max)
        except TypeError:
            if sensor3_max == None and sensor2_max == None:
                maximum = 'NA'
            else:
                maximum = sensor2_max if sensor3_max == None else sensor3_max

        matrix.append([minimum, moyenne, maximum])

    df = pd.DataFrame(matrix)
    df.columns = ['Temperature minimum', 'Temperature moyenne', 'Temperature maximum']
    return df


def values_dataframe(list_mp):
    matrix = []

    for mp in list_mp:
        list_conductivity, list_ph, list_oxygen = conditions(mp)
        values = list_conductivity + list_ph + list_oxygen
        matrix.append(values)

    df = pd.DataFrame(matrix)
    df.columns = ['Conductivité J0', 'Conductivité J14', 'Conductivité JN', 'Conductivité J21',
                  'pH J0', 'pH J14', 'pH JN', 'pH J21',
                  'Oxygène J0', 'Oxygène J14', 'Oxygène JN', 'Oxygène J21']
    df = df.dropna(how='all', axis='columns')

    return df


def create_physicochimie_dataframe(head_dataframe, list_campaigns, dict_mp):
    list_dataframe = []
    for campaign_str in list_campaigns:
        list_mp = dict_mp[campaign_str]
        df_temperature = temperatures_dataframe(list_mp)
        df_values = values_dataframe(list_mp)
        df_temperature_values = pd.concat([df_temperature, df_values], axis=1)
        list_dataframe.append(df_temperature_values)

    df_values = pd.concat(list_dataframe)
    df_concat = pd.concat([head_dataframe, df_values], axis=1)
    df_physicochimie = df_concat.sort_values('Numéro')

    return df_physicochimie
