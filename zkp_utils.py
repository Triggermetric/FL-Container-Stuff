import hashlib
import numpy as np


def hash_model(parameters):

    m = hashlib.sha256()

    for p in parameters:
        m.update(p.tobytes())

    return m.hexdigest()


def generate_proof(parameters):

    model_hash = hash_model(parameters)

    proof = {
        "hash": model_hash
    }

    return proof


def verify_proof(parameters, proof):

    if proof is None:
        return False

    if not isinstance(proof, dict):
        return False

    if "hash" not in proof:
        return False

    server_hash = hash_model(parameters)

    return server_hash == proof["hash"]
