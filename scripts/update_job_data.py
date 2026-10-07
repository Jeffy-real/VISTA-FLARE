#!/usr/bin/env python
"""Update job data using the JobDataProvider abstraction with offline fallback."""
from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from backend.app.services.job_provider import CompositeJobProvider


def update_job_market_data(use_external: bool = False):
    print("=" * 60)
    print("Vista Flare - Job Market Data Ingestion")
    print("=" * 60)
    provider = CompositeJobProvider()

    print(f"Fetching jobs (external enabled: {use_external})...")
    jobs = provider.fetch_jobs(limit=100, use_external=use_external)

    if not jobs:
        print("Warning: No jobs fetched. Falling back to local seed data.")
        jobs = provider.local_provider.fetch_jobs()

    print(f"[OK] Retrieved {len(jobs)} jobs.")
    sample = jobs[0] if jobs else {}
    print(f"Sample job: {sample.get('job_title', 'N/A')} at {sample.get('company_name', 'N/A')} ({sample.get('source', 'seed')})")
    print("=" * 60)
    print("Job market data ingestion completed.")
    print("=" * 60)


if __name__ == "__main__":
    ext = "--external" in sys.argv
    update_job_market_data(use_external=ext)
