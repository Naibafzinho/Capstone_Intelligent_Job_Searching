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

        # ── Phrase matcher (surface form) ──────────────────────
        print("Building phrase matcher (surface)...")
        self.matcher = PhraseMatcher(self.nlp.vocab, attr="LOWER")
        patterns = list(self.nlp.pipe(skills, batch_size=2000))
        self.matcher.add("SKILLS", patterns)

        # ── Phrase matcher (lemma) ─────────────────────────────
        # Catches plurals / verb inflections, e.g. "managed" → "manage"
        print("Building phrase matcher (lemma)...")
        self.lemma_matcher = PhraseMatcher(self.nlp.vocab, attr="LEMMA")
        self.lemma_matcher.add("SKILLS_LEMMA", patterns)

        # ── Pre-tokenised skill lemma sets for token-level scan ─
        # Covers cases like "machine learning" split across a hyphen or slash
        print("Building token-level lemma index...")
        self._skill_lemma_sets: dict[str, frozenset[str]] = {}
        for skill, doc in zip(skills, patterns):
            lemmas = frozenset(t.lemma_ for t in doc if not t.is_punct)
            if lemmas:
                self._skill_lemma_sets[skill] = lemmas

        # ── Embeddings (used only for the guarded semantic pass) ──
        print("Computing skill embeddings...")
        self.skills, self.matrix = self._build_matrix(skills)

        print("Extractor ready.\n")

    def _build_matrix(self, skills: list[str]):
        valid, vectors = [], []
        for skill in skills:
            vec = self.nlp(skill).vector
            if vec.any():
                valid.append(skill)
                vectors.append(vec)
        matrix = np.array(vectors, dtype=np.float32)
        norms = np.linalg.norm(matrix, axis=1, keepdims=True)
        norms[norms == 0] = 1
        return valid, matrix / norms

    def extract(self, text: str, threshold: float = 0.92) -> list[str]:
        """
        Return every skill that is explicitly present in *text*.

        Four passes are run in order, all anchored to actual resume tokens:
          1. Surface phrase match   – exact text, any casing
          2. Lemma phrase match     – inflected forms, e.g. "managed" → "manage"
          3. Token-level lemma scan – multi-word skills (2+ tokens) whose lemmas
                                      all appear somewhere in the resume
          4. Guarded semantic match – cosine similarity >= threshold, but ONLY
                                      accepted when at least one skill token also
                                      appears verbatim in the resume, preventing
                                      pure hallucination from the vector space.

        Args:
            text:      Raw resume text.
            threshold: Cosine similarity cutoff for the semantic pass (default 0.92).
        """
        cleaned = clean_text(text)
        doc = self.nlp(cleaned)

        found: set[str] = set()

        # ── Pass 1: surface exact match ────────────────────────
        for _, start, end in self.matcher(doc):
            found.add(doc[start:end].text.lower())

        # ── Pass 2: lemma phrase match ─────────────────────────
        for _, start, end in self.lemma_matcher(doc):
            # Map back to the canonical skill name via lemma comparison
            span_lemmas = frozenset(t.lemma_ for t in doc[start:end] if not t.is_punct)
            for skill, skill_lemmas in self._skill_lemma_sets.items():
                if skill_lemmas == span_lemmas:
                    found.add(skill)
                    break

        # ── Pass 3: token-level lemma scan ────────────────────
        # Build a lemma bag from the whole resume once.
        resume_lemmas = [
            t.lemma_.lower()
            for t in doc
            if not t.is_stop and not t.is_punct and not t.is_space
        ]
        resume_lemma_set = set(resume_lemmas)

        for skill, skill_lemmas in self._skill_lemma_sets.items():
            if skill in found:
                continue  # already matched

            if not skill_lemmas.issubset(resume_lemma_set):
                # At least one required lemma is absent → definite miss
                continue

            # For single-token skills the subset check is sufficient only
            # when the token is relatively rare. Require at least 2 tokens
            # for order-independent matching to avoid false positives like
            # "data" matching a "data entry" skill.
            if len(skill_lemmas) < 2:
                continue

            found.add(skill)

        # ── Pass 4: guarded semantic match ─────────────────────
        # Cosine similarity alone is too loose even at 0.95 because related
        # tech terms cluster tightly (Java ↔ JavaScript, AWS ↔ Azure).
        # The guard requires that at least one non-stop token from the
        # candidate skill actually appears in the resume, so the vector
        # only promotes a match rather than creating one from nothing.
        if self.matrix.size:
            resume_surface = {t.lower_ for t in doc if not t.is_space}
            for chunk in doc.noun_chunks:
                vec = chunk.vector
                if not vec.any():
                    continue
                norm = np.linalg.norm(vec)
                if norm == 0:
                    continue
                vec = vec / norm
                sims = self.matrix @ vec
                best_idx = int(np.argmax(sims))
                if sims[best_idx] < threshold:
                    continue
                candidate = self.skills[best_idx]
                if candidate in found:
                    continue
                # Guard: at least one skill token must exist in the resume
                skill_tokens = {
                    t.lower_
                    for t in self.nlp(candidate)
                    if not t.is_stop and not t.is_punct
                }
                if skill_tokens & resume_surface:
                    found.add(candidate)

        return sorted(found)

