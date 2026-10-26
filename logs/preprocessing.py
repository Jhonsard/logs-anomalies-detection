""" Script pour lire le fichier des logs genenrers ou le feature engineering"""
import os
import sys
import pandas as pd
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline

sys.path.append(os.getcwd())
from logs.constant import Constants as cts


class LogPreprocessor:
    def __init__(self) -> None:
        self.preprocessor = None # variable ou l'on stocke le pipe line de nos caracteristiques

    # methode d'ajout des nouvelles colonnes
    def parse_features(self, df) -> pd.DataFrame:

        df['status_code'] = df['status_code'].astype(str)
        df['timestamp'] = pd.to_datetime(df['timestamp']) # inserer des nouvelles valeurs dans le tableau qui sont de date
        df['hour_of_day'] = df['timestamp'].dt.hour
        df['day_of_week'] = df['timestamp'].dt.day_of_week
        df['month_of_week'] = df['timestamp'].dt.month
        df['is_weekend'] = df['day_of_week'].isin([5,6]).astype(int)


        # nouveau data frame pour mesurer les activites de l'utiliateur
        user_stats = df.groupby('user_ip', as_index=False).agg(
                # calcul  d'erreur http par utilisateur
                error_count=("status_code", lambda x: (x.str.startswith("5") | x.str.startswith("4")).sum()),
                unique_error_type=("status_code", lambda x: x[x.str.startswith("5") | x.str.startswith("4")].nunique()),                    
                avg_response_time=('response_time', 'mean'), # panda comprends automatiquement ce que mean veut dire pour la moyenne
                max_response_time=('response_time', 'max')).reset_index() # on remet les indexes de notre data frame dans l'etat standard

        df = df.merge(user_stats, on='user_ip', how='left') # `on` porte la cle primaire et `how` specifie la jointure

        # ajoutons une colone pour categoriser la reponse en fonction du temps
        df['response_time_category'] = pd.cut(
            # nous discretison nos reponses `bins` portant les interval
            df['response_time'], bins=[-1, 100, 200, 300],
            labels=['fast', 'normal', 'slow'] # de -1 a 100 : fast
        )

        # ajoutons une colonne pour identifier les anomalies potentielles
        df['is_potential_anomalous'] = (
            (df['response_time'] > 200) |
            (df['status_code'].str.startswith("5") | df['status_code'].str.startswith("4"))
        ).astype(int)
        
        return df

    def build_preprocessor(self, df):
        # passons au regroupement des variables

        numeric_features = [
            'response_time',
            'hour_of_day',
            'day_of_week',
            'month_of_week',
            'error_count',
            'unique_error_type',
            'avg_response_time',
            'max_response_time'
        ]

        categorical_features =[
            'is_weekend',
            'methode',
            'endpoint',
            'is_potential_anomalous',
            'response_time_category'
        ]

        numeric_transformer = Pipeline(steps=[
            ('scaler', StandardScaler())
        ])

        categorical_transformer = Pipeline(steps=[
            ('onehot', OneHotEncoder(handle_unknown='ignore'))
        ])

        # commande pour combiner ensemble les deux pipelines
        self.preprocessor = ColumnTransformer(
            transformers=[
                ('num', numeric_transformer, numeric_features),
                ('cat', categorical_transformer, categorical_features)
            ]
        )

        return self # retourne l'objet courant

    def fit_transform(self, df):
        
        df_parsed = self.parse_features(df)
        
        self.build_preprocessor(df=df_parsed)

        X = df_parsed.drop(['timestamp', 'status_code', 'user_ip'], axis=1)

        X_processed = self.preprocessor.fit_transform(X)
        
        return X_processed, X

    def split_dataset(self, df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
        """
            Separe notre dataset en deux parties:
            - les données d'entrainement
            - les donnees de test
        """
        # melange de nos donnes dans le dataset avec le shufling method
        df = df.sample(n=len(df)) # melange tout le dataframe

        train_test_size = cts.TRAIN_SET_RATIO * len(df)

        df_train = df.iloc[:int(train_test_size)]
        df_test = df.iloc[int(train_test_size):]

        return df_train, df_test

if __name__ == '__main__':
    df = pd.read_csv('data/logs_dataset.csv', skipinitialspace=True)

    log_preprocessor = LogPreprocessor()
    X_processed, X = log_preprocessor.fit_transform(df)

    print('X_processed Donne !')
    print( )
    print('Shape:', X_processed.shape)
    print('X_Shape:', X.shape)
    print( )
    print(f"X_processed:\n{X_processed}")
    print(f"X:\n{X.head()}")

    X.to_csv('data/logs_preprocessed.csv')