import pandas as pd
import numpy as np

yearListFile = {
    '1995.xls': 9,
    '2002.xls': 16,
    '2007.xls': 12,
    '2012.xls': 10,
    '2017.xls': 11,
    '2022.xls': 12
}
departments = ['LOIRE ATLANTIQUE', 'MAINE ET LOIRE', 'MAYENNE', 'SARTHE', 'VENDEE']  
df_results = pd.DataFrame()


for yearFile, num_candidates in yearListFile.items():
    dfT1 = pd.read_excel('../cleaned_data/electorales/' + yearFile, sheet_name='Départements T1')

    df = dfT1[dfT1['Libellé du département'].isin(departments)] 

    year = yearFile.split('.')[0] 

    df['Année'] = year

    for i in range(0, num_candidates):
        columnVersion = ''
        if i > 0:
            columnVersion = '.' + str(i)
            
        df['Candidat'] = df['Prénom'+columnVersion] + ' ' + df['Nom'+columnVersion]

        df['Pourcentage tour 1'] = df['% Voix/Exp'+columnVersion]
        df['Pourcentage tour 2'] = 0

        temp_df = df[['Année', 'Libellé du département', 'Candidat', 'Pourcentage tour 1', 'Pourcentage tour 2']]

        df_results = pd.concat([df_results, temp_df], ignore_index=True)

    dfT2 = pd.read_excel('../cleaned_data/electorales/' + yearFile, sheet_name='Départements T2')
    dfT2 = dfT2[dfT2['Libellé du département'].isin(departments)]  # Filtre les départements

    for i in range(0, 2):
        columnVersion = ''
        if i > 0:
            columnVersion = '.' + str(i)

        for dep in departments:
            for idx, row in dfT2.iterrows():
                candidat = row['Prénom'+columnVersion] + ' ' + row['Nom'+columnVersion]
                if row['Libellé du département'] == dep and year in df_results['Année'].values and candidat in df_results['Candidat'].values:
                    df_results.loc[(df_results['Libellé du département'] == dep) & (df_results['Candidat'] == candidat) & (df_results['Année'] == year), 'Pourcentage tour 2'] = row['% Voix/Exp'+columnVersion]
                  
df_candidats = pd.read_excel('../cleaned_data/candidat/candidats.xlsx')

df_results['Année'] = df_results['Année'].astype(str)
df_candidats['Année'] = df_candidats['Année'].astype(str)

df_results_by_candidats = pd.merge(df_results, df_candidats, how='left', on=['Année', 'Candidat'])

yearsElection = df_results_by_candidats['Année'].unique()

# Pouvoir d'achat 
df_results_by_candidats['Pouvoir achat'] = 0
df_pouvoir_achat = pd.read_csv('../cleaned_data/pouvoir_achat/valeurs_annuelles.csv', sep=';')
df_pouvoir_achat['Annee'] = df_pouvoir_achat['Annee'].astype(str)

# Criminalité
df_results_by_candidats['Taux criminalite'] = 0
df_securite = pd.read_excel('../cleaned_data/securite/taux_criminalite.xlsx')
df_securite['Année'] = df_securite['Année'].astype(str)

# Chomage 
df_results_by_candidats['Taux chomage'] = 0
df_chomage = pd.read_csv('../cleaned_data/chomage/taux_chomage.csv', sep=';')
# Sélectionner la ligne pour la région Pays de la Loire
df_chomage = df_chomage[df_chomage['Libellé'] == 'Taux de chômage localisé par région - Pays de la Loire']
# Supprimer les colonnes non pertinentes
df_chomage = df_chomage.drop(columns=['Libellé', 'idBank', 'Dernière mise à jour', 'Période'])
# Transformer le dataframe pour avoir une ligne par trimestre
df_chomage = df_chomage.melt(var_name='Trimestre', value_name='Taux')
# Extraire l'année du trimestre
df_chomage['Année'] = df_chomage['Trimestre'].str.split('-').str[0].astype(str)
# Supprimer les colonnes non pertinentes
df_chomage = df_chomage.drop(columns=['Trimestre'])
# Convertir la colonne 'Taux' en décimaux
df_chomage['Taux'] = pd.to_numeric(df_chomage['Taux'], errors='coerce')
# Calculer la moyenne du taux de chômage par année
df_chomage = df_chomage.groupby('Année')['Taux'].mean().reset_index()

# Défaillance entreprises 
df_results_by_candidats['Nombre defaillance entreprise'] = 0
df_defaillance = pd.read_csv('../cleaned_data/defaillance/entreprises.csv', sep=';')
# Extraire l'année de la colonne "Periode"
df_defaillance["Annee"] = df_defaillance["Periode"].str.split("-").str[0]
# Convertir la colonne "Nombre defaillance entreprise" en nombre entier
df_defaillance["Nombre defaillance entreprise"] = df_defaillance["Nombre defaillance entreprise"].astype(int)
# Faire la somme du nombre de défaillances par année 
df_defaillance = df_defaillance.groupby("Annee")["Nombre defaillance entreprise"].sum().reset_index()

for i in range(len(yearsElection) - 1):
    start_year = int(yearsElection[i]) + 1
    end_year = int(yearsElection[i + 1])

    # Pouvoir d'achat 
    # Récupérer les taux de croissance annuels pour la période
    achat_growth_rates = df_pouvoir_achat.loc[(df_pouvoir_achat['Annee'].astype(int) >= start_year) & 
                                        (df_pouvoir_achat['Annee'].astype(int) <= end_year), 'Pouvoir achat'].values
    # Convertir les taux de croissance en multiplicateurs
    achat_multipliers = [(rate / 100) + 1 for rate in achat_growth_rates]
    # Calculer la croissance totale
    achat_total_growth = np.prod(achat_multipliers)
    # Convertir la croissance totale en un taux de croissance en pourcentage
    achat_total_growth_rate = (achat_total_growth - 1) * 100
    # Mettre à jour les lignes de df_results_by_candidats pour l'année actuelle avec la croissance totale
    df_results_by_candidats.loc[df_results_by_candidats['Année'] == str(end_year), 'Pouvoir achat'] = achat_total_growth_rate

    # Criminalité 
    # Récupérer les taux de criminalité annuels pour la période
    crime_growth_rates = df_securite.loc[(df_securite['Année'].astype(int) >= start_year) & 
                                        (df_securite['Année'].astype(int) <= end_year), 'Pays de la Loire'].values
    # Récupérer la moyenne durant le mandat 
    crime_average = 0
    if len(crime_growth_rates) > 0:
        crime_average = sum(crime_growth_rates) / len(crime_growth_rates)
    # Mettre à jour les lignes de df_results_by_candidats pour l'année actuelle avec le nombre de crime moyen
    df_results_by_candidats.loc[df_results_by_candidats['Année'] == str(end_year), 'Taux criminalite'] = crime_average

    # Chomage 
    # Récupérer les taux de chomage annuels pour la période
    chomage_growth_rates = df_chomage.loc[(df_chomage['Année'].astype(int) >= start_year) & 
                                        (df_chomage['Année'].astype(int) <= end_year), 'Taux'].values
    # Récupérer la moyenne durant le mandat 
    chomage_average = 0
    if len(chomage_growth_rates) > 0:
        chomage_average = sum(chomage_growth_rates) / len(chomage_growth_rates)
    # Mettre à jour les lignes de df_results_by_candidats pour l'année actuelle avec le nombre de chomage moyen
    df_results_by_candidats.loc[df_results_by_candidats['Année'] == str(end_year), 'Taux chomage'] = chomage_average

    # Défaillance d'entreprises 
    # Récupérer le nombre défaillances d'entreprises annuels pour la période
    defaillance_growth_rates = df_defaillance.loc[(df_defaillance['Annee'].astype(int) >= start_year) & 
                                        (df_defaillance['Annee'].astype(int) <= end_year), 'Nombre defaillance entreprise'].values
    # Récupérer la somme durant le mandat 
    defaillance_sum = 0
    if len(defaillance_growth_rates) > 0:
        defaillance_sum = sum(defaillance_growth_rates)
    # Mettre à jour les lignes de df_results_by_candidats pour l'annee actuelle avec le nombre de défaillance d'entreprise moyen
    df_results_by_candidats.loc[df_results_by_candidats['Année'] == str(end_year), 'Nombre defaillance entreprise'] = defaillance_sum

df_results_by_candidats['Année'] = df_results_by_candidats['Année'].astype(int)
df_results_by_candidats['Pourcentage tour 1'] = df_results_by_candidats['Pourcentage tour 1'].apply(lambda x: float(x.replace(',', '.')) if isinstance(x, str) and ',' in x else x)
df_results_by_candidats['Pourcentage tour 2'] = df_results_by_candidats['Pourcentage tour 2'].apply(lambda x: float(x.replace(',', '.')) if isinstance(x, str) and ',' in x else x)
df_results_by_candidats['Pouvoir achat'] = df_results_by_candidats['Pouvoir achat'].astype(float)
df_results_by_candidats['Taux criminalite'] = df_results_by_candidats['Taux criminalite'].astype(float)
df_results_by_candidats['Taux chomage'] = df_results_by_candidats['Taux chomage'].astype(float)
df_results_by_candidats['Nombre defaillance entreprise'] = df_results_by_candidats['Nombre defaillance entreprise'].astype(int)


# Obtenir les indices des lignes ayant le pourcentage le plus élevé pour chaque année et département
idx1 = df_results_by_candidats.groupby(['Année', 'Libellé du département'])['Pourcentage tour 1'].idxmax()
# Créer une nouvelle colonne 'Gagnant' et initialiser à 0
df_results_by_candidats['Gagnant tour 1'] = 0
# Mettre '1' dans la colonne 'Gagnant' pour les lignes correspondant aux indices obtenus
df_results_by_candidats.loc[idx1, 'Gagnant tour 1'] = 1
# Réinitialiser les index du DataFrame
df_results_by_candidats = df_results_by_candidats.reset_index(drop=True)

# Obtenir les indices des lignes ayant le pourcentage le plus élevé pour chaque année et département
idx2 = df_results_by_candidats.groupby(['Année', 'Libellé du département'])['Pourcentage tour 2'].idxmax()
# Créer une nouvelle colonne 'Gagnant' et initialiser à 0
df_results_by_candidats['Gagnant tour 2'] = 0
# Mettre '1' dans la colonne 'Gagnant' pour les lignes correspondant aux indices obtenus
df_results_by_candidats.loc[idx2, 'Gagnant tour 2'] = 1
# Réinitialiser les index du DataFrame
df_results_by_candidats = df_results_by_candidats.reset_index(drop=True)

df_results_by_candidats.to_excel('../fusioned_data/results_by_year.xlsx', index=False)
df_results_by_candidats.to_csv('../fusioned_data/results_by_year.csv', index=False)