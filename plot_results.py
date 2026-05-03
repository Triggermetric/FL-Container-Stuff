import json
import matplotlib.pyplot as plt
import os
import numpy as np

MODE = os.getenv("MODE", "non_iid")
RESULTS_DIR = os.getenv("RESULTS_DIR", ".")
SAVE_DIR = os.getenv("PLOTS_DIR", os.path.join(RESULTS_DIR, "plots", MODE))

os.makedirs(SAVE_DIR, exist_ok=True)

history_candidates = [
    os.path.join(RESULTS_DIR, "history", "server_history_fedadam_non_iid.json"),
    os.path.join(RESULTS_DIR, "history", "server_history_fedadam.json"),
    "history/server_history_fedadam_non_iid.json",
    "history/server_history_fedadam.json",
]

for history_path in history_candidates:
    if os.path.exists(history_path):
        with open(history_path, "r") as f:
            history = json.load(f)
        break
else:
    raise FileNotFoundError(
        "No server history file found. Expected one of: " + ", ".join(history_candidates)
    )

global_data = history["global"]
clients_data = history["clients"]

rounds = global_data["round"]

plt.style.use("seaborn-v0_8-whitegrid")

def align_xy(x, y):
    n = min(len(x), len(y))
    return x[:n], y[:n]

# ==============================
# 1️⃣ Train Time per Client
# ==============================
plt.figure(figsize=(8,5))
lines = []
labels = []

for cid, data in clients_data.items():

    x, y = align_xy(data["round"], data["train_time"])

    line, = plt.plot(x, y, marker="o")
    lines.append(line)
    labels.append(f"Client {cid}")

plt.title("Training Time per Client")
plt.xlabel("Communication Round")
plt.ylabel("Training Time (seconds)")

plt.legend(lines, labels)
plt.tight_layout()
plt.savefig(f"{SAVE_DIR}/train_time.png", dpi=300)
plt.close()

# ==============================
# 2️⃣ Local Test Accuracy
# ==============================
plt.figure(figsize=(8,5))

lines = []
labels = []

for cid in sorted(clients_data.keys(), key=lambda x: int(x)):
    data = clients_data[cid]

    x, y = align_xy(data["round"], data["test_accuracy"])

    line, = plt.plot(x, y, marker="o")
    lines.append(line)
    labels.append(f"Client {cid}")

plt.title("Local Test Accuracy per Client")
plt.xlabel("Communication Round")
plt.ylabel("Accuracy")
plt.ylim(0,1)

plt.legend(lines, labels)

plt.tight_layout()
plt.savefig(f"{SAVE_DIR}/local_accuracy.png", dpi=300)
plt.close()

# ==============================
# 3️⃣ Loss Comparison
# ==============================
plt.figure(figsize=(8,5))

line_global, = plt.plot(
    rounds,
    global_data["loss"],
    linewidth=3,
    label="Global Loss"
)

lines = [line_global]
labels = ["Global Loss"]

for cid in sorted(clients_data.keys(), key=lambda x: int(x)):
    data = clients_data[cid]
    x, y = align_xy(data["round"], data["test_loss"])

    line, = plt.plot(
        x,
        y,
        linestyle="--",
        alpha=0.7
    )

    lines.append(line)
    labels.append(f"Client {cid}")

plt.title("Loss Comparison (Global vs Clients)")
plt.xlabel("Communication Round")
plt.ylabel("Loss")

plt.legend(lines, labels)

plt.tight_layout()
plt.savefig(f"{SAVE_DIR}/loss_comparison.png", dpi=300)
plt.close()

# ==============================
# 4️⃣ Accuracy Comparison
# ==============================
plt.figure(figsize=(8,5))

line_global, = plt.plot(
    rounds,
    global_data["accuracy"],
    linewidth=3
)

lines = [line_global]
labels = ["Global Accuracy"]

for cid in sorted(clients_data.keys(), key=lambda x: int(x)):
    data = clients_data[cid]
    x, y = align_xy(data["round"], data["test_accuracy"])

    line, = plt.plot(
        x,
        y,
        linestyle="--",
        alpha=0.7
    )

    lines.append(line)
    labels.append(f"Client {cid}")

plt.title("Accuracy Comparison (Global vs Clients)")
plt.xlabel("Communication Round")
plt.ylabel("Accuracy")

plt.legend(lines, labels)

plt.tight_layout()
plt.savefig(f"{SAVE_DIR}/accuracy_comparison.png", dpi=300)
plt.close()

# ==============================
# 5️⃣ Rejected Clients (Line Plot - Clean)
# ==============================
rejected = global_data.get("penalty_clients", [])
TOTAL_CLIENTS = len(clients_data)

if len(rejected) > 0:

    x = []
    rejected_rate = []
    valid_rate = []

    for i, round_clients in enumerate(rejected):

        r_rate = len(round_clients) / TOTAL_CLIENTS
        v_rate = 1 - r_rate

        x.append(i + 1)
        rejected_rate.append(r_rate)
        valid_rate.append(v_rate)

    plt.figure(figsize=(9,5))

    plt.plot(x, valid_rate, marker='o', linewidth=2, label="Valid Update Rate")
    plt.plot(x, rejected_rate, marker='o', linewidth=2, label="Rejected Update Rate")

    plt.title("Valid vs Rejected Update Rate per Round", fontsize=14, fontweight='bold')
    plt.xlabel("Communication Round")
    plt.ylabel("Rate")

    plt.ylim(0,1)
    plt.yticks(np.arange(-0.1,1.1,0.1))

    plt.grid(axis='y', linestyle='--', alpha=0.6)

    plt.legend(loc="upper left", bbox_to_anchor=(1,1))

    plt.tight_layout()
    plt.savefig(f"{SAVE_DIR}/rejected_clients.png", dpi=300)
    plt.close()
    
# ==============================
# 6️⃣ Global Accuracy + Loss
# ==============================
plt.figure(figsize=(8,5))

plt.plot(rounds, global_data["accuracy"], marker="o", label="Accuracy")
plt.plot(rounds, global_data["loss"], marker="s", label="Loss")

plt.title("Global Model Performance")
plt.xlabel("Communication Round")

plt.legend()

plt.tight_layout()
plt.savefig(f"{SAVE_DIR}/global_performance.png", dpi=300)
plt.close()

# ==============================
# 7️⃣ Client Reputation
# ==============================
plt.figure(figsize=(8,5))
lines = []
labels = []

for cid, data in clients_data.items():

    if "reputation" not in data:
        continue

    r_rounds = []
    r_values = []

    for r in data["reputation"]:
        r_rounds.append(r["round"])
        r_values.append(r["value"])

    line, = plt.plot(r_rounds, r_values, marker="o", label=f"Client {cid}")
    lines.append(line)
    labels.append(f"Client {cid}")

plt.title("Client Reputation Evolution")
plt.xlabel("Communication Round")
plt.ylabel("Reputation Score")

plt.legend(lines, labels)
plt.tight_layout()
plt.savefig(f"{SAVE_DIR}/client_reputation.png", dpi=300)
plt.close()

# ==============================
# 8️⃣ Convergence Speed
# ==============================

acc = global_data["accuracy"]

# tốc độ thay đổi accuracy giữa các round
convergence_speed = np.diff(acc)

rounds_conv = rounds[1:len(convergence_speed)+1]

plt.figure(figsize=(8,5))

plt.plot(rounds_conv, convergence_speed, marker="o", linewidth=2)

plt.title("Model Convergence Speed")
plt.xlabel("Communication Round")
plt.ylabel("Accuracy Improvement")

plt.axhline(0, linestyle="--", linewidth=1)

plt.tight_layout()
plt.savefig(f"{SAVE_DIR}/convergence_speed.png", dpi=300)
plt.close()

print(f"\n✅ All plots saved in folder: {SAVE_DIR}")