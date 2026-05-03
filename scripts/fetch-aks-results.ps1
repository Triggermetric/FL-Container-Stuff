param(
    [string]$Namespace = "nt114-fl",
    [string]$OutputDir = ".\aks-results"
)

$pod = kubectl get pod -n $Namespace -l app=results-viewer -o jsonpath='{.items[0].metadata.name}'

if (-not $pod) {
    throw "results-viewer pod not found in namespace $Namespace"
}

New-Item -ItemType Directory -Force -Path $OutputDir | Out-Null

kubectl cp -n $Namespace "$pod:/results" $OutputDir

Write-Host "Results copied to $OutputDir\results"