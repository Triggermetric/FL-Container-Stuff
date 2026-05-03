import numpy as np
from FL_Server.config import LAMBDA_DEFENSE

def flatten_weights(weights):
    return np.concatenate([w.flatten() for w in weights])

def compute_delta(global_weights, local_weights):
    gw = flatten_weights(global_weights)
    lw = flatten_weights(local_weights)
    delta = np.linalg.norm(lw - gw) / (np.linalg.norm(gw) + 1e-10)
    return delta

def cosine_similarity(global_weights, local_weights):
    gw = flatten_weights(global_weights)
    lw = flatten_weights(local_weights)
    return np.dot(gw, lw) / ((np.linalg.norm(gw) * np.linalg.norm(lw)) + 1e-10)

def defense_scaling(delta, lambda_defense=0.05):
    gamma = 1 / (1 + np.exp(lambda_defense * (delta - 1.0)))  # sigmoid
    return np.clip(gamma, 0.05, 1.0)