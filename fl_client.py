import os
import sys

import flwr as fl
from FL_Client.Flower import FlowerClient

if __name__ == "__main__":

    if len(sys.argv) == 3:
        client_id = int(sys.argv[1])
        split_type = sys.argv[2]
    else:
        client_id = int(os.getenv("CLIENT_ID", "1"))
        split_type = os.getenv("SPLIT_TYPE", "non_iid")

    server_address = os.getenv("SERVER_ADDRESS", "localhost:8080")

    print(f"Starting Client {client_id} with {split_type}")

    fl.client.start_numpy_client(
        server_address=server_address,
        client=FlowerClient(client_id, split_type),
    )