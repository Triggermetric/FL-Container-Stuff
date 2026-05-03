# ================== evaluate.py ==================
import torch
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

def evaluate(model, testloader, criterion):
    model.eval()
    correct, total, loss = 0, 0, 0.0
    with torch.no_grad():
        for data, target in testloader:
            data, target = data.to(DEVICE), target.to(DEVICE)
            output = model(data)
            loss += criterion(output, target).item()
            pred = torch.argmax(output, dim=1)
            correct += (pred == target).sum().item()
            total += target.size(0)
    return {
        "loss": loss / len(testloader),
        "accuracy": correct / total
    }