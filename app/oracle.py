import time

def fetch_from_oracle(key: str):
    time.sleep(2)
    return {
        "key": key,
        "value": f"Data for {key} from Oracle"
    }
