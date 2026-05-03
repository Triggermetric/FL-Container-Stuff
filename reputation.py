import json
import os
import numpy as np

REPUTATION_FILE = "reputation.json"
INITIAL_REPUTATION = 0.5

# ================= LOAD / SAVE =================
def load_reputation():
    if not os.path.exists(REPUTATION_FILE):
        return {}
    with open(REPUTATION_FILE, "r") as f:
        try:
            return json.load(f)
        except:
            return {}

def save_reputation(rep_dict):
    with open(REPUTATION_FILE, "w") as f:
        json.dump(rep_dict, f, indent=4)

# ================= MATH UTILS =================
def flatten_weights(weights):
    return np.concatenate([w.flatten() for w in weights])

def compute_delta(global_weights, local_weights):
    gw = flatten_weights(global_weights)
    lw = flatten_weights(local_weights)
    return np.linalg.norm(lw - gw) / (np.linalg.norm(gw) + 1e-10)

def cosine_similarity(global_weights, local_weights):
    gw = flatten_weights(global_weights)
    lw = flatten_weights(local_weights)
    return np.dot(gw, lw) / ((np.linalg.norm(gw) * np.linalg.norm(lw)) + 1e-10)

def compute_quartiles(values):
    if not values: return 0, 0, 0, 0
    Q1 = np.percentile(values, 25)
    Q3 = np.percentile(values, 75)
    IQR = Q3 - Q1
    return Q1, Q3, Q1 - 1.5 * IQR, Q3 + 1.5 * IQR

# ================= REPUTATION CORE =================
def update_reputation(client_id, score):
    rep_dict = load_reputation()
    cid = str(client_id)

    old_rep = float(rep_dict.get(cid, INITIAL_REPUTATION))
    
    lr = 0.3 
    
    new_rep = old_rep + lr * (score - old_rep)
    new_rep = float(np.clip(new_rep, 0.1, 1.0))

    rep_dict[cid] = new_rep
    save_reputation(rep_dict)
    return new_rep

# ================= EVALUATION =================
def evaluate_clients(global_weights, client_weights_dict, clients_info, rejected_clients=None):
    delta_dict = {}
    sim_dict = {}

    for cid, weights in client_weights_dict.items():
        delta_dict[cid] = compute_delta(global_weights, weights)
        sim_dict[cid] = cosine_similarity(global_weights, weights)

    deltas = list(delta_dict.values())
    accs = [info["test_acc"] for info in clients_info]
    losses = [info["test_loss"] for info in clients_info]

    Q1, Q3, lower, upper = compute_quartiles(deltas)
    mean_delta = np.mean(deltas) + 1e-8
    max_acc, min_acc = max(accs), min(accs)
    max_loss, min_loss = max(losses), min(losses)

    results = {}

    for i, info in enumerate(clients_info):
        cid = info["client_id"]
        delta = delta_dict[cid]
        sim = sim_dict[cid]
        
        score_sim = sim
        norm_delta = min(delta / mean_delta, 3.0)
        score_delta = 1.0 - (norm_delta / 3.0)
        
        acc_norm = (info["test_acc"] - min_acc) / (max_acc - min_acc + 1e-8)
        loss_norm = (info["test_loss"] - min_loss) / (max_loss - min_loss + 1e-8)
        
        combined_score = (0.4 * score_sim) + (0.3 * score_delta) + (0.3 * acc_norm) - (0.2 * loss_norm)
        
        status = "normal"
        if sim < 0.1 or (rejected_clients and str(cid) in rejected_clients):
            combined_score = -1.0
            status = "rejected"
        elif delta < lower or delta > upper:
            combined_score -= 0.2
            status = "outlier"
            
        final_score = max(-1.0, min(1.0, combined_score))
        reputation = update_reputation(cid, final_score)

        print(f"[Client {cid}] Δ={delta:.4f} | Sim={sim:.4f} | Score={final_score:.4f} | Rep={reputation:.4f} | {status}")

        results[cid] = {
            "delta": float(delta),
            "similarity": float(sim),
            "score": float(final_score),
            "status": status,
            "reputation": reputation
        }

    return results, Q1, Q3