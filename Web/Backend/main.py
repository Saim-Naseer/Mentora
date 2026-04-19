# main.py
import torch
import torch.nn.functional as F
from fastapi import FastAPI
from pydantic import BaseModel
from transformers import AutoTokenizer
from model import TwoTowerModel  
from dotenv import load_dotenv
import os
load_dotenv()

HF_TOKEN = os.getenv("HF_TOKEN")

device = "cuda" if torch.cuda.is_available() else "cpu"
app = FastAPI()
model_name = "sentence-transformers/all-MiniLM-L6-v2"
from transformers import AutoTokenizer

tokenizer = AutoTokenizer.from_pretrained(
    model_name,
    token=HF_TOKEN
)

tokenizer = AutoTokenizer.from_pretrained(model_name)

def mean_pooling(model_output, attention_mask):
    token_embeddings = model_output.last_hidden_state
    mask = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
    return torch.sum(token_embeddings * mask, dim=1) / torch.clamp(mask.sum(dim=1), min=1e-9)

class ProjectionHead(nn.Module):
    def __init__(self, input_dim=384, output_dim=128):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(input_dim, 256),
            nn.ReLU(),
            nn.Linear(256, output_dim)
        )

    def forward(self, x):
        return self.net(x)
    
class TwoTowerModel(nn.Module):
    def __init__(self):
        super().__init__()
        self.user_encoder = user_encoder
        self.uni_encoder = uni_encoder
        self.user_proj = ProjectionHead()
        self.uni_proj = ProjectionHead()

    def encode_user(self, input_ids, attention_mask, **kwargs):
        output = self.user_encoder(input_ids=input_ids, attention_mask=attention_mask)
        pooled = mean_pooling(output, attention_mask)
        return self.user_proj(pooled)

    def encode_uni(self, input_ids, attention_mask, **kwargs):
        output = self.uni_encoder(input_ids=input_ids, attention_mask=attention_mask)
        pooled = mean_pooling(output, attention_mask)
        return self.uni_proj(pooled)

model = TwoTowerModel().to(device)

model.load_state_dict(torch.load("model.pth", map_location=device))
model.eval()

data = torch.load("uni_embeddings.pt", map_location=device)
uni_names = data["uni_names"]
uni_embeddings = data["uni_embeddings"].to(device)


class StudentRequest(BaseModel):
    text: str
    top_k: int = 10


@app.post("/recommend")
def recommend(req: StudentRequest):
    # Tokenize input
    tokens = tokenizer([req.text], padding=True, truncation=True, return_tensors="pt")
    tokens = {k: v.to(device) for k, v in tokens.items()}

    # Encode student
    with torch.no_grad():
        student_emb = F.normalize(model.encode_user(
            input_ids=tokens["input_ids"],
            attention_mask=tokens["attention_mask"]
        ), dim=1)

        # Similarity with all universities
        sims = student_emb @ uni_embeddings.T

    # Sort and get top-k
    topk = sims.topk(req.top_k)
    results = []
    for i, idx in enumerate(topk.indices[0]):
        results.append({
            "rank": i+1,
            "university": uni_names[idx],
            "score": float(topk.values[0][i])
        })

    return {"recommendations": results}