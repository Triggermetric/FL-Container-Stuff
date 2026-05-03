import torch
from torch.utils.data import DataLoader, TensorDataset, random_split
import pickle
import numpy as np

CACHE = {}

def load_client_data(client_id, split_type="non_iid", batch_size=128):
    key = f"{split_type}_{client_id}"
    
    if key in CACHE:
        return CACHE[key]
    
    path = f"data_new/{split_type}/client_{client_id}.pkl"

    with open(path, "rb") as f:
        data = pickle.load(f)

    if isinstance(data, dict):
        X = np.array(data['images'], dtype=np.float32)
        y = data['labels']
    else:
        raise ValueError(f"{path} cần dict với key 'images' và 'labels'")

    if X.ndim == 2: 
        X = X.reshape(-1, 1, 28, 28)
    elif X.ndim == 3:  
        X = X[:, None, :, :]

    X = torch.from_numpy(X).float()

    if isinstance(y[0], str):
        y_processed = []
        for label in y:
            if label.isdigit():
                y_processed.append(int(label))
            else:
                y_processed.append(ord(label.lower()) - ord('a'))
        y = torch.tensor(y_processed, dtype=torch.long)
    else:
        y = torch.tensor(y, dtype=torch.long)

    dataset = TensorDataset(X, y)
    
    train_size = int(0.8 * len(dataset))
    test_size = len(dataset) - train_size
    generator = torch.Generator().manual_seed(42)
    
    train_dataset, test_dataset = random_split(
        dataset, 
        [train_size, test_size], 
        generator=generator
    )
    
    trainloader = DataLoader(
        train_dataset,
        batch_size=batch_size,
        shuffle=True,
        num_workers=4,
        persistent_workers=True,
        prefetch_factor=2 
    )
    
    testloader = DataLoader(
        test_dataset,
        batch_size=batch_size,
        shuffle=False,
        num_workers=4,
        persistent_workers=True,
        prefetch_factor=2 
    )
    
    CACHE[key] = (trainloader, testloader)
    return trainloader, testloader