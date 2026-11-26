"""Verify a host-issued read grant before graph expansion and context assembly.

This module does not issue grants or authenticate users. The application supplies
its authenticated principal and a verifier key from protected host configuration,
never from a model request. Grants authorize bounded reads, not execution or truth.
"""
import hashlib
import hmac
from datetime import UTC, datetime

from .provenance import context_receipt, digest, utc, validate_bundle
from .provenance_adapters import bounded_neighbors


def authorized_context(bundle: dict, envelope: dict, *, verifier_key: bytes,
                       authenticated_principal: str, purpose: str,
                       query_sha256: str, read_profile_sha256: str,
                       seeds: list[str], cited_ids: list[str], limit: int,
                       now: datetime | None = None, trusted_reviews: dict | None = None) -> dict:
    """Bind authorization to exact bytes, policy, principal, tenant and time.

    A read grant may be re-used inside its <=300-second validity window. This is
    not a one-shot execution lease. Host review trust remains a separate input.
    """
    if not isinstance(verifier_key, bytes) or len(verifier_key) < 32:
        raise PermissionError("HOST_VERIFIER_KEY_REQUIRED")
    if set(envelope) != {"grant", "mac"}:
        raise PermissionError("READ_GRANT_SCHEMA")
    grant = envelope["grant"]
    expected = hmac.new(verifier_key, digest(grant).encode(), hashlib.sha256).hexdigest()
    if not isinstance(envelope["mac"], str) or not hmac.compare_digest(expected, envelope["mac"]):
        raise PermissionError("READ_GRANT_SIGNATURE")
    fields = {"version", "principal", "tenant_id", "purpose", "query_sha256", "read_profile_sha256",
              "bundle_sha256", "issued_at", "expires_at", "cutoff", "max_bytes", "members"}
    if not isinstance(grant, dict) or set(grant) != fields or grant["version"] != "trace-read-grant/1":
        raise PermissionError("READ_GRANT_SCHEMA")
    current = now or datetime.now(UTC)
    issued, expires = utc(grant["issued_at"]), utc(grant["expires_at"])
    if current.tzinfo is None or not issued <= current < expires or not 0 < (expires-issued).total_seconds() <= 300:
        raise PermissionError("READ_GRANT_EXPIRED_OR_FUTURE")
    if not authenticated_principal or grant["principal"] != authenticated_principal or grant["purpose"] != purpose:
        raise PermissionError("READ_GRANT_PRINCIPAL_OR_PURPOSE")
    if grant["query_sha256"] != query_sha256 or grant["read_profile_sha256"] != read_profile_sha256 or grant["bundle_sha256"] != digest(bundle):
        raise PermissionError("READ_GRANT_IDENTITY")
    if type(grant["max_bytes"]) is not int or grant["max_bytes"] <= 0 or utc(grant["cutoff"]) > current:
        raise PermissionError("READ_GRANT_BOUNDS")
    validate_bundle(bundle, trusted_reviews=trusted_reviews)
    entities = {e["id"]:e for e in bundle["entities"]}
    if not isinstance(grant["members"], list) or not grant["members"]:
        raise PermissionError("READ_GRANT_MEMBERS")
    admitted = set()
    for member in grant["members"]:
        if not isinstance(member, dict) or set(member) != {"id", "artifact_id", "revision", "sha256"}:
            raise PermissionError("READ_GRANT_MEMBERS")
        e = entities.get(member["id"])
        if not e or member["id"] in admitted or any(member[k] != e[k] for k in member) or e["tenant_id"] != grant["tenant_id"]:
            raise PermissionError("READ_GRANT_MEMBER_IDENTITY")
        admitted.add(member["id"])
    selected = bounded_neighbors(bundle, seeds, admitted_ids=admitted, limit=limit, trusted_reviews=trusted_reviews)
    result = context_receipt(bundle, candidate_ids=selected, selected_ids=selected, cited_ids=cited_ids,
        admitted_ids=admitted, cutoff=grant["cutoff"], max_bytes=grant["max_bytes"],
        query_sha256=query_sha256, trusted_reviews=trusted_reviews)
    return {"context":result, "grant_sha256":digest(grant), "principal":authenticated_principal,
            "tenant_id":grant["tenant_id"], "selected_ids":selected, "execution_authorized":False}
