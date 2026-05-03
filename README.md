# Federated Learning dựa trên Blockchain với cơ chế điều chỉnh trọng số và bảo mật ZKP

Dự án nghiên cứu và xây dựng kiến trúc học liên kết (Federated Learning) an toàn, phi tập trung, tích hợp công nghệ Blockchain và bằng chứng không tiết lộ (Zero-Knowledge Proof) nhằm bảo vệ quyền riêng tư và chống tấn công độc hại.

---

## Tổng quan
Trong kỷ nguyên chuyển đổi số, việc huấn luyện mô hình trên dữ liệu lớn vấp phải rào cản về bảo mật dữ liệu cá nhân. Hệ thống này giải quyết các lỗ hổng của FL truyền thống như:
* **Nguy cơ tấn công:** Poisoning attacks và backdoor.

Nếu muốn đi theo Helm, dùng chart trong [helm/nt114-fl](helm/nt114-fl). Chart này tạo namespace, ACR-backed deployments cho Ganache/IPFS/server/clients, job bootstrap contract, và một PVC dùng chung để giữ history/plots/runtime.
* **Thiếu minh bạch:** Sự phụ thuộc vào một máy chủ trung tâm không đáng tin cậy.
Luồng triển khai bằng Helm:

1. Build và push image lên ACR, rồi thay `YOUR_ACR_NAME.azurecr.io/project-nt114:latest` trong [helm/nt114-fl/values.yaml](helm/nt114-fl/values.yaml).
2. Cài chart:

helm upgrade --install nt114-fl helm/nt114-fl -n nt114-fl --create-namespace --wait --wait-for-jobs
2. **Decentralized Storage Layer (IPFS):**
3. Khi training xong, bật job sinh ảnh bằng một upgrade:
   * Trả về mã băm định danh nội dung (CID) để tham chiếu.
helm upgrade nt114-fl helm/nt114-fl -n nt114-fl --reuse-values --set plot.enabled=true --wait --wait-for-jobs
   * **Smart Contract** đóng vai trò là bộ xác thực ZK Verifier và thực thi cơ chế thưởng - phạt.
4. Copy ảnh và history về máy:
   * Tổng hợp các bản cập nhật đã qua xác thực để tạo mô hình toàn cục (Global Model).
.\scripts\fetch-aks-results.ps1
* **Zero-Knowledge Proof (ZKP):** Chứng minh tính hợp lệ của cập nhật mà không làm lộ tham số nhạy cảm hoặc dữ liệu gốc.

Azure-specific setup:

1. Create or reuse an ACR and attach it to AKS so image pulls work without imagePullSecrets.
2. Make sure the AKS cluster has the Azure File CSI driver enabled, because the chart uses `azurefile-csi` for RWX storage.
3. If you want to test poisoning, set `fl.faultyClients` in the Helm values, for example `--set fl.faultyClients=3`.

To inspect the shared results directly in-cluster, use the `results-viewer` pod and `kubectl cp` from `/results`.

If you prefer the raw YAML approach, the [k8s](k8s) folder is still there, but Helm is the recommended path now.

2. Deploy contract một lần để tạo file địa chỉ runtime:
```bash
docker compose --profile bootstrap run --rm contract-init
```

3. Chạy hệ thống federated learning:
```bash
docker compose up --build fl-server client-1 client-2 client-3 client-4 client-5
```

4. Muốn test client độc hại, đặt `FAULTY_CLIENTS=3` trước khi chạy compose. Ví dụ:
```powershell
$env:FAULTY_CLIENTS="3"
docker compose up --build fl-server client-1 client-2 client-3 client-4 client-5
```

## Ý nghĩa container hóa

Container hóa giúp tách biệt từng thành phần, tái lập thí nghiệm ổn định, dễ scale số client, và kiểm thử các tình huống như tắt một client, poison một client, so sánh IID/Non-IID, cũng như đo overhead giữa FL cơ bản và FL có Blockchain, ZKP, IPFS.

## Deploy To AKS

The Helm chart lives in [helm/nt114-fl](helm/nt114-fl). It creates the namespace, the AKS-friendly shared volume for `history/`, `plots/`, and the contract runtime file, plus Ganache, IPFS, the FL server, the 5 clients, and a results viewer pod.

1. Build and push your image to ACR, then update `YOUR_ACR_NAME.azurecr.io/project-nt114:latest` in [helm/nt114-fl/values-aks.yaml](helm/nt114-fl/values-aks.yaml).
2. Install the chart:
```bash
helm upgrade --install nt114-fl helm/nt114-fl -n nt114-fl --create-namespace -f helm/nt114-fl/values-aks.yaml --wait --wait-for-jobs
```
3. After training finishes, enable plot generation and upgrade once more:
```bash
helm upgrade nt114-fl helm/nt114-fl -n nt114-fl -f helm/nt114-fl/values-aks.yaml --reuse-values --set plot.enabled=true --wait --wait-for-jobs
```
4. Pull the results back to your PC:
```powershell
.\scripts\fetch-aks-results.ps1
```

If you want to inspect the shared results directly inside the cluster, the [results viewer](helm/nt114-fl/templates/results-viewer.yaml) keeps the PVC mounted at `/results`, so `kubectl exec` or `kubectl cp` works immediately.

### How to know training ended

Training ends when the `fl-server` job completes successfully and the client jobs also show `Completed`.

Useful checks:

```powershell
kubectl get jobs -n nt114-fl
kubectl get pods -n nt114-fl
kubectl logs job/fl-server -n nt114-fl
```

What you want to see:

- `fl-server` job: `Completed`
- `fl-client-1` to `fl-client-5`: `Completed`
- `reputation-deploy-*`: `Completed`
- `plot-results-*`: `Completed` after you enable plot generation

When those finish, the PNGs are already on the shared PVC under `/results/plots/...`, and the history JSON is under `/results/history/...`.



