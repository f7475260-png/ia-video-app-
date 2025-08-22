from datetime import datetime, timedelta

def best_publish_time():
    return (datetime.utcnow() + timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S UTC")
