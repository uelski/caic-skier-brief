# ml/models/bert.py
import json
from pathlib import Path

import numpy as np
import torch, torch.nn as nn
from torch.utils.data import Dataset, DataLoader
import torch.optim as optim

from transformers import AutoTokenizer, AutoModel

from ml.common.processing import make_splits  # your JSON/splits utils

MODEL_NAME = "distilbert-base-uncased"
MAX_LEN = 256
VERSION = "v1"
NUM_CLASSES = 5  # labels 0..4

# ---------- Dataset ----------
class AvalancheTextDataset(Dataset):
    def __init__(self, texts, y_btl, y_tl, y_atl, tokenizer, max_len=MAX_LEN):
        enc = tokenizer(
            texts,
            truncation=True,
            padding="max_length",
            max_length=max_len,
            return_tensors="pt",
        )
        self.input_ids = enc["input_ids"]
        self.attn = enc["attention_mask"]
        self.yb = torch.as_tensor(y_btl, dtype=torch.long)
        self.yt = torch.as_tensor(y_tl, dtype=torch.long)
        self.ya = torch.as_tensor(y_atl, dtype=torch.long)

    def __len__(self): return self.input_ids.size(0)

    def __getitem__(self, idx):
        return (
            self.input_ids[idx],
            self.attn[idx],
            self.yb[idx],
            self.yt[idx],
            self.ya[idx],
        )

# ---------- Model (shared encoder + 3 heads) ----------
class BertThreeHead(nn.Module):
    def __init__(self, model_name=MODEL_NAME, num_classes=NUM_CLASSES, dropout=0.1):
        super().__init__()
        self.encoder = AutoModel.from_pretrained(model_name)
        H = self.encoder.config.hidden_size
        self.drop = nn.Dropout(dropout)
        self.head_b = nn.Linear(H, num_classes)
        self.head_t = nn.Linear(H, num_classes)
        self.head_a = nn.Linear(H, num_classes)

    def forward(self, input_ids, attention_mask):
        out = self.encoder(input_ids=input_ids, attention_mask=attention_mask)
        # use [CLS]-like token (token 0) for pooled rep
        h = self.drop(out.last_hidden_state[:, 0])
        return self.head_b(h), self.head_t(h), self.head_a(h)

def main():
    # ----- data -----
    splits = make_splits()  # uses your json + train_test_split
    Xtr, Xte = splits.X_train, splits.X_test
    ytr, yte = splits.y_train, splits.y_test

    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

    train_ds = AvalancheTextDataset(
        Xtr, ytr["btl"], ytr["tl"], ytr["atl"], tokenizer
    )
    test_ds = AvalancheTextDataset(
        Xte, yte["btl"], yte["tl"], yte["atl"], tokenizer
    )

    train_loader = DataLoader(train_ds, batch_size=16, shuffle=True, num_workers=2)
    test_loader  = DataLoader(test_ds,  batch_size=32, shuffle=False, num_workers=2)

    # ----- model / train -----
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = BertThreeHead().to(device)
    optimizer = optim.AdamW(model.parameters(), lr=2e-5)
    criterion = nn.CrossEntropyLoss()
    epochs = 3

    def run_epoch(loader, train=True):
        model.train() if train else model.eval()
        total_loss = 0.0
        cb = ct = ca = tot = 0
        ctx = torch.enable_grad() if train else torch.no_grad()
        with ctx:
            for input_ids, attn, yb, yt, ya in loader:
                input_ids = input_ids.to(device, non_blocking=True)
                attn = attn.to(device, non_blocking=True)
                yb, yt, ya = yb.to(device), yt.to(device), ya.to(device)

                if train: optimizer.zero_grad()
                lb, lt, la = model(input_ids, attn)
                loss = (criterion(lb, yb) + criterion(lt, yt) + criterion(la, ya)) / 3.0
                if train:
                    loss.backward()
                    optimizer.step()

                bs = input_ids.size(0)
                total_loss += loss.item() * bs
                cb += (lb.argmax(1) == yb).sum().item()
                ct += (lt.argmax(1) == yt).sum().item()
                ca += (la.argmax(1) == ya).sum().item()
                tot += bs

        return total_loss / max(tot, 1), cb / tot, ct / tot, ca / tot

    for e in range(1, epochs + 1):
        tl, tb, tt, ta = run_epoch(train_loader, True)
        vl, vb, vt, va = run_epoch(test_loader, False)
        print(f"Epoch {e:02d} | train_loss {tl:.4f} val_loss {vl:.4f} | "
              f"acc_b tl/va {tb:.3f}/{vb:.3f} | acc_t {tt:.3f}/{vt:.3f} | acc_a {ta:.3f}/{va:.3f}")

    # ----- artifacts -----
    project_root = Path(__file__).resolve().parents[2]
    artifacts_dir = project_root / "ml" / "artifacts" / "bert" / VERSION
    artifacts_dir.mkdir(parents=True, exist_ok=True)

    # weights
    torch.save(model.state_dict(), artifacts_dir / "bert_threehead.pt")

    # tokenizer + minimal config
    tokenizer.save_pretrained(artifacts_dir)  # writes vocab + tokenizer.json, etc.
    meta = {
        "model_name": MODEL_NAME,
        "max_length": MAX_LEN,
        "num_classes": NUM_CLASSES,
        "heads": ["btl", "tl", "atl"],
        "label2id": {"0":0,"1":1,"2":2,"3":3,"4":4},
        "id2label": {"0":"0","1":"1","2":"2","3":"3","4":"4"},
    }
    (artifacts_dir / "bert_meta.json").write_text(json.dumps(meta))

if __name__ == "__main__":
    main()
