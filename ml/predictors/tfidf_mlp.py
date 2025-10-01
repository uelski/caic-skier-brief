from pathlib import Path
import json
import numpy as np
import torch

from ml.common.tokenization import load_vectorizer
from ml.models.tfidf_mlp import MLP  # your tuple-returning model class

class TfidfMLPPredictor:
    def __init__(self, artifacts_dir: str | Path | None = None, device: str | None = None):
        # 0) device first
        if device is None:
            device = "cuda" if torch.cuda.is_available() else "cpu"
        self.device = torch.device(device)

        self.art = Path(artifacts_dir) if artifacts_dir else Path(__file__).resolve().parents[1] / "artifacts"
        # load meta + vectorizer + model
        meta = json.loads((self.art / "tfidf_mlp_meta.json").read_text())
        self.vec = load_vectorizer(self.art / "tfidf.joblib")

        self.model = MLP(
            input_dim=meta["input_dim"],
            hidden=meta.get("hidden", 16),
            num_classes=meta["num_classes"],
            dropout=meta.get("dropout", 0.0),
        ).to(self.device)

        state = torch.load(self.art / "tfidf_mlp_model.pt", map_location="cpu")
        self.model.load_state_dict(state)
        self.model.eval()

    @torch.no_grad()
    def predict_one(self, text: str):
        X = self.vec.transform([text]).toarray().astype(np.float32)
        xb = torch.from_numpy(X)
        logits_b, logits_t, logits_a = self.model(xb)

        pb = torch.softmax(logits_b, dim=1)
        pt = torch.softmax(logits_t, dim=1)
        pa = torch.softmax(logits_a, dim=1)

        return {
            "below_treeline": int(pb.argmax(1).item()),
            "treeline":       int(pt.argmax(1).item()),
            "above_treeline": int(pa.argmax(1).item()),
            "scores": {
                "below_treeline": pb[0].tolist(),
                "treeline":       pt[0].tolist(),
                "above_treeline": pa[0].tolist(),
            },
            "model_id": "tfidf_mlp",
        }


def get_predictor(artifacts_dir: str | Path | None = None) -> TfidfMLPPredictor:
    return TfidfMLPPredictor(artifacts_dir)
