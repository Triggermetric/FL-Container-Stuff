import flwr as fl
import numpy as np
import json
import time
import os

from flwr.common import parameters_to_ndarrays, ndarrays_to_parameters
from flwr.server.strategy.aggregate import aggregate

from FL_Server.config import NUM_CLIENTS

os.makedirs("history", exist_ok=True)


class SimpleFLStrategy(fl.server.strategy.FedAvg):
    def __init__(self):
        super().__init__(
            fraction_fit=1.0,
            min_fit_clients=NUM_CLIENTS,
            min_available_clients=NUM_CLIENTS
        )

        # ===== map client id =====
        self.client_map = {}
        self.next_client_id = 1

        self.start_time = None

        # ===== history =====
        self.history = {
            "global": {
                "round": [],
                "accuracy": [],
                "loss": [],
                "round_time": []
            },
            "clients": {}
        }

    # ================= MAP CLIENT =================
    def _get_simple_client_id(self, cid):
        cid = str(cid)

        if cid not in self.client_map:
            self.client_map[cid] = str(self.next_client_id)
            self.next_client_id += 1

        return self.client_map[cid]

    # ================= TRAIN =================
    def aggregate_fit(self, server_round, results, failures):
        self.start_time = time.time()

        if not results:
            return None, {}

        weights_results = []

        for idx, (client, res) in enumerate(results):
            weights = parameters_to_ndarrays(res.parameters)
            weights_results.append((weights, res.num_examples))

            metrics = res.metrics

            cid = self._get_simple_client_id(client.cid)

            acc = float(metrics.get("test_acc", 0))
            loss = float(metrics.get("test_loss", 0))
            t = float(metrics.get("train_time", 0))

            # ===== init client log =====
            if cid not in self.history["clients"]:
                self.history["clients"][cid] = {
                    "round": [],
                    "test_accuracy": [],
                    "test_loss": [],
                    "train_time": []
                }

            h = self.history["clients"][cid]

            h["round"].append(server_round)
            h["test_accuracy"].append(acc)
            h["test_loss"].append(loss)
            h["train_time"].append(t)

        # ===== aggregate model =====
        aggregated = aggregate(weights_results)

        # ===== save =====
        with open("history/fedavg.json", "w", encoding="utf-8") as f:
            json.dump(self.history, f, indent=4)

        return ndarrays_to_parameters(aggregated), {}

    # ================= EVALUATE =================
    def aggregate_evaluate(self, server_round, results, failures):
        if not results:
            return None, {}

        accuracies = []
        losses = []

        for _, res in results:
            if res.metrics.get("accuracy") is not None:
                accuracies.append(res.metrics["accuracy"])
            losses.append(res.loss)

        if len(accuracies) == 0:
            return None, {}

        avg_acc = float(np.mean(accuracies))
        avg_loss = float(np.mean(losses))

        print(f"\n--- Round {server_round} ---")
        print(f"Accuracy: {avg_acc:.4f} | Loss: {avg_loss:.4f}")

        self.history["global"]["round"].append(server_round)
        self.history["global"]["accuracy"].append(avg_acc)
        self.history["global"]["loss"].append(avg_loss)

        if self.start_time:
            self.history["global"]["round_time"].append(time.time() - self.start_time)

        with open("history/fedavg.json", "w", encoding="utf-8") as f:
            json.dump(self.history, f, indent=4)

        return avg_loss, {"accuracy": avg_acc}