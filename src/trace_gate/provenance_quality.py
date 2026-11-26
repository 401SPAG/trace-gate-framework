"""Conservative cell-level qualification; raw OCR and prior results stay intact."""
from .provenance import digest


def evaluate_cells(expected: list[dict], extracted: list[dict], *, source_sha256: str,
                   trusted_gold: dict | None = None) -> dict:
    """Compare exact cell identity and critical fields, not page token presence.

    trusted_gold must be independently authenticated by the host. This helper
    neither authenticates a reviewer nor turns an assistant transcript into Gold.
    Numeric tokens remain strings: no inferred separators or silent corrections.
    """
    identity = ("page", "table", "row", "column")
    critical = ("token", "unit", "period", "basis")
    def index(rows):
        result = {}
        for row in rows:
            if set(row) != set(identity+critical) or type(row["page"]) is not int or row["page"] < 1 or any(not isinstance(row[k],str) or not row[k] for k in identity[1:]+critical):
                raise ValueError("CELL_SCHEMA")
            key=tuple(row[k] for k in identity)
            if key in result: raise ValueError("CELL_DUPLICATE")
            result[key]=row
        return result
    if not expected: raise ValueError("CELL_EXPECTED_EMPTY")
    a,b=index(expected),index(extracted)
    matched=sum(all(a[k][f]==b[k][f] for f in critical) for k in a.keys() & b.keys())
    disagreements=[{"cell":list(k),"fields":[f for f in critical if a[k][f]!=b[k][f]]}
                   for k in sorted(a.keys() & b.keys()) if any(a[k][f]!=b[k][f] for f in critical)]
    gold=bool(trusted_gold and trusted_gold.get("method")=="independent_human" and
              trusted_gold.get("reviewer") and trusted_gold.get("expected_sha256")==digest(expected) and
              trusted_gold.get("source_sha256")==source_sha256)
    complete=matched==len(a) and len(a)==len(b)
    return {"expected_cells":len(a),"extracted_cells":len(b),"exact_cells":matched,
            "missing_cells":len(a.keys()-b.keys()),"unexpected_cells":len(b.keys()-a.keys()),
            "critical_mismatches":disagreements,"expected_sha256":digest(expected),
            "independent_gold_verified":gold,"status":"QUALIFIED" if complete and gold else "NOT_QUALIFIED",
            "originals_modified":False,"page_token_presence_is_cell_accuracy":False}
