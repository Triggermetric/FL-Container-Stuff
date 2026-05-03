import json
import matplotlib.pyplot as plt
import numpy as np
import os

# ==========================================
# CONFIG
# ==========================================
MODE = "iid"
BASIC_FILE = r"log\log_basic\fedavg_iid.json"
FULL_FILE  = r"log\log_full\server_history_fedadam_iid.json"

SAVE_DIR = f"picture/{MODE}/comparison_basic_full"
os.makedirs(SAVE_DIR, exist_ok=True)

# ==========================================
# LOAD DATA
# ==========================================
with open(BASIC_FILE, "r") as f:
    basic = json.load(f)

with open(FULL_FILE, "r") as f:
    full = json.load(f)

rounds_basic = basic["global"]["round"]
rounds_full = full["global"]["round"]

# ==========================================
# STYLE
# ==========================================
plt.style.use("seaborn-v0_8-whitegrid")

# ==========================================
# 1. GLOBAL ACCURACY
# ==========================================
plt.figure(figsize=(8,5))

plt.plot(rounds_basic, basic["global"]["accuracy"],
         marker="o", label="Basic FL")

plt.plot(rounds_full, full["global"]["accuracy"],
         marker="s", label="Secure FL")

plt.title("Global Test Accuracy: Basic FL vs Secure FL")
plt.xlabel("Round")
plt.ylabel("Accuracy")
plt.ylim(0, 1)
plt.legend()

plt.tight_layout()
plt.savefig(f"{SAVE_DIR}/accuracy.png", dpi=300)
plt.close()

# ==========================================
# 2. GLOBAL LOSS
# ==========================================
plt.figure(figsize=(8,5))

plt.plot(rounds_basic, basic["global"]["loss"],
         marker="o", label="Basic FL")

plt.plot(rounds_full, full["global"]["loss"],
         marker="s", label="Secure FL")

plt.title("Global Test Loss: Basic FL vs Secure FL")
plt.xlabel("Round")
plt.ylabel("Loss")

plt.legend()
plt.tight_layout()
plt.savefig(f"{SAVE_DIR}/loss.png", dpi=300)
plt.close()

# ==========================================
# 3. TRAIN TIME
# ==========================================
plt.figure(figsize=(6,5))

plt.bar(["Basic", "Full"],
        [np.mean(basic["global"]["round_time"]),
         np.mean(full["global"]["round_time"])])

plt.title("Average Training Time per Round")
plt.ylabel("Seconds")

plt.tight_layout()
plt.savefig(f"{SAVE_DIR}/train_time.png", dpi=300)
plt.close()

# ==========================================
# 4. CLIENT AVERAGE ACCURACY
# ==========================================
def avg_client_acc(data):
    clients = data["clients"]
    rounds = data["global"]["round"]

    result = []

    for i in range(len(rounds)):
        accs = [clients[c]["test_accuracy"][i] for c in clients]
        result.append(np.mean(accs))

    return result


basic_client = avg_client_acc(basic)
full_client = avg_client_acc(full)

plt.figure(figsize=(8,5))

plt.plot(rounds_basic, basic_client,
         marker="o", label="Basic")

plt.plot(rounds_full, full_client,
         marker="s", label="Full")

plt.title("Average Client Accuracy")
plt.xlabel("Round")
plt.ylabel("Accuracy")
plt.ylim(0,1)

plt.legend()
plt.tight_layout()
plt.savefig(f"{SAVE_DIR}/client_accuracy.png", dpi=300)
plt.close()

# ==========================================
print("Done -> saved in:", SAVE_DIR)