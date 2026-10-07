#!/usr/bin/env python
"""Generate synthetic training profiles for Vista Flare career prediction model.

Creates 20,000+ synthetic user skill profiles based on role-skill relationships
with realistic variations in skill levels and coverage.
"""
from __future__ import annotations

import json
import random
from pathlib import Path

import numpy as np
import pandas as pd

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.common import (
    ARTIFACTS_DIR,
    LEVEL_ORDER,
    LEVEL_VALUES,
    PROCESSED_DIR,
    RANDOM_SEED,
    SEED_DIR,
    build_skill_vocabulary,
    canonicalize_skill,
    ensure_directories,
    load_aliases,
    load_seed_data,
    save_json,
    set_global_seed,
)

NUM_PROFILES = 22000
NOISE_SKILL_PROB = 0.25
PARTIAL_PROFILE_PROB = 0.35


def sample_level() -> str:
    weights = [0.2, 0.4, 0.3, 0.1]
    return random.choices(LEVEL_ORDER, weights=weights, k=1)[0]


def add_noise_skills(profile: list[dict], all_skills: list[str], role_skills: set[str], count: int = 2) -> None:
    candidates = [s for s in all_skills if s not in role_skills]
    if not candidates:
        return
    chosen = random.sample(candidates, min(count, len(candidates)))
    for skill in chosen:
        profile.append({"name": skill, "level": sample_level()})


def generate_strong_profile(role_skills_df: pd.DataFrame, role_id: int, all_skills: list[str], aliases: dict) -> list[dict]:
    role_skills = role_skills_df[role_skills_df["role_id"] == role_id]
    profile = []
    role_skill_names = set()
    for _, row in role_skills.iterrows():
        skill = canonicalize_skill(row["skill_name"], aliases)
        if not skill:
            continue
        role_skill_names.add(skill)
        importance = float(row["importance"])
        if random.random() < importance * 0.9:
            level = sample_level()
            if random.random() < 0.3:
                level = "advanced"
            profile.append({"name": skill, "level": level})
    return profile, role_skill_names


def generate_intermediate_profile(role_skills_df: pd.DataFrame, role_id: int, all_skills: list[str], aliases: dict) -> tuple[list[dict], set[str]]:
    role_skills = role_skills_df[role_skills_df["role_id"] == role_id]
    profile = []
    role_skill_names = set()
    for _, row in role_skills.iterrows():
        skill = canonicalize_skill(row["skill_name"], aliases)
        if not skill:
            continue
        role_skill_names.add(skill)
        importance = float(row["importance"])
        if random.random() < importance * 0.7:
            level = random.choice(["beginner", "intermediate"])
            profile.append({"name": skill, "level": level})
    return profile, role_skill_names


def generate_partial_profile(role_skills_df: pd.DataFrame, role_id: int, all_skills: list[str], aliases: dict) -> tuple[list[dict], set[str]]:
    role_skills = role_skills_df[role_skills_df["role_id"] == role_id]
    profile = []
    role_skill_names = set()
    for _, row in role_skills.iterrows():
        skill = canonicalize_skill(row["skill_name"], aliases)
        if not skill:
            continue
        role_skill_names.add(skill)
        importance = float(row["importance"])
        if random.random() < importance * 0.4:
            level = random.choice(["beginner", "intermediate"])
            profile.append({"name": skill, "level": level})
    return profile, role_skill_names


def generate_overlapping_profile(
    role_skills_df: pd.DataFrame,
    role_id: int,
    all_roles: pd.DataFrame,
    all_skills: list[str],
    aliases: dict,
) -> tuple[list[dict], set[str]]:
    profile, role_skill_names = generate_intermediate_profile(role_skills_df, role_id, all_skills, aliases)
    other_roles = all_roles[all_roles["role_id"] != role_id]["role_id"].tolist()
    if other_roles:
        other_id = random.choice(other_roles)
        other_skills = role_skills_df[role_skills_df["role_id"] == other_id]
        for _, row in other_skills.iterrows():
            if random.random() < 0.3:
                skill = canonicalize_skill(row["skill_name"], aliases)
                if skill and skill not in role_skill_names:
                    profile.append({"name": skill, "level": random.choice(["beginner", "intermediate"])})
                    role_skill_names.add(skill)
    return profile, role_skill_names


def main():
    print("=" * 60)
    print("Vista Flare - Training Data Generation")
    print("=" * 60)

    ensure_directories()
    set_global_seed(RANDOM_SEED)

    print("\n[1/5] Loading seed data...")
    roles_df, skills_df, role_skills_df = load_seed_data()
    aliases = load_aliases()

    print(f"  - Loaded {len(roles_df)} roles")
    print(f"  - Loaded {len(skills_df)} skills")
    print(f"  - Loaded {len(role_skills_df)} role-skill mappings")

    print("\n[2/5] Building skill vocabulary...")
    all_skills = build_skill_vocabulary()
    print(f"  - Total unique skills: {len(all_skills)}")

    print("\n[3/5] Generating synthetic profiles...")
    profiles = []
    role_ids = roles_df["role_id"].tolist()
    role_names_map = dict(zip(roles_df["role_id"], roles_df["role_name"]))
    skill_vocab_set = set(all_skills)

    profiles_per_role = NUM_PROFILES // len(role_ids)
    extra = NUM_PROFILES % len(role_ids)

    for role_id in role_ids:
        n = profiles_per_role + (1 if role_id <= extra else 0)
        role_name = role_names_map[role_id]

        for i in range(n):
            variant = random.random()
            if variant < 0.35:
                profile, role_skill_names = generate_strong_profile(role_skills_df, role_id, all_skills, aliases)
            elif variant < 0.65:
                profile, role_skill_names = generate_intermediate_profile(role_skills_df, role_id, all_skills, aliases)
            elif variant < 0.85:
                profile, role_skill_names = generate_partial_profile(role_skills_df, role_id, all_skills, aliases)
            else:
                profile, role_skill_names = generate_overlapping_profile(
                    role_skills_df, role_id, roles_df, all_skills, aliases
                )

            if not profile:
                profile, role_skill_names = generate_intermediate_profile(role_skills_df, role_id, all_skills, aliases)

            if random.random() < NOISE_SKILL_PROB:
                add_noise_skills(profile, skill_vocab_set, role_skill_names, count=random.randint(1, 3))

            if random.random() < PARTIAL_PROFILE_PROB and len(profile) > 3:
                keep = random.sample(profile, max(3, len(profile) // 2))
                profile = keep

            profiles.append({
                "role_id": role_id,
                "role_name": role_name,
                "skills": profile,
            })

    random.shuffle(profiles)
    print(f"  - Generated {len(profiles)} profiles")

    print("\n[4/5] Saving mappings...")
    role_names = roles_df.sort_values("role_id")["role_name"].tolist()
    save_json(ARTIFACTS_DIR / "skill_mapping.json", {"skills": all_skills, "version": "v1"})
    save_json(ARTIFACTS_DIR / "role_mapping.json", {"roles": role_names, "version": "v1"})
    print(f"  - Saved {len(all_skills)} skills to artifacts/skill_mapping.json")
    print(f"  - Saved {len(role_names)} roles to artifacts/role_mapping.json")

    print("\n[5/5] Saving training examples...")
    rows = []
    for p in profiles:
        rows.append({
            "role_id": p["role_id"],
            "role_name": p["role_name"],
            "skills_json": json.dumps(p["skills"]),
        })

    df = pd.DataFrame(rows)
    output_path = PROCESSED_DIR / "training_examples.csv"
    df.to_csv(output_path, index=False)
    print(f"  - Saved to {output_path}")

    print("\n" + "=" * 60)
    print("Training data generation complete!")
    print(f"  Total profiles: {len(profiles)}")
    print(f"  Skills: {len(all_skills)}")
    print(f"  Roles: {len(role_names)}")
    print("=" * 60)


if __name__ == "__main__":
    main()
