import flwr as fl
from FL_Server.strategy import SecureFLStrategy
from FL_Server.strategy_fedavg import SimpleFLStrategy
from FL_Server.config import ROUNDS

def main():

    # strategy = SimpleFLStrategy()
    strategy = SecureFLStrategy()

    fl.server.start_server(
        server_address="0.0.0.0:8080",
        config=fl.server.ServerConfig(num_rounds=ROUNDS),
        strategy=strategy
    )
    
if __name__ == "__main__":
    print("Starting Federated Learning Server...")
    main()