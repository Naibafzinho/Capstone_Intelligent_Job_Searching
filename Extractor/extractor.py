"""
extractor.py
------------
Core logic for extracting skills from text.
"""

import re
import numpy as np
import spacy
from spacy.matcher import PhraseMatcher
from pathlib import Path


# ── Read file ──────────────────────────────────────────────────

def read_file(path: str) -> str:
    path = Path(path)
    ext = path.suffix.lower()

    if ext == ".txt":
        return path.read_text(encoding="utf-8", errors="replace")

    elif ext == ".pdf":
        import pdfplumber
        text = []
        with pdfplumber.open(path) as pdf:
            for page in pdf.pages:
                t = page.extract_text()
                if t:
                    text.append(t)
        return "\n".join(text)

    elif ext in (".docx", ".doc"):
        from docx import Document
        doc = Document(path)
        return "\n".join(p.text for p in doc.paragraphs if p.text.strip())

    else:
        raise ValueError(f"Unsupported file type: {ext}")


# ── Clean text ─────────────────────────────────────────────────

def clean_text(text: str) -> str:
    text = re.sub(r"[^\x20-\x7E\n]", " ", text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{2,}", "\n", text)
    return text.strip()


# ── Extractor ─────────────────────────────────────────────────

class SkillExtractor:

    def __init__(self, skills: list[str], model: str = "en_core_web_md"):
        print(f"Loading spaCy model '{model}'...")
        self.nlp = spacy.load(model)

        skills = sorted({s.strip().lower() for s in skills if s.strip()})
        print(f"{len(skills)} skills loaded.")

        # Phrase matcher
        print("Building phrase matcher...")
        self.matcher = PhraseMatcher(self.nlp.vocab, attr="LOWER")
        patterns = list(self.nlp.pipe(skills, batch_size=2000))
        self.matcher.add("SKILLS", patterns)

        # Embeddings
        print("Computing embeddings...")
        self.skills, self.matrix = self._build_matrix(skills)

        print("Extractor ready.\n")

    def _build_matrix(self, skills):
        valid = []
        vectors = []

        for skill in skills:
            vec = self.nlp(skill).vector
            if vec.any():
                valid.append(skill)
                vectors.append(vec)

        matrix = np.array(vectors, dtype=np.float32)

        norms = np.linalg.norm(matrix, axis=1, keepdims=True)
        norms[norms == 0] = 1

        return valid, matrix / norms

    def extract(self, text: str, threshold: float = 0.80):

        doc = self.nlp(clean_text(text))

        # ── Exact matches ──
        exact = {
            doc[s:e].text.lower()
            for _, s, e in self.matcher(doc)
        }

        # ── Filtered candidate phrases ──
        candidates = [
            chunk for chunk in doc.noun_chunks
            if len(chunk.text) > 2
            and chunk.root.pos_ in ("NOUN", "PROPN")
        ]

        # ── Semantic matches ──
        semantic = set()

        if self.matrix.size:
            for chunk in candidates:
                vec = chunk.vector

                if not vec.any():
                    continue

                norm = np.linalg.norm(vec)
                if norm == 0:
                    continue

                vec = vec / norm
                sims = self.matrix @ vec

                best_idx = int(np.argmax(sims))

                if sims[best_idx] >= threshold:
                    semantic.add(self.skills[best_idx])

        return sorted(exact | semantic)