from tools import QueryScript, translate
import pandas as pd
import env

def create_tox_dataframe(campaigns_dict, measurepoint_list):
    list_dataframe = []
    data = QueryScript(f"SELECT measurepoint_id, round(male_survival_7_days), round(alimentation, 1), round(neurotoxicity, 1), round(female_survivor), number_days_exposition, number_female_concerned, round(percent_inhibition_fecondite, 1), number_female_analysis, molting_cycle,number_female_concerned_area,endocrine_disruption, molting_cycle_conformity, surface_retard_conformity FROM {env.DATABASE_TREATED}.toxtable WHERE version=  {env.CHOSEN_VERSION()} AND measurepoint_id IN {tuple(measurepoint_list) if len(measurepoint_list)>1 else '('+(str(measurepoint_list[0]) if len(measurepoint_list) else '0')+')'};").execute()
    for campaign_id in campaigns_dict:
        matrix =[]
        for place_id in campaigns_dict[campaign_id]["place"]:
            temp = [None]*20
            if "duplicate" in campaigns_dict[campaign_id]["place"][place_id] and ("alimentation" in campaigns_dict[campaign_id]["place"][place_id]["duplicate"] or "neurology" in campaigns_dict[campaign_id]["place"][place_id]["duplicate"] or "reproduction" in campaigns_dict[campaign_id]["place"][place_id]["duplicate"]):
                for measurepoint_id in campaigns_dict[campaign_id]["place"][place_id]["measurepoint"]:
                    number = float(str(campaigns_dict[campaign_id]["place"][place_id]["number"])+'.'+str(campaigns_dict[campaign_id]["place"][place_id]["measurepoint"][measurepoint_id]["number"]))
                    for mp_id, male_survival_7_days, alimentation, neurotoxicity, female_survivor, number_days_exposition, number_female_concerned, percent_inhibition_fecondite, number_female_analysis, molting_cycle, number_female_concerned_area, endocrine_disruption, molting_cycle_conformity, surface_retard_conformity in data :
                        if measurepoint_id==mp_id and measurepoint_id in measurepoint_list :
                            for index in range(4):
                                temp[index] = [campaigns_dict[campaign_id]["number"], number, translate(campaigns_dict[campaign_id]["place"][place_id]["name"]), campaigns_dict[campaign_id]["place"][place_id]["agency"] if "agency" in campaigns_dict[campaign_id]["place"][place_id] else 'ND'][index]
                            temp[5], temp[6] = male_survival_7_days if male_survival_7_days else 'NA', alimentation if male_survival_7_days else None
                            if neurotoxicity != None:
                                temp[7] = neurotoxicity if male_survival_7_days else None
                            if female_survivor or number_days_exposition:
                                for index in range(9,20):
                                    temp[index] = [female_survivor, number_days_exposition, number_female_concerned, percent_inhibition_fecondite if percent_inhibition_fecondite and female_survivor else "NA", number_female_analysis, molting_cycle, number_female_concerned_area, endocrine_disruption  if endocrine_disruption else "NA", measurepoint_id, molting_cycle_conformity, surface_retard_conformity][index-9]
                    matrix.append(temp)
                    temp = [None]*20
            else :
                number = campaigns_dict[campaign_id]["place"][place_id]["number"]
                for measurepoint_id in campaigns_dict[campaign_id]["place"][place_id]["measurepoint"]:
                    for mp_id, male_survival_7_days, alimentation, neurotoxicity, female_survivor, number_days_exposition, number_female_concerned, percent_inhibition_fecondite, number_female_analysis, molting_cycle, number_female_concerned_area, endocrine_disruption, molting_cycle_conformity, surface_retard_conformity in data :
                        if measurepoint_id==mp_id :
                            for index in range(4):
                                temp[index] = [campaigns_dict[campaign_id]["number"], number, translate(campaigns_dict[campaign_id]["place"][place_id]["name"]), campaigns_dict[campaign_id]["place"][place_id]["agency"] if "agency" in campaigns_dict[campaign_id]["place"][place_id] else 'ND'][index]
                            temp[5], temp[6] = male_survival_7_days if male_survival_7_days else 'NA', alimentation if male_survival_7_days else None
                            if neurotoxicity !=None :
                                temp[7] = neurotoxicity if male_survival_7_days else None
                            if female_survivor or number_days_exposition :
                                for index in range(9,20):
                                    temp[index] = [female_survivor, number_days_exposition, number_female_concerned, percent_inhibition_fecondite if percent_inhibition_fecondite and female_survivor else "NA" , number_female_analysis, molting_cycle, number_female_concerned_area, endocrine_disruption if endocrine_disruption else "NA", measurepoint_id, molting_cycle_conformity, surface_retard_conformity][index-9]
                matrix.append(temp)
        df = pd.DataFrame(matrix)
        df.columns = ['Campagne', 'Numéro', 'Station de mesure', 'Code Agence','','Survie Male - 7 jours', 'Alimentation',
                'Neurotoxicité AChE','', 'Survie Femelle','Nombre jours exposition in situ',
                'n','Fécondité','n','Cycle de mue','n','Perturbation endocrinienne','', '', '']
        list_dataframe.append(df)
    df_values = pd.concat(list_dataframe)
    df_sorted = df_values.sort_values(['Numéro', 'Campagne'])
    return df_sorted
