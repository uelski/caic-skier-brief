import torch, torch.nn as nn
from torch.utils.data import Dataset, DataLoader
import torch.optim as optim
from pathlib import Path
import json, joblib
import numpy as np

from ml.common.processing import make_splits   # your renamed file
from ml.common.tokenization import fit_tfidf, transform_dense, save_vectorizer

# 1) data
splits = make_splits()
Xtr, Xte = splits.X_train, splits.X_test
ytr, yte = splits.y_train, splits.y_test  # dicts with 0..5 labels

# For clarity / later Dataset usage:
y_below_train    = ytr["btl"]
y_treeline_train = ytr["tl"]
y_above_train    = ytr["atl"]

y_below_test     = yte["btl"]
y_treeline_test  = yte["tl"]
y_above_test     = yte["atl"]

# 2) tf-idf → dense
vec = fit_tfidf(Xtr, max_features=10_000, ngram_range=(1, 2))
X_train_vec = transform_dense(vec, Xtr).astype(np.float32)  # (N_train, D)
X_test_vec  = transform_dense(vec, Xte).astype(np.float32)  # (N_test,  D)
D = X_train_vec.shape[1]

# Save the fitted vectorizer for inference
from pathlib import Path
project_root = Path(__file__).resolve().parents[2]   # from ml/models/... up to repo root
artifacts_dir = project_root / "ml" / "artifacts"
artifacts_dir.mkdir(parents=True, exist_ok=True)
save_vectorizer(vec, str(artifacts_dir / "tfidf.joblib"))

# 3) tiny MLP (3 heads)
class MLP(nn.Module):
    def __init__(self, input_dim, hidden=16, num_classes=6, dropout=0.0):
        super().__init__()
        self.shared = nn.Sequential(
            nn.Linear(input_dim, hidden),
            nn.ReLU(),
            nn.Linear(hidden, hidden),
            nn.ReLU(),
            nn.Dropout(dropout)
        )
        self.head_below    = nn.Linear(hidden, num_classes)
        self.head_treeline = nn.Linear(hidden, num_classes)
        self.head_above    = nn.Linear(hidden, num_classes)

    def forward(self, x):
        z = self.shared(x)
        return (
            self.head_below(z),     # logits_below
            self.head_treeline(z),  # logits_treeline
            self.head_above(z)      # logits_above
        )

model = MLP(D)

# define dataset class and loaders
class AvalancheDataset(Dataset):
    def __init__(self, X, y_below, y_treeline, y_above):
        self.X  = torch.as_tensor(X, dtype=torch.float32)   # (N, D)
        self.yb = torch.as_tensor(y_below, dtype=torch.long)  # (N,)
        self.yt = torch.as_tensor(y_treeline, dtype=torch.long)
        self.ya = torch.as_tensor(y_above, dtype=torch.long)

    def __len__(self):
        return self.X.shape[0]

    def __getitem__(self, idx):
        return self.X[idx], self.yb[idx], self.yt[idx], self.ya[idx]

train_ds = AvalancheDataset(X_train_vec, y_below_train, y_treeline_train, y_above_train)
test_ds  = AvalancheDataset(X_test_vec,  y_below_test,  y_treeline_test,  y_above_test)

train_loader = DataLoader(train_ds, batch_size=64, shuffle=True,  pin_memory=True, num_workers=2, drop_last=False)
test_loader  = DataLoader(test_ds,  batch_size=64, shuffle=False, pin_memory=True, num_workers=2, drop_last=False)

# training
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)

optimizer = optim.Adam(model.parameters(), lr=1e-3)
criterion = nn.CrossEntropyLoss()   # labels must be torch.long in 0..(C-1)
epochs = 20

def run_epoch(loader, train=True):
    model.train() if train else model.eval()
    total_loss = 0.0
    correct_b = correct_t = correct_a = 0
    total = 0

    ctx = torch.enable_grad() if train else torch.no_grad()
    with ctx:
        for X, yb, yt, ya in loader:
            X  = X.to(device, non_blocking=True)
            yb = yb.to(device, non_blocking=True)
            yt = yt.to(device, non_blocking=True)
            ya = ya.to(device, non_blocking=True)

            if train:
                optimizer.zero_grad()

            # ⬇️ tuple of logits for (below, treeline, above)
            logits_b, logits_t, logits_a = model(X)

            loss_b = criterion(logits_b, yb)
            loss_t = criterion(logits_t, yt)
            loss_a = criterion(logits_a, ya)
            loss = (loss_b + loss_t + loss_a) / 3.0

            if train:
                loss.backward()
                optimizer.step()

            bs = X.size(0)
            total_loss += loss.item() * bs

            # accuracies
            pred_b = logits_b.argmax(dim=1)
            pred_t = logits_t.argmax(dim=1)
            pred_a = logits_a.argmax(dim=1)
            correct_b += (pred_b == yb).sum().item()
            correct_t += (pred_t == yt).sum().item()
            correct_a += (pred_a == ya).sum().item()
            total += bs

    avg_loss = total_loss / total
    return avg_loss, correct_b/total, correct_t/total, correct_a/total

for epoch in range(1, epochs + 1):
    tloss, tacc_b, tacc_t, tacc_a = run_epoch(train_loader, train=True)
    vloss, vacc_b, vacc_t, vacc_a = run_epoch(test_loader,  train=False)
    print(
        f"Epoch {epoch:02d} | "
        f"train_loss={tloss:.4f}  val_loss={vloss:.4f} | "
        f"acc_below: tr={tacc_b:.3f} va={vacc_b:.3f} | "
        f"acc_treeline: tr={tacc_t:.3f} va={vacc_t:.3f} | "
        f"acc_above: tr={tacc_a:.3f} va={vacc_a:.3f}"
    )

# save model weights
torch.save(model.state_dict(), "ml/artifacts/tfidf_mlp_model.pt")

# save minimal metadata needed to rebuild the model
D = X_train_vec.shape[1]                       # input dim used to build the model
num_classes = model.btl.out_features          # or model.head_btl.out_features
meta = {
    "input_dim": int(D),
    "num_classes": int(num_classes),
    "tfidf": {"max_features": 10_000, "ngram_range": [1, 2]},
}
(artifacts_dir / "tfidf_mlp_meta.json").write_text(json.dumps(meta))
