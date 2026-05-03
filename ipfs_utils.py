import os
import time

import ipfshttpclient


def upload_to_ipfs(file_path):

    try:

        api_addr = os.getenv("IPFS_API_ADDR", "/ip4/127.0.0.1/tcp/5001")
        last_error = None

        for _ in range(30):
            try:
                client = ipfshttpclient.connect(api_addr)
                break
            except Exception as error:
                last_error = error
                time.sleep(2)
        else:
            raise RuntimeError(f"Unable to connect to IPFS at {api_addr}") from last_error

        res = client.add(file_path)

        cid = res["Hash"]

        print(f"📦 Uploaded {file_path} -> CID: {cid}")

        return cid

    except Exception as e:

        print("❌ IPFS Upload Failed:", e)

        return "IPFS_ERROR"