# AKS Cloud Shell - Deployment and Results (Cloud Shell only)

Follow these commands exactly in **Azure Cloud Shell** (Bash). Replace the placeholder values shown in ALL_CAPS.

## Quick overview
- Creates an Azure Container Registry (ACR) and AKS cluster
- Builds & pushes the container image using `az acr build` (no local Docker needed)
- Deploys the Helm chart from the repo into AKS
- Waits for Jobs to complete, fetches `/results` (plots/history/runtime)
- Cleans up resources when finished

> Notes: run everything in Cloud Shell. You will need your Git repo reachable from Cloud Shell (HTTPS or SSH URL).

## Set variables
```bash
# Edit these before running
RG=nt114-rg
LOCATION=koreacentral
ACR_NAME=nt114acr$(date +%s | sed 's/[^0-9]//g' | tail -c6)
AKS_NAME=nt114-aks
NODE_COUNT=3
NODE_SIZE=Standard_DS2_v2
GIT_REPO_URL=https://github.com/YOUR_USER/YOUR_REPO.git
BRANCH=main
IMAGE_NAME=project-nt114
IMAGE_TAG=latest
NAMESPACE=nt114-fl
RESULTS_LOCAL_DIR=./nt114-results
```

## 1) Create resource group and ACR
```bash
az group create --name $RG --location $LOCATION
az acr create --resource-group $RG --name $ACR_NAME --sku Standard --admin-enabled false

# Get fully-qualified login server
ACR_LOGIN_SERVER=$(az acr show -n $ACR_NAME -g $RG --query "loginServer" -o tsv)
echo "ACR: $ACR_LOGIN_SERVER"
```

## 2) Create AKS and attach ACR
```bash
az aks create \
  --resource-group $RG \
  --name $AKS_NAME \
  --node-count $NODE_COUNT \
  --node-vm-size $NODE_SIZE \
  --generate-ssh-keys \
  --attach-acr $ACR_NAME \
  --enable-addons monitoring

# Configure kubectl context
az aks get-credentials --resource-group $RG --name $AKS_NAME
kubectl create namespace $NAMESPACE || true
```

## 3) Clone repo into Cloud Shell and build/push image using ACR build
```bash
git clone --branch $BRANCH $GIT_REPO_URL project-nt114 || (cd project-nt114 && git pull)
cd project-nt114

# Build & push using ACR (Cloud Shell uses Azure builder, no local Docker required)
az acr build --registry $ACR_NAME --image $IMAGE_NAME:$IMAGE_TAG .

# Full image ref
IMAGE_REF=$ACR_LOGIN_SERVER/$IMAGE_NAME:$IMAGE_TAG
echo "Image: $IMAGE_REF"
```

## 4) Configure Helm values and deploy (use values file or --set)

Option A — deploy using `values-aks.yaml` in the repo and override image:
```bash
helm repo update || true
helm upgrade --install nt114-fl helm/nt114-fl -n $NAMESPACE \
  -f helm/nt114-fl/values-aks.yaml \
  --set image.repository=$ACR_LOGIN_SERVER/$IMAGE_NAME \
  --set image.tag=$IMAGE_TAG
```

Option B — change `helm/nt114-fl/values-aks.yaml` (edit in Cloud Shell) to set `image.repository` and `image.tag` then run the same helm command without `--set`.

To inject faulty clients (poisoning tests) edit `helm/nt114-fl/values-aks.yaml` and set e.g. `faultyClients: "1,3"` or use `--set faultyClients="1,3"` with the `helm upgrade` command.

## 5) Wait for bootstrap, server and client jobs to finish
Use job completion as the signal training finished.

```bash
# Watch job status
kubectl get jobs -n $NAMESPACE

# Wait for all jobs in the namespace to complete (2-hour timeout per job)
for j in $(kubectl get jobs -n $NAMESPACE -o jsonpath='{.items[*].metadata.name}'); do
  echo "waiting for job: $j"
  kubectl wait --for=condition=complete job/$j -n $NAMESPACE --timeout=7200s || {
    echo "job $j failed or timed out; dumping logs..."
    kubectl logs job/$j -n $NAMESPACE --tail=200 || true
  }
done

# You can follow server logs live (replace job name if different):
kubectl logs job/fl-server -n $NAMESPACE --follow
```

How to know training ended: all server & client Jobs show `Completed` in `kubectl get jobs -n $NAMESPACE` and the plot job (if enabled) has completed and produced files under `/results/plots` in the shared PVC.

## 6) Fetch results (plots, history, runtime)
The chart writes results to the shared PVC at `/results`. Use kubectl cp to copy them to Cloud Shell.

```bash
# Find a pod that has the /results volume mounted (results-viewer or any job pod)
POD=$(kubectl get pods -n $NAMESPACE -o jsonpath='{.items[0].metadata.name}')
echo "Picking pod: $POD"

mkdir -p $RESULTS_LOCAL_DIR
kubectl cp -n $NAMESPACE $POD:/results $RESULTS_LOCAL_DIR || \
  echo "If copy fails, list files inside pods to locate /results and adjust pod name."

ls -la $RESULTS_LOCAL_DIR
```

If the chart creates a `results-viewer` Job/Pod, prefer that pod name instead of the generic one; use `kubectl get pods -n $NAMESPACE` to find the correct pod.

## 7) Teardown (delete Helm release, AKS, ACR)
Run when you are done with the experiment.

```bash
helm uninstall nt114-fl -n $NAMESPACE || true
kubectl delete namespace $NAMESPACE --ignore-not-found=true || true

# Delete AKS (this can take several minutes)
az aks delete --name $AKS_NAME --resource-group $RG --yes --no-wait

# Optionally delete ACR
az acr delete --name $ACR_NAME --resource-group $RG --yes

# Optionally delete resource group (deletes everything inside)
az group delete --name $RG --yes --no-wait
```

## Troubleshooting notes
- If `helm` is missing in Cloud Shell use: `curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash` (Cloud Shell usually has `helm`).
- If `az acr build` fails, ensure the repo root contains the `Dockerfile` and necessary files. Use `az acr login` and `docker build` locally as fallback.
- If Jobs restart repeatedly, check pod logs: `kubectl logs <pod> -n $NAMESPACE` and check the shared PVC mount path `/results/runtime` for `reputation-address.json` (contract bootstrap must complete first).

## Quick checklist (one-pass)
1. Open Cloud Shell (Bash)
2. Set variables at top of this file
3. Run steps 1 → 4
4. Monitor jobs (step 5) until Completed
5. Fetch results (step 6)
6. Tear down when done (step 7)

---
Edit `helm/nt114-fl/values-aks.yaml` to tune number of clients, IID vs non-IID dataset flags, and `faultyClients` before step 4 when you want to run experiments.
