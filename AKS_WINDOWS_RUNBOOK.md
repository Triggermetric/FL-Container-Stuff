# AKS Windows Runbook

This guide is the shortest path to deploy the system on Azure AKS from Windows and get the result images back.

## 1. Prerequisites

- Azure CLI
- Helm
- PowerShell
- An Azure Container Registry
- An AKS cluster with the Azure File CSI driver available

If you do not have `kubectl` on Windows, use Azure Cloud Shell for the AKS checks and `kubectl` commands in this guide.

If Helm is missing on Windows, install it with:

```powershell
winget install --id Helm.Helm -e --accept-package-agreements --accept-source-agreements
```

Restart PowerShell after install if `helm` is not recognized immediately.

## 2. Create ACR And Push The Image

Use the same container image for the server, clients, and plot job.

```powershell
az login
az acr create -g <resourceGroup> -n <acrName> --sku Basic
az acr build -r <acrName> -t project-nt114:latest .
```

If your AKS cluster is not already attached to the ACR, attach it:

```powershell
az aks update -g <resourceGroup> -n <aksName> --attach-acr <acrName>
```

## 3. Create A Fresh AKS Cluster

If you want a clean test environment, create a new AKS cluster first and then deploy into it.

```powershell
az group create -n <resourceGroup> -l <region>
az aks create -g <resourceGroup> -n <aksName> --node-count 3 --generate-ssh-keys --attach-acr <acrName>
az aks get-credentials -g <resourceGroup> -n <aksName>
```

If you already have a cluster but want to start from zero, delete the old one first:

```powershell
az aks delete -g <resourceGroup> -n <aksName> --yes --no-wait
```

## 4. Edit Helm Values

Open [helm/nt114-fl/values-aks.yaml](helm/nt114-fl/values-aks.yaml) and replace:

- `YOUR_ACR_NAME.azurecr.io/project-nt114` with your real ACR image path
- `storage.className` if your AKS storage class is different

The default chart uses:

- 1 Ganache pod
- 1 IPFS pod
- 1 FL server job
- 5 FL client jobs
- 1 contract bootstrap job
- 1 optional plot job

## 5. Install The Stack

Run this from Windows PowerShell if Helm is installed locally. If you prefer, you can also run it from Azure Cloud Shell after the cluster credentials are available.

```powershell
helm upgrade --install nt114-fl helm/nt114-fl -n nt114-fl --create-namespace -f helm/nt114-fl/values-aks.yaml --wait --wait-for-jobs
```

This first install deploys the blockchain node, IPFS node, the contract bootstrap job, the server job, and the client jobs.

## 6. Know When Training Ends

If you do not have `kubectl` on Windows, run these checks in Azure Cloud Shell.

Training is finished when these resources show `Completed`:

- `job/reputation-deploy-*`
- `job/fl-server`
- `job/fl-client-1` through `job/fl-client-5`

Check them with:

```powershell
kubectl get jobs -n nt114-fl
kubectl logs job/fl-server -n nt114-fl
```

The server logs will print the round summaries. When the final round is done, the job exits and Kubernetes marks it `Completed`.

## 7. Generate The PNG Results

Run this the same way as the install step: Windows PowerShell if Helm is local, or Azure Cloud Shell if that is where you manage the cluster.

After training completes, run a second Helm upgrade to enable the plot job:

```powershell
helm upgrade nt114-fl helm/nt114-fl -n nt114-fl -f helm/nt114-fl/values-aks.yaml --reuse-values --set plot.enabled=true --wait --wait-for-jobs
```

This writes the images into the shared PVC at `/results/plots`.

## 8. Copy Results Back To Windows

Use the helper script:

```powershell
.\scripts\fetch-aks-results.ps1
```

The script copies the full `/results` tree to a local `aks-results` folder, including:

- `history/`
- `plots/`
- `runtime/`

If you are using Azure Cloud Shell, you can also use `kubectl cp` from there to download the files, but the PowerShell script is the easiest Windows path.

## 9. Delete Everything After Testing

Run `helm uninstall` from wherever you ran Helm originally. Run `az aks delete` from Windows PowerShell or Azure Cloud Shell.

When you are done testing on Azure, remove the Helm release and the cluster so you do not keep paying for resources.

```powershell
helm uninstall nt114-fl -n nt114-fl
az aks delete -g <resourceGroup> -n <aksName> --yes --no-wait
```

If you want to keep the cluster but remove only the app, use the Helm uninstall command only.

## 10. Why We Containerized It

Containerization makes the system easier to run, repeat, and debug because every part gets the same runtime environment.

For this project, that matters because:

- You can deploy the same stack on local Docker or AKS without changing the code.
- You can restart or kill one client pod to test fault tolerance.
- You can run poisoning tests by marking one client as faulty through `FAULTY_CLIENTS`.
- You can compare IID vs Non-IID runs with the same image and same deployment flow.
- You can measure overhead from Blockchain, ZKP, and IPFS in a controlled way.
- You can keep the generated JSON history and PNG plots in persistent storage and pull them back after the run.