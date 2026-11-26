-- OPTIONAL isolated deployment profile; never execute on a production DB implicitly.
-- Apply after provenance-postgresql.sql as an administrator. Reader logins must
-- be authenticated by the host/DB; do not expose a shared privileged connection.
CREATE ROLE trace_projection_reader NOLOGIN;
CREATE TABLE trace_provenance.principal_tenant (
    principal name NOT NULL,
    tenant_id text NOT NULL,
    PRIMARY KEY (principal, tenant_id)
);
REVOKE ALL ON trace_provenance.principal_tenant FROM PUBLIC;
CREATE FUNCTION trace_provenance.tenant_allowed(wanted text) RETURNS boolean
LANGUAGE sql STABLE SECURITY DEFINER SET search_path = pg_catalog
AS $$ SELECT EXISTS (SELECT 1 FROM trace_provenance.principal_tenant
                     WHERE principal = SESSION_USER AND tenant_id = wanted) $$;
REVOKE ALL ON FUNCTION trace_provenance.tenant_allowed(text) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION trace_provenance.tenant_allowed(text) TO trace_projection_reader;
GRANT USAGE ON SCHEMA trace_provenance TO trace_projection_reader;
GRANT SELECT ON trace_provenance.entity, trace_provenance.relation TO trace_projection_reader;
-- Deliberately no SELECT on canonical bundle.payload: it can contain several tenants.
ALTER TABLE trace_provenance.entity ENABLE ROW LEVEL SECURITY;
ALTER TABLE trace_provenance.entity FORCE ROW LEVEL SECURITY;
ALTER TABLE trace_provenance.relation ENABLE ROW LEVEL SECURITY;
ALTER TABLE trace_provenance.relation FORCE ROW LEVEL SECURITY;
CREATE POLICY entity_tenant ON trace_provenance.entity FOR SELECT TO trace_projection_reader
    USING (trace_provenance.tenant_allowed(tenant_id));
CREATE POLICY relation_tenant ON trace_provenance.relation FOR SELECT TO trace_projection_reader
    USING (trace_provenance.tenant_allowed(tenant_id));
-- Mapping updates and ingest writes remain administrator/host duties. Never grant
-- readers membership in another tenant login, a writer, the owner or BYPASSRLS role.
