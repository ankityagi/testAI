"""Supabase client wrapper."""
from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any

from supabase import Client, create_client


@dataclass
class SupabaseClient:
    client: Client

    @classmethod
    def from_env(cls) -> "SupabaseClient":
        url = os.environ.get("SUPABASE_URL")
        key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
        if not url or not key:
            raise RuntimeError("Supabase credentials not configured")
        client = create_client(url, key)
        return cls(client=client)

    def table(self, name: str) -> Any:  # pragma: no cover - thin wrapper
        return self.client.table(name)
