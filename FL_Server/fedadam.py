import numpy as np
from FL_Server.config import LR, BETA1, BETA2, EPS

class FedAdamState:

    def __init__(self):
        self.m = None
        self.v = None
        self.t = 0


fedadam = FedAdamState()


def fedadam_update(global_weights, gradients):

    fedadam.t += 1

    if fedadam.m is None:
        fedadam.m = [np.zeros_like(x) for x in gradients]
        fedadam.v = [np.zeros_like(x) for x in gradients]

    new_weights = []

    for i in range(len(gradients)):
        g = gradients[i]
        g = np.clip(g, -1.0, 1.0)

        fedadam.m[i] = BETA1 * fedadam.m[i] + (1 - BETA1) * g
        fedadam.v[i] = BETA2 * fedadam.v[i] + (1 - BETA2) * (g ** 2)

        m_hat = fedadam.m[i] / (1 - BETA1 ** fedadam.t)
        v_hat = fedadam.v[i] / (1 - BETA2 ** fedadam.t)

        new_w = global_weights[i] + LR * m_hat / (np.sqrt(v_hat) + EPS)

        new_weights.append(new_w)

    return new_weights