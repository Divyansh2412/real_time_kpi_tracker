# producer.py
import json
import random
import time
from datetime import datetime
from kafka import KafkaProducer

TOPIC = "sales"
BROKER = "localhost:9092"

producer = KafkaProducer(
    bootstrap_servers=BROKER,
    value_serializer=lambda v: json.dumps(v).encode("utf-8")
)

products = [
    {"id": "P001", "category": "Electronics"},
    {"id": "P002", "category": "Home"},
    {"id": "P003", "category": "Clothing"},
    {"id": "P004", "category": "Sports"},
    {"id": "P005", "category": "Books"}
]

def generate_event():
    p = random.choice(products)
    event = {
        "order_id": f"O{random.randint(10000,99999)}",
        "product_id": p["id"],
        "category": p["category"],
        "price": round(random.uniform(5, 500), 2),
        "quantity": random.randint(1, 5),
        "timestamp": datetime.utcnow().isoformat()
    }
    return event

if __name__ == "__main__":
    print("Starting producer. Press Ctrl+C to stop.")
    try:
        while True:
            ev = generate_event()
            producer.send(TOPIC, ev)
            producer.flush()
            print("Produced:", ev)
            time.sleep(random.uniform(0.5, 1.5))
    except KeyboardInterrupt:
        print("Producer stopped.")
