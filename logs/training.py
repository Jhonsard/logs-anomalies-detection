import sys
import os
from logging import logProcesses
import pandas as pd
import numpy as np 
import joblib as jl # librerie qui nous permettra de stocker nos donner dans le dossier models
from matplotlib import pyplot as plt

from sklearn.ensemble import IsolationForest
from sklearn.svm import OneClassSVM

sys.path.append(os.getcwd())
from logs.constant import Constants as cts
from logs.preprocessing import LogPreprocessor as lpr


class AnomalyDetector:
    def __init__(self):
        self.isolation_forest = IsolationForest(
            n_jobs=-1, verbose=1, contamination=0.05
        )
        self.one_class_svm = OneClassSVM(verbose=1, nu=0.05)

    def train_models(self, X: np.ndarray):
        """
            Entrainement de modele par IsolatioForest et One classe SVM
        """
        self.isolation_forest.fit(X)
        self.one_class_svm.fit(X)
        
        # Sauvegarde des modèles entraînés
        jl.dump(self.isolation_forest, cts.ISOLATION_FOREST_MODEL_PATH)
        jl.dump(self.one_class_svm, cts.ONE_CLASS_SVM_MODEL_PATH)
        

    def predict(self, X: np.ndarray) -> dict[str, np.ndarray]:
        """
            Fait la prediction IsolatioForest et OneClassSVM sur la variable X
        """

        isolation_forest: IsolationForest = jl.load(cts.ISOLATION_FOREST_MODEL_PATH)
        one_class_svm: OneClassSVM = jl.load(cts.ONE_CLASS_SVM_MODEL_PATH)
        
        isolation_forest_pred = isolation_forest.predict(X)
        one_class_svm_pred = one_class_svm.predict(X)
        
        return {
            "isolation_forest": isolation_forest_pred,
            "one_class_svm": one_class_svm_pred
        }

    # plan d'evaluation de nos modeles
    def compute_anomaly_scores(self, X: np.ndarray) -> dict[str, np.ndarray]:
        """ 
            Compute anomaly score per model
        """
        isolation_forest: IsolationForest = jl.load(cts.ISOLATION_FOREST_MODEL_PATH)
        one_class_svm: OneClassSVM = jl.load(cts.ONE_CLASS_SVM_MODEL_PATH)
        
        isolation_forest_decision = isolation_forest.decision_function(X)
        one_class_svm_decision = one_class_svm.decision_function(X)
        
        return {
            "isolation_forest": isolation_forest_decision,
            "one_class_svm": one_class_svm_decision
        }

    def evaluate_models(self, X: np.ndarray):
        """
            Evalue IsolationForest et OneClass SVM
        """
        scores = self.compute_anomaly_scores(X)

        fig, (ax1, ax2) = plt.subplots(2, 1)

        ax1.hist(scores['isolation_forest'], bins=20, color='blue', alpha=.7)
        ax1.set_title("Histogramme isolation forest")

        ax2.hist(scores['one_class_svm'], bins=20, color='green', alpha=.7)
        ax2.set_title("Histogramme One Class SVM")

        plt.xlabel("Scores d'anomalies")
        plt.ylabel("Frequences")
        plt.tight_layout()

        plt.show()

        predictions = self.predict(X)

        outlier_isolation_forest_ratio = np.mean(predictions['isolation_forest']==-1)
        outlier_one_class_svm_ratio = np.mean(predictions['one_class_svm']==-1)
        
        print("|===========================================================================|")
        print(f"| Ratio d'anomalies Isolation Forest: {outlier_isolation_forest_ratio:.2%} |")
        print(f"| Ratio d'anomalies One Class SVM: {outlier_one_class_svm_ratio:.2%}       |")
        print("|===========================================================================|")

if __name__ == '__main__':
    df = pd.read_csv(cts.LOGS_DATASET_FILE_NAME, skipinitialspace=True)

    preprocessor = lpr()

    df_train, df_test = preprocessor.split_dataset(df)
    print()
    print("++++++++++++++++++++++++++++++Pre traitement des modeles+++++++++++++++++++++++++++++++++++++")
    X_train, df_train_engineered = preprocessor.fit_transform(df_train)
    X_test, df_test_engineered = preprocessor.fit_transform(df_test)

    detector = AnomalyDetector()
    print("______________________________________________________________________________________________")
    print()
    print("++++++++++++++++++++++++++++++Entrainement des modeles+++++++++++++++++++++++++++++++++++++")
    detector.train_models(X_train)
    print("______________________________________________________________________________________________")
    print()
    print("++++++++++++++++++++++++++++++Evaluation des modeles+++++++++++++++++++++++++++++++++++++")
    detector.evaluate_models(X_test)
    print("______________________________________________________________________________________________")
    print()