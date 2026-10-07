#!/usr/bin/env python
"""Preprocess seed datasets, generate canonical vocabularies and artifact mappings."""
from __future__ import annotations

import json
import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

import pandas as pd

from scripts.common import (
    ARTIFACTS_DIR,
    PROCESSED_DIR,
    SEED_DIR,
    build_skill_vocabulary,
    canonicalize_skill,
    ensure_directories,
    load_aliases,
    load_seed_data,
    save_json,
)


def preprocess():
    print("=" * 60)
    print("Vista Flare - Preprocessing Pipeline")
    print("=" * 60)

    ensure_directories()
    aliases = load_aliases()
    print(f"Loaded {len(aliases)} skill aliases.")

    roles_df, skills_df, role_skills_df = load_seed_data()
    print(f"Loaded {len(roles_df)} roles, {len(skills_df)} skills, {len(role_skills_df)} role-skill pairs.")

    # 1. Build canonical skill vocabulary
    skill_vocab = build_skill_vocabulary()
    print(f"Built canonical skill vocabulary with {len(skill_vocab)} skills.")

    # 2. Build canonical role vocabulary
    role_names = roles_df.sort_values("role_id")["role_name"].tolist()
    print(f"Built canonical role vocabulary with {len(role_names)} roles.")

    # 3. Save mappings
    save_json(ARTIFACTS_DIR / "skill_mapping.json", {"skills": skill_vocab, "version": "v1"})
    save_json(ARTIFACTS_DIR / "role_mapping.json", {"roles": role_names, "version": "v1"})
    print("Saved skill_mapping.json and role_mapping.json to artifacts/.")

    # 4. Verify role skills coverage
    role_skills_canonical = role_skills_df.copy()
    role_skills_canonical["canonical_skill"] = role_skills_canonical["skill_name"].map(
        lambda s: canonicalize_skill(s, aliases)
    )
    unmapped = role_skills_canonical[~role_skills_canonical["canonical_skill"].isin(skill_vocab)]
    if len(unmapped) > 0:
        print(f"Warning: {len(unmapped)} role skills are not in vocabulary:")
        print(unmapped[["role_name", "skill_name"]])
    else:
        print("[OK] All role skills successfully map to canonical vocabulary.")

    print("=" * 60)
    print("Preprocessing completed successfully.")
    print("=" * 60)


if __name__ == "__main__":
    preprocess()
