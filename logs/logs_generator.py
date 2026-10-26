"""
    Script pour generer mes logs
"""
import os
import sys
import faker
from datetime import datetime, timedelta
import random

sys.path.append(os.getcwd())
from logs.constant import Constants as cts

# methode pour generer le pas de temps entre les logs
def generate_datetimes(start_date: datetime, end_date: datetime, number_logs: int) -> list[datetime]:
    """
    Génère une liste de pas de temps sur une période donnée
    """
    timestamps = []
    total_seconds = (end_date - start_date).total_seconds()

    for i in range(number_logs):
        random_offset = random.random()  * total_seconds
        timestamp = start_date + timedelta(seconds=random_offset)
        timestamps.append(timestamp)
    
    # trie de notre liste de timestamps dans l'ordre croissant
    timestamps.sort()
    
    return timestamps

# methode pour generer les intrvales d'anomalies
def generate_anomaly_intervals(
    number_of_logs: int,
    number_of_anomaly_intervals: int,
    min_number_of_anomaly_per_interval: int,
    max_number_of_anomaly_per_interval: int,
    anomaly_types: list[str]
) -> list[dict[str, int | str]]:
    """
    Génère les intervalles d'anomalies
    """
    intervals = []

    #
    for _ in range(number_of_anomaly_intervals):
        start_idx = random.randint(0, number_of_logs - max_number_of_anomaly_per_interval)
        nb_anomaly = random.randint(min_number_of_anomaly_per_interval, max_number_of_anomaly_per_interval)
        end_idx = min(start_idx + nb_anomaly, number_of_logs - 1)

        intervals.append(
            {
                "start_idx": start_idx,
                "end_idx": end_idx,
                "type": random.choice(anomaly_types)
            }
        )
    
    return intervals

def generate_logs_dataset(
    start_date: datetime,
    end_date: datetime,
    number_of_logs: int,
    number_of_anomaly_intervals: int,
    min_number_of_anomaly_per_interval: int,
    max_number_of_anomaly_per_interval: int,
    http_error_list: list[str],
    number_of_anomalies_ips: int,
    logs_dataset_file_name: str,
    http_methods: list[str],
    http_normal_status_codes: list[str],
    http_error_status_codes: dict[str, list[str]],
    api_endpoints: list[str]
):
    """
    Génère le dataset de logs en incluant des anomalies
    """
    fak = faker.Faker()

    # Génération des adresses IP d'anomalies(ou factices)
    anomaly_ips = [fak.ipv4() for _ in range(number_of_anomalies_ips)]
    timestamp = generate_datetimes(
        start_date=start_date,
        end_date=end_date,
        number_logs=number_of_logs
    )
    
    anomaly_types = http_error_list.copy()
    anomaly_types.append("mixed_errors")

    # Liste d'intervales d'anomalies
    anomaly_intervals = generate_anomaly_intervals(
        number_of_logs=number_of_logs,
        number_of_anomaly_intervals=number_of_anomaly_intervals,
        min_number_of_anomaly_per_interval=min_number_of_anomaly_per_interval,
        max_number_of_anomaly_per_interval=max_number_of_anomaly_per_interval,
        anomaly_types=anomaly_types
    )
    
    with open(logs_dataset_file_name, "w") as f:
        f.write("timestamp,user_ip,methode,status_code,endpoint,response_time\n")

        for i in range(number_of_logs):
            timestamp_i = timestamp[i]
            user_ip = fak.ipv4()
            methode = random.choice(http_methods)
            status_code = random.choice(http_normal_status_codes)
            endpoint = random.choice(api_endpoints)
            response_time = random.randint(10, 300)

            for interval in anomaly_intervals:
                if interval["start_idx"] <= i <= interval["end_idx"]:
                    # Changer l'IP pour une IP d'anomalie
                    user_ip = random.choice(anomaly_ips)

                    if interval["type"] == "server_errors":
                        status_code = random.choice(http_error_status_codes["server_errors"])
                        
                    elif interval["type"] == "client_errors":
                        status_code = random.choice(http_error_status_codes["client_errors"])

                    elif interval["type"] == "timeout":
                        status_code = random.choice(http_error_status_codes["timeout"])
                        response_time = random.randint(1000, 5000)

                    elif interval["type"] == "rate_limit":
                        status_code = random.choice(http_error_status_codes["rate_limit"])

                    else:
                        status_code = random.choice(listcl(http_error_status_codes.values()))[0]
                        response_time = random.randint(1000, 5000)
            
            f.write(f"{timestamp_i},{user_ip},{methode},{status_code},{endpoint},{response_time}\n")
    print(f"[OK] le fichier csv {logs_dataset_file_name} a été généré avec {number_of_logs} logs et {number_of_anomaly_intervals}",
          f"et {number_of_anomaly_intervals} plage d'anomalies.")

if __name__ == "__main__":
    generate_logs_dataset(
        start_date = cts.LOGS_START_DATE,
        end_date = cts.LOGS_END_DATE,
        number_of_anomaly_intervals = cts.NUMBER_OF_ANOMALY_INTERVALS,
        number_of_logs = cts.NUMBER_OF_LOGS,
        min_number_of_anomaly_per_interval = cts.MIN_NUMBER_OF_ANOMALIES_PER_INTERVAL,
        max_number_of_anomaly_per_interval = cts.MAX_NUMBER_OF_ANOMALIES_PER_INTERVAL,
        http_error_list = list(cts.HTTP_ERROR_STATUS_CODES.keys()),
        number_of_anomalies_ips = cts.NUMBER_OF_ANOMALY_IPS,
        logs_dataset_file_name = cts.LOGS_DATASET_FILE_NAME,
        http_methods = cts.HTTP_METHODS,
        http_normal_status_codes= cts.HTTP_NORMAL_STATUS_CODES,
        http_error_status_codes = cts.HTTP_ERROR_STATUS_CODES,
        api_endpoints= cts.API_ENDPOINTS
    )