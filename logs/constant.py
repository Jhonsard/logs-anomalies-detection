from datetime import datetime

class Constants:
    # dates de début et de fin pour la génération des logs
    LOGS_START_DATE: datetime = datetime(year=2026, month=10, day=1, hour=0, minute=0, second=0)
    LOGS_END_DATE: datetime = datetime(year=2026, month=11, day=30, hour=23, minute=59, second=59)

    # nombre voulu de logs à générer
    NUMBER_OF_LOGS: int = 100000

    # méthodes HTTP à utiliser pour simuler des logs
    HTTP_METHODS: list[str] = ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS", "HEAD"]

    # endpoints factices pour simuler des logs
    API_ENDPOINTS: list[str] = ["/login","/data","/metrics","/register","/logout","/profile","/settings","/dashboard","/admin","/api/v1/users","/api/v1/products","/api/v1/orders"]
    
    # codes de statut HTTP à utiliser pour simuler des logs
    HTTP_NORMAL_STATUS_CODES: list[str] = ["200", "201", "204"]
    HTTP_ERROR_STATUS_CODES: dict[str, list[str]] = {
        "server_errors": ["500","502","503"],
        "client_errors": ["400", "401", "403", "404"],
        "timeout": ["408", "504"],
        "rate_limit": ["429"]
        }

    # l'intervales entre anomalies
    NUMBER_OF_ANOMALY_INTERVALS: int = 5
    MIN_NUMBER_OF_ANOMALIES_PER_INTERVAL: int = 500
    MAX_NUMBER_OF_ANOMALIES_PER_INTERVAL: int = 1000
    NUMBER_OF_ANOMALY_IPS: int = 15
    
    # fichier de sortie pour le dataset de logs
    LOGS_DATASET_FILE_NAME: str = "data/logs_dataset.csv"

    # ratio de separation entre l'entrainement et le test
    TRAIN_SET_RATIO: float = 0.85 # entrainement = 85% du dataset

    ISOLATION_FOREST_MODEL_PATH: str = "models/isolation_forest.pkl"
    ONE_CLASS_SVM_MODEL_PATH: str = "models/one_class_svm.pkl"