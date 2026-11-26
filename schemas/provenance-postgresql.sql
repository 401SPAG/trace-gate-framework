-- OPTIONAL projection only. Apply in an isolated schema after deployment review.
-- Canonical manifests remain the source of truth; no production migration here.
CREATE SCHEMA trace_provenance;
CREATE TABLE trace_provenance.bundle (
    bundle_sha256 text PRIMARY KEY CHECK (bundle_sha256 ~ '^[a-f0-9]{64}$'),
    profile_id text NOT NULL,
    payload jsonb NOT NULL,
    validated_at timestamptz NOT NULL,
    validator_version text NOT NULL
);
CREATE TABLE trace_provenance.entity (
    bundle_sha256 text REFERENCES trace_provenance.bundle ON DELETE RESTRICT,
    entity_id text NOT NULL,
    tenant_id text NOT NULL,
    kind text NOT NULL,
    payload jsonb NOT NULL,
    PRIMARY KEY (bundle_sha256, entity_id),
    UNIQUE (bundle_sha256, entity_id, tenant_id)
);
CREATE TABLE trace_provenance.relation (
    bundle_sha256 text NOT NULL,
    from_id text NOT NULL,
    to_id text NOT NULL,
    tenant_id text NOT NULL,
    relation_type text NOT NULL,
    status text NOT NULL CHECK (status IN ('structural','candidate','reviewed')),
    PRIMARY KEY (bundle_sha256, from_id, to_id, relation_type),
    FOREIGN KEY (bundle_sha256, from_id, tenant_id) REFERENCES trace_provenance.entity(bundle_sha256,entity_id,tenant_id),
    FOREIGN KEY (bundle_sha256, to_id, tenant_id) REFERENCES trace_provenance.entity(bundle_sha256,entity_id,tenant_id),
    CHECK (from_id <> to_id)
);
-- No role grants are supplied. The application must enforce TRACE-DM admission
-- before querying, including graph expansion. This DDL alone is not tenant isolation.
