import json
import matplotlib.pyplot as plt
import numpy as np
import os

IID_FILE = "history/server_history_fedadam_iid.json"
NONIID_FILE = "history/server_history_fedadam_non_iid.json"

SAVE_DIR = "plots/comparison"
os.makedirs(SAVE_DIR, exist_ok=True)

with open(IID_FILE, "r") as f:
    iid = json.load(f)

with open(NONIID_FILE, "r") as f:
    noniid = json.load(f)

rounds_iid = iid["global"]["round"]
rounds_noniid = noniid["global"]["round"]

plt.style.use("seaborn-v0_8-whitegrid")

plt.rcParams.update({
    "font.size": 12,
    "axes.labelweight": "bold",
    "axes.titleweight": "bold"
})

def compute_avg_local_accuracy(data):
    clients = data["clients"]
    rounds = data["global"]["round"]

    avg_acc = []

    for i in range(len(rounds)):
        accs = []

        for cid in clients:
            accs.append(clients[cid]["test_accuracy"][i])

        avg_acc.append(np.mean(accs))

    return avg_acc


def avg_train_time(data):

    times = []

    for cid in data["clients"]:
        times.extend(data["clients"][cid]["train_time"])

    return np.mean(times)


# ======================================================
# 1️⃣ GLOBAL ACCURACY COMPARISON
# ======================================================
plt.figure(figsize=(10,5))

plt.plot(rounds_iid, iid["global"]["accuracy"],
         marker="o", linewidth=2, label="IID")

plt.plot(rounds_noniid, noniid["global"]["accuracy"],
         marker="s", linewidth=2, label="Non-IID")

plt.title("Global Accuracy: IID vs Non-IID")
plt.xlabel("Communication Round")
plt.ylabel("Accuracy")
plt.ylim(0,1)

plt.legend(loc="upper left", bbox_to_anchor=(1.02, 1))
plt.tight_layout()

plt.savefig(f"{SAVE_DIR}/compare_global_accuracy.png", dpi=300)
plt.close()


# ======================================================
# 2️⃣ GLOBAL LOSS COMPARISON
# ======================================================
plt.figure(figsize=(10,5))

plt.plot(rounds_iid, iid["global"]["loss"],
         marker="o", linewidth=2, label="IID")

plt.plot(rounds_noniid, noniid["global"]["loss"],
         marker="s", linewidth=2, label="Non-IID")

plt.title("Global Loss: IID vs Non-IID")
plt.xlabel("Communication Round")
plt.ylabel("Loss")

plt.legend(loc="upper left", bbox_to_anchor=(1.02, 1))
plt.tight_layout()

plt.savefig(f"{SAVE_DIR}/compare_global_loss.png", dpi=300)
plt.close()

# ======================================================
# 3️⃣ ROUND TIME COMPARISON (Sửa để tránh KeyError)
# ======================================================
if "round_time" in iid["global"] and "round_time" in noniid["global"]:
    plt.figure(figsize=(8,5))
    plt.plot(rounds_iid, iid["global"]["round_time"], marker="o", linewidth=2, label="IID")
    plt.plot(rounds_noniid, noniid["global"]["round_time"], marker="s", linewidth=2, label="Non-IID")
    plt.title("Round Time Comparison")
    plt.xlabel("Communication Round")
    plt.ylabel("Round Time (seconds)")
    
    plt.legend(loc="upper left", bbox_to_anchor=(1.02, 1))
    plt.tight_layout()
    
    plt.savefig(f"{SAVE_DIR}/compare_round_time.png", dpi=300)
    plt.close()
else:
    print("⚠️ Bỏ qua biểu đồ 3: Một trong các file thiếu dữ liệu 'round_time'")

# ======================================================
# 4️⃣ TRAINING TIME COMPARISON
# ======================================================
iid_train = avg_train_time(iid)
noniid_train = avg_train_time(noniid)

plt.figure(figsize=(10,5))

labels = ["IID", "Non-IID"]
values = [iid_train, noniid_train]

plt.bar(labels, values)

plt.title("Average Client Training Time")
plt.ylabel("Seconds")

plt.legend(loc="upper left", bbox_to_anchor=(1.02, 1))
plt.tight_layout()

plt.savefig(f"{SAVE_DIR}/compare_train_time.png", dpi=300)
plt.close()

# ======================================================
# 5️⃣ AVERAGE REPUTATION PER ROUND
# ======================================================

def compute_avg_reputation(data):

    rounds = data["global"]["round"]
    clients = data["clients"]

    avg_rep = []

    for i in range(len(rounds)):

        reps = []

        for cid in clients:
            reps.append(clients[cid]["reputation"][i]["value"])

        avg_rep.append(np.mean(reps))

    return avg_rep


iid_rep = compute_avg_reputation(iid)
noniid_rep = compute_avg_reputation(noniid)

plt.figure(figsize=(10,5))

plt.plot(rounds_iid, iid_rep,
         marker="o", linewidth=2, label="IID")

plt.plot(rounds_noniid, noniid_rep,
         marker="s", linewidth=2, label="Non-IID")

plt.title("Average Client Reputation: IID vs Non-IID")
plt.xlabel("Communication Round")
plt.ylabel("Reputation Score")

plt.legend(loc="upper left", bbox_to_anchor=(1.02, 1))
plt.tight_layout()

plt.savefig(f"{SAVE_DIR}/compare_reputation.png", dpi=300)
plt.close()

# ======================================================
# 6️⃣ REPUTATION DISTRIBUTION ACROSS CLIENTS
# ======================================================

def collect_client_reputation(data):

    rep_per_client = []

    for cid in data["clients"]:
        reps = []

        for r in data["clients"][cid]["reputation"]:
            reps.append(r["value"])

        rep_per_client.append(reps)

    return rep_per_client

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6), sharey=True)
iid_rep_clients = collect_client_reputation(iid)
noniid_rep_clients = collect_client_reputation(noniid)

ax1.boxplot(iid_rep_clients)
ax1.set_title("Reputation Score Distribution (IID)", fontsize=14, fontweight='bold')
ax1.set_ylabel("Reputation Score")
ax1.set_xticklabels([f"Client {i+1}" for i in range(len(iid_rep_clients))], rotation=45)
ax1.grid(True, linestyle='--', alpha=0.6)

ax2.boxplot(noniid_rep_clients)
ax2.set_title("Reputation Score Distribution (Non-IID)", fontsize=14, fontweight='bold')
ax2.set_xticklabels([f"Client {i+1}" for i in range(len(noniid_rep_clients))], rotation=45)
ax2.grid(True, linestyle='--', alpha=0.6)

plt.tight_layout()

plt.savefig(f"{SAVE_DIR}/reputation_distribution_comparison.png", dpi=300)
plt.close()

#=======================================================
# 7️⃣ VALID UPDATE RATE vs REJECTED UPDATE RATE
#=======================================================

TOTAL_CLIENTS = 5

# IID
iid_penalty = iid["global"].get("penalty_clients", [])
iid_penalty_count = [len(p) for p in iid_penalty]

iid_rejected_rate = np.array(iid_penalty_count) / TOTAL_CLIENTS
iid_valid_rate = 1 - iid_rejected_rate

noniid_penalty = noniid["global"].get("penalty_clients", [])
noniid_penalty_count = [len(p) for p in noniid_penalty]

noniid_rejected_rate = np.array(noniid_penalty_count) / TOTAL_CLIENTS
noniid_valid_rate = 1 - noniid_rejected_rate


plt.figure(figsize=(10,5))

plt.plot(rounds_iid, iid_valid_rate,
         marker="o", linewidth=2, label="IID Valid Rate")

plt.plot(rounds_iid, iid_rejected_rate,
         marker="o", linestyle="--", label="IID Rejected Rate")

plt.plot(rounds_noniid, noniid_valid_rate,
         marker="s", linewidth=2, label="Non-IID Valid Rate")

plt.plot(rounds_noniid, noniid_rejected_rate,
         marker="s", linestyle="--", label="Non-IID Rejected Rate")


plt.title("Valid vs Rejected Update Rate")
plt.xlabel("Communication Round")
plt.ylabel("Rate")
plt.ylim(-0.05, 1.05)

plt.legend(loc="upper left", bbox_to_anchor=(1.02, 1))
plt.tight_layout()

plt.savefig(f"{SAVE_DIR}/compare_update_rate.png", dpi=300)
plt.close()

# ======================================================
# 8️⃣ MODEL CONVERGENCE SPEED
# ======================================================

def compute_accuracy_gain(acc_list):

    gains = [0]  # round 1 không có round trước

    for i in range(1, len(acc_list)):
        gains.append(acc_list[i] - acc_list[i-1])

    return gains


iid_gain = compute_accuracy_gain(iid["global"]["accuracy"])
noniid_gain = compute_accuracy_gain(noniid["global"]["accuracy"])


plt.figure(figsize=(10,5))

plt.plot(rounds_iid, iid_gain,
         marker="o", linewidth=2, label="IID")

plt.plot(rounds_noniid, noniid_gain,
         marker="s", linewidth=2, label="Non-IID")

plt.axhline(0, linestyle="--")  # đường tham chiếu

plt.title("Model Convergence Speed (Accuracy Gain per Round)")
plt.xlabel("Communication Round")
plt.ylabel("Accuracy Gain")

plt.legend(loc="upper left", bbox_to_anchor=(1.02, 1))
plt.tight_layout()

plt.savefig(f"{SAVE_DIR}/compare_convergence_speed.png", dpi=300)
plt.close()

print("✅ All comparison plots saved in:", SAVE_DIR)