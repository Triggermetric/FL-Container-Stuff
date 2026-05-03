import json
import os
import time
from pathlib import Path

from web3 import Web3


ROOT = Path(__file__).resolve().parent
ARTIFACT_PATH = Path(os.getenv("CONTRACT_ARTIFACT", ROOT / "build/contracts/Reputation.json"))
ADDRESS_FILE = Path(os.getenv("CONTRACT_ADDRESS_FILE", ROOT / "runtime/reputation-address.json"))
WEB3_PROVIDER_URI = os.getenv("WEB3_PROVIDER_URI", "http://127.0.0.1:7545")


def main():
    with open(ARTIFACT_PATH, "r", encoding="utf-8") as f:
        artifact = json.load(f)

    w3 = Web3(Web3.HTTPProvider(WEB3_PROVIDER_URI))

    last_error = None
    for _ in range(30):
        try:
            if w3.is_connected() and w3.eth.accounts:
                break
        except Exception as error:
            last_error = error
        time.sleep(2)
    else:
        raise RuntimeError(f"Unable to connect to Ethereum provider: {WEB3_PROVIDER_URI}") from last_error

    contract = w3.eth.contract(abi=artifact["abi"], bytecode=artifact["bytecode"])
    account = w3.eth.accounts[0]

    tx_hash = contract.constructor().transact({"from": account})
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

    ADDRESS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(ADDRESS_FILE, "w", encoding="utf-8") as f:
        json.dump(
            {
                "address": receipt.contractAddress,
                "provider": WEB3_PROVIDER_URI,
                "artifact": str(ARTIFACT_PATH),
            },
            f,
            indent=2,
        )

    print(f"Deployed Reputation contract at {receipt.contractAddress}")
    print(f"Saved runtime address file to {ADDRESS_FILE}")


if __name__ == "__main__":
    main()