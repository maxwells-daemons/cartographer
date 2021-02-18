"""
Heuristics to select the right groceries.
"""

import numpy as np
import torch
import transformers
from rich.padding import Padding
from rich.table import Table
from rich import box

_MODEL = "johngiorgi/declutr-small"


def load_tokenizer_and_model():
    tokenizer = transformers.AutoTokenizer.from_pretrained(_MODEL)
    model = transformers.AutoModel.from_pretrained(_MODEL)
    return tokenizer, model


def embed(string, tokenizer, model):
    tokens = tokenizer(string, return_tensors="pt")
    with torch.no_grad():
        out = model(**tokens, output_hidden_states=False)
        mean_embedding = out["last_hidden_state"][0].mean(0)
    return mean_embedding.numpy()


def similarity(embed_1, embed_2):
    dot = embed_1.dot(embed_2)
    norm = np.linalg.norm(embed_1) * np.linalg.norm(embed_2)
    return dot / norm


def score(item, description_embedding, tokenizer, model) -> float:
    """
    Score items. Higher is better.
    """
    item_embedding = embed(item["description"], tokenizer, model)
    sim = similarity(item_embedding, description_embedding)
    return sim


def select_item(item, data, description, tokenizer, model, console):
    """
    Select the best item from a list.
    """
    if not description:  # No description: just select the first item
        result = data[0]
        console.print(
            Padding(
                f"[bold yellow]{item} [bold]-> [bold green]{result['description']}", 1
            ),
            justify="center",
        )
        return result

    table = Table(title=f"[bold yellow]{item} -- {description}", box=box.ROUNDED)
    table.add_column("Description")
    table.add_column("Similarity")

    # Precompute description embedding
    description_embedding = embed(description, tokenizer, model)

    # Select the item with the greatest text similarity
    best_item = data[0]
    best_score = -1
    rows = []
    for item in data:
        item_score = score(item, description_embedding, tokenizer, model)
        if item_score > best_score:
            best_score = item_score
            best_item = item

        rows.append((item, item_score))

    for item, item_score in rows:
        if item_score == best_score:
            formatted_description = f"[bold green]{item['description']}"
            formatted_score = f"[bold green]{item_score:.3f}"
        else:
            formatted_description = f"{item['description']}"
            formatted_score = f"{item_score:.3f}"

        table.add_row(formatted_description, formatted_score)

    console.print(Padding(table, 1), justify="center")
    return best_item
