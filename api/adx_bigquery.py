"""
adx_bigquery.py — Azure Data Explorer backend exposing a BigQuery-compatible surface.

Replaces the non-Azure `google-cloud-bigquery` SDK (prereq CLOUD_SDK_MIGRATION).
Call sites keep their shape:  `from adx_bigquery import bigquery`.

Configuration (all optional at import time — the module never raises on import):
    ADX_CLUSTER_URI   e.g. https://mycluster.eastus.kusto.windows.net
    ADX_DATABASE      e.g. osintneoai
    ADX_TENANT_ID / ADX_CLIENT_ID / ADX_CLIENT_SECRET   (service principal)
      -- or omit all three to use DefaultAzureCredential / managed identity.
    ADX_DATASETS      comma-separated BigQuery dataset names to expose in the
                      catalog (default: the datasets this app already uses).

Table naming: BigQuery `project.dataset.table` maps to ADX `dataset_table`.
The catalog endpoints reverse that mapping against ADX_DATASETS.

Failure behaviour matches the pre-migration app exactly: every call that needs
a live backend raises, and every call site already wraps those calls in
try/except with a graceful fallback. Until an ADX cluster exists, endpoints
degrade the same way they did when GCP credentials were absent.
"""

from __future__ import annotations

import json
import os
import re
import threading
from datetime import datetime, timezone

__all__ = ["bigquery", "UnsupportedQuery"]


class UnsupportedQuery(Exception):
    """Raised when a statement has no Kusto equivalent this shim can build."""


# ── Configuration ────────────────────────────────────────────────────────────

DEFAULT_DATASETS = (
    "osint_engine",
    "osint_pipeline",
    "workspace",
    "workspaces",
    "ledger",
    "osint",
)


def _datasets() -> list[str]:
    raw = os.getenv("ADX_DATASETS", "")
    names = [d.strip() for d in raw.split(",") if d.strip()]
    return names or list(DEFAULT_DATASETS)


def _cluster_uri() -> str:
    return os.getenv("ADX_CLUSTER_URI", "").strip()


def _database() -> str:
    return os.getenv("ADX_DATABASE", "").strip() or "osintneoai"


# ── Identifier mapping ───────────────────────────────────────────────────────

_SAFE = re.compile(r"[^0-9A-Za-z_]+")


def _sanitize(name: str) -> str:
    return _SAFE.sub("_", name).strip("_") or "table"


def to_adx_table(ref: str) -> str:
    """`project.dataset.table` | `dataset.table` | `table`  ->  ADX table name."""
    parts = [p for p in ref.replace("`", "").strip().split(".") if p]
    if len(parts) >= 3:
        parts = parts[-2:]
    return _sanitize("_".join(parts))


def to_bigquery_ref(adx_table: str, project: str | None = None) -> str:
    """Best-effort reverse of :func:`to_adx_table` for the catalog endpoints."""
    project = project or os.getenv("GCP_PROJECT_ID", "osintneoai")
    for ds in _datasets():
        prefix = _sanitize(ds) + "_"
        if adx_table.startswith(prefix):
            return "{}.{}.{}".format(project, ds, adx_table[len(prefix):])
    return "{}.{}".format(project, adx_table)


# ── BigQuery type -> Kusto type ─────────────────────────────────────────────

_BQ_TO_KUSTA = {
    "STRING": "string",
    "BYTES": "string",
    "BOOL": "bool",
    "BOOLEAN": "bool",
    "INT64": "long",
    "INTEGER": "long",
    "INT": "long",
    "FLOAT64": "real",
    "FLOAT": "real",
    "DOUBLE": "real",
    "NUMERIC": "decimal(38,9)",
    "BIGNUMERIC": "decimal(38,9)",
    "TIMESTAMP": "datetime",
    "DATE": "datetime",
    "TIME": "string",
    "DATETIME": "datetime",
    "GEOGRAPHY": "string",
    "JSON": "dynamic",
    "RECORD": "dynamic",
    "STRUCT": "dynamic",
}

_KUSTA_TO_BQ = {v: k for k, v in _BQ_TO_KUSTA.items()}
_KUSTA_TO_BQ.update(
    {
        "string": "STRING",
        "long": "INT64",
        "real": "FLOAT64",
        "bool": "BOOL",
        "datetime": "TIMESTAMP",
        "dynamic": "JSON",
        "decimal(38,9)": "NUMERIC",
    }
)


def _map_type(bq_type: str) -> str:
    t = (bq_type or "STRING").strip().upper()
    if t.startswith("ARRAY<"):
        inner = t[6:-1].strip()
        # Kusto has no typed arrays; arrays travel as dynamic JSON.
        return "dynamic" if inner in ("STRING", "BYTES") else "dynamic"
    if t.startswith("STRUCT<") or t.startswith("RECORD<"):
        return "dynamic"
    return _BQ_TO_KUSTA.get(t, "string")


def _kusto_to_bq(ktype: str) -> str:
    return _KUSTA_TO_BQ.get((ktype or "").lower().split("(")[0].strip(), "STRING")


# ── Parameter objects (BigQuery-compatible) ─────────────────────────────────

class ScalarQueryParameter:
    def __init__(self, name, type_, value):
        self.name = name
        self.type = (type_ or "STRING").upper()
        self.value = value

    def literal(self) -> str:
        return _to_literal(self.value, self.type)


class ArrayQueryParameter:
    def __init__(self, name, array_type, values):
        self.name = name
        self.type = "ARRAY<{}>".format((array_type or "STRING").upper())
        self.values = list(values or [])

    def literal(self) -> str:
        inner = _to_literal
        return "[" + ",".join(inner(v, self.type[6:-1]) for v in self.values) + "]"


def _to_literal(value, type_: str) -> str:
    t = (type_ or "STRING").upper()
    if value is None:
        return "null()"
    if t in ("BOOL", "BOOLEAN"):
        return "true" if value else "false"
    if t in ("INT64", "INTEGER", "INT", "FLOAT64", "FLOAT", "DOUBLE", "NUMERIC", "BIGNUMERIC"):
        return str(value)
    if t == "TIMESTAMP":
        return "datetime({})".format(_quote(str(value)))
    s = str(value)
    return _quote(s)


def _quote(s: str) -> str:
    return "'" + s.replace("\\", "\\\\").replace("'", "\\'") + "'"


class QueryJobConfig:
    def __init__(self, query_parameters=None, **_):
        self.query_parameters = list(query_parameters or [])


class Dataset:
    def __init__(self, dataset_ref, location="East US"):
        self.reference = dataset_ref
        self.dataset_id = getattr(dataset_ref, "dataset_id", str(dataset_ref))
        self.location = location


class _Field:
    def __init__(self, name, field_type="STRING", mode="NULLABLE", description=""):
        self.name = name
        self.field_type = field_type
        self.mode = mode
        self.description = description or ""


class SchemaField:
    def __init__(self, name, field_type, mode="NULLABLE", description=None):
        self.name = name
        self.field_type = field_type
        self.mode = mode
        self.description = description or ""

    def __repr__(self):
        return "SchemaField({}, {})".format(self.name, self.field_type)


class Table:
    def __init__(self, reference, schema=None, table_type="TABLE",
                 description="", created=None, num_rows=0, num_bytes=0):
        self.reference = reference
        self.schema = list(schema or [])
        self.table_type = table_type
        self.description = description or ""
        self.created = created or datetime.now(timezone.utc)
        self.num_rows = num_rows
        self.num_bytes = num_bytes
        self.table_id = str(reference).split(".")[-1]


# ── Row / Job result objects ────────────────────────────────────────────────

class Row(dict):
    """dict subclass so `dict(row)` works exactly as with BigQuery rows."""

    def __getitem__(self, key):
        try:
            return super().__getitem__(key)
        except KeyError:
            for k, v in self.items():
                if k.lower() == str(key).lower():
                    return v
            raise KeyError(key)

    def get(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            return default

    def keys(self):
        return dict.keys(self)


class _RowIterator:
    def __init__(self, rows):
        self._rows = list(rows)

    def __iter__(self):
        return iter(self._rows)

    def __next__(self):
        return next(iter(self._rows))

    def __len__(self):
        return len(self._rows)


class _Job:
    def __init__(self, rows, sql=None):
        self._rows = list(rows or [])
        self.sql = sql
        self.errors = []

    def result(self, **_):
        return _RowIterator(self._rows)

    def __iter__(self):
        return iter(self._rows)


# ── SQL -> KQL translation ─────────────────────────────────────────────────

_BACKTICK = re.compile(r"`([^`]*)`")
_FROM = re.compile(
    r"\bFROM\s+(?:`([^`]+)`|([A-Za-z_][\w$]*(?:\.[A-Za-z_][\w$]*)+))",
    re.IGNORECASE,
)


def _bind_params(sql: str, params) -> str:
    """Substitute BigQuery `@name` placeholders with Kusto-safe literals."""
    if not params:
        return sql
    table = {}
    for p in params or []:
        if isinstance(p, (ScalarQueryParameter, ArrayQueryParameter)):
            table[p.name] = p.literal()
    out = sql
    for name, literal in table.items():
        out = re.sub(r"@" + re.escape(name) + r"\b", literal, out)
    # A bare @param with no config still has to become a literal, not KQL.
    out = re.sub(r"@[A-Za-z_]\w*", "''", out)
    return out


def _strip_clause(sql: str, keyword: str):
    """Return (without_keyword_part, matched_part)."""
    m = re.search(
        r"\b" + keyword + r"\b(.*?)(?=\b(?:ORDER\s+BY|GROUP\s+BY|HAVING|LIMIT|OFFSET)\b|$)",
        sql,
        re.IGNORECASE | re.DOTALL,
    )
    if not m:
        return sql, ""
    return sql[: m.start()] + sql[m.end():], m.group(0)


def _translate_select(sql: str) -> str:
    body = sql.strip().rstrip(";")

    m_from = _FROM.search(body)
    if not m_from:
        raise UnsupportedQuery("no FROM clause found: {}".format(body[:120]))
    raw_ref = (m_from.group(1) or m_from.group(2)).strip()
    table = to_adx_table(raw_ref)

    head = body[: m_from.start()]
    head = re.sub(r"^\s*SELECT\b", "", head, flags=re.IGNORECASE).strip()

    remainder = body[m_from.end():]

    # WHERE
    m_where = re.search(r"\bWHERE\b", remainder, re.IGNORECASE)
    where_sql = ""
    if m_where:
        m_order = re.search(r"\b(?:ORDER\s+BY|GROUP\s+BY|HAVING|LIMIT|OFFSET)\b",
                            remainder[m_where.end():], re.IGNORECASE)
        end = m_where.end() + (m_order.start() if m_order else len(remainder) - m_where.end())
        where_sql = remainder[m_where.end():end].strip()
        remainder = remainder[: m_where.start()] + remainder[end:]

    # ORDER BY
    m_order = re.search(r"\bORDER\s+BY\b(.*?)(?=\bLIMIT\b|$)", remainder,
                        re.IGNORECASE | re.DOTALL)
    order_sql = m_order.group(1).strip() if m_order else ""
    if m_order:
        remainder = remainder[: m_order.start()] + remainder[m_order.end():]

    # LIMIT
    m_limit = re.search(r"\bLIMIT\s+(\d+)", remainder, re.IGNORECASE)
    limit = int(m_limit.group(1)) if m_limit else None

    pipeline = [table]
    if where_sql:
        pipeline.append("| where " + _where_to_kql(where_sql))
    if head and head != "*":
        cols = _normalize_select_list(head)
        if cols:
            pipeline.append("| project " + cols)
    if order_sql:
        pipeline.append("| order by " + _order_to_kql(order_sql))
    if limit is not None:
        pipeline.append("| take {}".format(limit))
    return "\n| ".join(pipeline)


def _normalize_select_list(head: str) -> str:
    parts, depth, cur = [], 0, ""
    for ch in head:
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
        if ch == "," and depth == 0:
            parts.append(cur.strip())
            cur = ""
        else:
            cur += ch
    if cur.strip():
        parts.append(cur.strip())

    out = []
    for p in parts:
        p = _BACKTICK.sub(r"\1", p).strip()
        if re.match(r"^[\w$.]+\s+AS\s+\w+$", p, re.IGNORECASE):
            col, alias = re.split(r"\s+AS\s+", p, flags=re.IGNORECASE)
            out.append("{} = {}".format(alias.strip(), _col_to_kql(col.strip())))
        elif re.match(r"^[\w$.]+$", p):
            out.append(_col_to_kql(p))
        else:
            out.append(_expr_to_kql(p))
    return ", ".join(out)


def _col_to_kql(col: str) -> str:
    col = col.split(".")[-1]
    return col if re.match(r"^[A-Za-z_]\w*$", col) else _expr_to_kql(col)


def _expr_to_kql(expr: str) -> str:
    e = expr
    e = re.sub(r"\bCOUNT\s*\(\s*\*\s*\)", "count()", e, flags=re.IGNORECASE)
    e = re.sub(r"\bCOUNT\s*\(", "count(", e, flags=re.IGNORECASE)
    e = re.sub(r"\bIFNULL\s*\(", "iif(isnotempty(", e, flags=re.IGNORECASE)
    e = re.sub(r"\bCOALESCE\s*\(", "coalesce(", e, flags=re.IGNORECASE)
    e = re.sub(r"\bEXTRACT\s*\(", "extract(", e, flags=re.IGNORECASE)
    e = re.sub(r"\bLOWER\s*\(", "tolower(", e, flags=re.IGNORECASE)
    e = re.sub(r"\bUPPER\s*\(", "toupper(", e, flags=re.IGNORECASE)
    e = re.sub(r"\bLENGTH\s*\(", "strlen(", e, flags=re.IGNORECASE)
    e = re.sub(r"\bCAST\s*\(", "tostring(", e, flags=re.IGNORECASE)
    e = re.sub(r"\bCONCAT\s*\(", "strcat(", e, flags=re.IGNORECASE)
    return e


def _where_to_kql(where_sql: str) -> str:
    w = where_sql.strip()
    w = _BACKTICK.sub(r"\1", w)
    w = re.sub(r"<>", "!=", w)
    w = re.sub(r"(?<![<>!=])=(?!=)", "==", w)
    w = re.sub(r"\bAND\b", "and", w, flags=re.IGNORECASE)
    w = re.sub(r"\bOR\b", "or", w, flags=re.IGNORECASE)
    w = re.sub(r"\bIS\s+NULL\b", "isnull()", w, flags=re.IGNORECASE)
    w = re.sub(r"\bIS\s+NOT\s+NULL\b", "isnotempty()", w, flags=re.IGNORECASE)
    w = re.sub(r"\bNOT\s+IN\s*\(", "!in~ (", w, flags=re.IGNORECASE)
    w = re.sub(r"\bIN\s*\(", "in~ (", w, flags=re.IGNORECASE)
    w = re.sub(r"\bIS\s+TRUE\b", "== true", w, flags=re.IGNORECASE)
    w = re.sub(r"\bIS\s+FALSE\b", "== false", w, flags=re.IGNORECASE)
    w = re.sub(r"\bLIKE\b", "has", w, flags=re.IGNORECASE)
    w = re.sub(r"\bNOT\s+LIKE\b", "!has", w, flags=re.IGNORECASE)
    w = re.sub(r"\bFALSE\b", "false", w, flags=re.IGNORECASE)
    w = re.sub(r"\bTRUE\b", "true", w, flags=re.IGNORECASE)
    w = re.sub(r"\bIFNULL\s*\(([^,]+),\s*([^)]+)\)", r'coalesce(\1, \2)', w, flags=re.IGNORECASE)
    return w


def _order_to_kql(order_sql: str) -> str:
    parts, depth, cur = [], 0, ""
    for ch in order_sql:
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
        if ch == "," and depth == 0:
            parts.append(cur.strip())
            cur = ""
        else:
            cur += ch
    if cur.strip():
        parts.append(cur.strip())

    out = []
    for p in parts:
        m = re.match(r"^(.*?)\s+(ASC|DESC)$", p.strip(), re.IGNORECASE | re.DOTALL)
        col = _col_to_kql(_BACKTICK.sub(r"\1", m.group(1)).strip()) if m else _col_to_kql(
            _BACKTICK.sub(r"\1", p).strip())
        direction = m.group(2).lower() if m else "asc"
        out.append("{} {}".format(col, direction))
    return ", ".join(out)


def _translate_create_table(sql: str) -> str:
    m = re.search(
        r"CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?(?:`([^`]+)`|([\w$.]+))\s*\((.*)\)\s*$",
        sql.strip().rstrip(";"),
        re.IGNORECASE | re.DOTALL,
    )
    if not m:
        raise UnsupportedQuery("unrecognised CREATE TABLE: {}".format(sql[:120]))
    raw_ref = (m.group(1) or m.group(2)).strip()
    cols_blob = m.group(3)
    table = to_adx_table(raw_ref)

    cols, depth, cur = [], 0, ""
    for ch in cols_blob:
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
        if ch == "," and depth == 0:
            cols.append(cur.strip())
            cur = ""
        else:
            cur += ch
    if cur.strip():
        cols.append(cur.strip())

    rendered = []
    for c in cols:
        m_col = re.match(r"^(?:`([^`]+)`|([\w$]+))\s+([A-Za-z_][\w<>,\s]*?)(?:\s+DEFAULT\b.*)?$",
                         c.strip(), re.IGNORECASE | re.DOTALL)
        if not m_col:
            continue
        name = (m_col.group(1) or m_col.group(2)).strip()
        type_ = _map_type(m_col.group(3))
        rendered.append("{}:{}".format(name, type_))
    if not rendered:
        raise UnsupportedQuery("no parseable columns in: {}".format(cols_blob[:120]))
    return ".create table ifnotexists {} ({})".format(table, ", ".join(rendered))


def _translate_update(sql: str) -> str:
    m = re.search(
        r"UPDATE\s+(?:`([^`]+)`|([\w$.]+))\s+SET\s+(.*?)(?:\s+WHERE\s+(.*))?$",
        sql.strip().rstrip(";"),
        re.IGNORECASE | re.DOTALL,
    )
    if not m:
        raise UnsupportedQuery("unrecognised UPDATE: {}".format(sql[:120]))
    raw_ref = (m.group(1) or m.group(2)).strip()
    sets_blob = (m.group(3) or "").strip()
    where_blob = (m.group(4) or "").strip()
    table = to_adx_table(raw_ref)

    sets = []
    for part in [s.strip() for s in sets_blob.split(",") if s.strip()]:
        if "=" not in part:
            continue
        col, val = part.split("=", 1)
        col = _BACKTICK.sub(r"\1", col).strip()
        val = val.strip()
        if re.match(r"^[\w$.]+\s*\+\s*1$", val):
            lhs = val.split("+")[0].strip().split(".")[-1]
            sets.append("{} = {} + 1".format(col, lhs))
        else:
            sets.append("{} = {}".format(col, _literalise(val)))
    if not sets:
        raise UnsupportedQuery("no parseable SET clause: {}".format(sets_blob[:120]))

    out = table
    if where_blob:
        out += "\n| where " + _where_to_kql(where_blob)
    return out + "\n| update " + ", ".join(sets)


def _literalise(val: str) -> str:
    v = val.strip()
    if re.match(r"^-?\d+(\.\d+)?$", v):
        return v
    if re.match(r"^(true|false|null)$", v, re.IGNORECASE):
        return v.lower()
    if v.startswith("@"):
        return _quote("")
    return v


def translate(sql: str, params=None) -> str:
    """Translate a BigQuery SQL statement to Kusto (query or control command)."""
    if not sql or not sql.strip():
        raise UnsupportedQuery("empty statement")
    body = _bind_params(sql, params).strip().rstrip(";")
    upper = body.lstrip().upper()

    if upper.startswith("."):
        return body
    if upper.startswith("CREATE TABLE"):
        return _translate_create_table(body)
    if upper.startswith("UPDATE"):
        return _translate_update(body)
    if upper.startswith(("INSERT ", "MERGE ", "DELETE ", "DROP ", "TRUNCATE ")):
        raise UnsupportedQuery(
            "{} statements are not part of this app's surface and have no "
            "Kusto equivalent in this shim".format(upper.split()[0])
        )
    if upper.startswith(("SELECT", "WITH")):
        if upper.startswith("WITH"):
            raise UnsupportedQuery("common-table expressions are not supported; "
                                   "rewrite as a direct KQL query")
        return _translate_select(body)
    if upper.startswith(("SHOW ", "DESCRIBE", "DESC ")):
        table_m = re.search(r"(?:`([^`]+)`|([\w$.]+))\s*$", body)
        if table_m:
            return ".show table {} schema".format(
                to_adx_table((table_m.group(1) or table_m.group(2)).strip()))
        return ".show tables"
    raise UnsupportedQuery("cannot translate statement: {}".format(body[:120]))


# ── Kusto client ────────────────────────────────────────────────────────────

class _KustoSession:
    """Lazy, thread-safe ADX connection. Never constructed at import time."""

    _lock = threading.Lock()
    _client = None
    _failed = None

    @classmethod
    def get(cls):
        uri = _cluster_uri()
        if not uri:
            raise RuntimeError(
                "ADX_CLUSTER_URI is not set — Azure Data Explorer is not configured"
            )
        with cls._lock:
            if cls._client is not None:
                return cls._client
            from azure.kusto.data import KustoClient, KustoConnectionStringBuilder

            tenant = os.getenv("ADX_TENANT_ID", "").strip()
            client_id = os.getenv("ADX_CLIENT_ID", "").strip()
            client_secret = os.getenv("ADX_CLIENT_SECRET", "").strip()

            if client_id and tenant and client_secret:
                # Service principal — CI / local with a registered app.
                kcsb = KustoConnectionStringBuilder.with_aad_application_key_authentication(
                    uri, client_id, client_secret, tenant
                )
            elif client_id:
                # User-assigned managed identity (App Service / Container Apps).
                kcsb = KustoConnectionStringBuilder.with_azure_managed_identity(
                    uri, client_id
                )
            elif os.getenv("MSI_ENDPOINT") or os.getenv("IDENTITY_ENDPOINT"):
                # System-assigned managed identity on the Azure host.
                kcsb = KustoConnectionStringBuilder.with_azure_managed_identity(uri)
            else:
                # Developer workstation fallback.
                kcsb = KustoConnectionStringBuilder.with_azure_cli_authentication(uri)
            cls._client = KustoClient(kcsb)
            return cls._client

    @classmethod
    def reset(cls):
        with cls._lock:
            cls._client = None
            cls._failed = None


def _execute(command: str) -> list[Row]:
    client = _KustoSession.get()
    response = client.execute(_database(), command)
    return _rows_from_response(response)


def _rows_from_response(response) -> list[Row]:
    rows: list[Row] = []
    try:
        primary = response.primary_results[0]
    except (AttributeError, IndexError):
        return rows
    try:
        columns = [c.column_name for c in primary.columns]
    except AttributeError:
        columns = []
    for raw in primary:
        if isinstance(raw, dict):
            rows.append(Row(raw))
        elif columns:
            try:
                rows.append(Row({columns[i]: raw[i] for i in range(len(columns))}))
            except Exception:
                rows.append(Row({"value": raw}))
    return rows


# ── Public `bigquery` namespace ─────────────────────────────────────────────

class _BigQueryNamespace:
    """Module-shaped object so `from adx_bigquery import bigquery` works."""

    Client = None  # bound below
    ScalarQueryParameter = ScalarQueryParameter
    ArrayQueryParameter = ArrayQueryParameter
    QueryJobConfig = QueryJobConfig
    Dataset = Dataset
    SchemaField = SchemaField
    Table = Table
    Row = Row
    UnsupportedQuery = UnsupportedQuery


class Client:
    def __init__(self, project=None, location=None, **_):
        self.project = project or os.getenv("GCP_PROJECT_ID", "osintneoai")
        self.location = location or "eastus2"

    # -- query ------------------------------------------------------------
    def query(self, sql, job_config=None, **_):
        params = getattr(job_config, "query_parameters", None)
        kql = translate(sql, params)
        rows = _execute(kql)
        return _Job(rows, sql=kql)

    # -- streaming insert -------------------------------------------------
    def insert_rows_json(self, table, rows, selected_fields=None, **_):
        rows = [r for r in (rows or []) if isinstance(r, dict)]
        if not rows:
            return []
        adx_table = to_adx_table(str(table))
        try:
            self._ensure_table(adx_table, rows[0])
            self._ingest(adx_table, rows)
            return []
        except Exception as exc:  # mirrors BigQuery's error-list contract
            return [{"index": 0, "errors": [{"reason": "backend", "message": str(exc)}]}]

    def _ensure_table(self, adx_table: str, sample: dict) -> None:
        cols = ", ".join(
            "{}:{}".format(_sanitize(k), _infer_kusto_type(v)) for k, v in sample.items()
        )
        _execute(".create table ifnotexists {} ({})".format(adx_table, cols))

    def _ingest(self, adx_table: str, rows: list[dict]) -> None:
        columns = list(rows[0].keys())
        types = [_infer_kusto_type(rows[0].get(c)) for c in columns]
        tuples = []
        for r in rows:
            vals = []
            for c, t in zip(columns, types):
                vals.append(_kusto_literal(r.get(c), t))
            tuples.append("({})".format(", ".join(vals)))
        command = ".set-or-append {} <| datatable ({}) [{}]".format(
            adx_table,
            ", ".join("{}:{}".format(_sanitize(c), t) for c, t in zip(columns, types)),
            ", ".join(tuples),
        )
        _execute(command)

    # -- catalog ----------------------------------------------------------
    def list_datasets(self):
        try:
            tables = self._list_adx_tables()
        except Exception:
            tables = []
        present = set()
        for t in tables:
            for ds in _datasets():
                if t.startswith(_sanitize(ds) + "_"):
                    present.add(ds)
        for ds in _datasets():
            present.add(ds)
        return [Dataset(type("Ref", (), {"dataset_id": ds})()) for ds in sorted(present)]

    def list_tables(self, dataset):
        ds_id = getattr(dataset, "dataset_id", str(dataset))
        prefix = _sanitize(ds_id) + "_"
        try:
            tables = self._list_adx_tables()
        except Exception:
            tables = []
        out = []
        for t in tables:
            if t.startswith(prefix):
                out.append(type("TableRef", (), {
                    "table_id": t[len(prefix):],
                    "reference": to_bigquery_ref(t),
                })())
            elif t == _sanitize(ds_id):
                out.append(type("TableRef", (), {
                    "table_id": t,
                    "reference": to_bigquery_ref(t),
                })())
        return out

    def _list_adx_tables(self) -> list[str]:
        rows = _execute(".show tables")
        names = []
        for r in rows:
            name = r.get("TableName") or r.get("TableName") or r.get("name")
            if not name:
                for v in r.values():
                    name = v
                    break
            if name:
                names.append(str(name))
        return names

    def get_table(self, table_ref) -> Table:
        adx_table = to_adx_table(str(table_ref))
        schema_rows = _execute(".show table {} schema".format(adx_table))
        fields = []
        for r in schema_rows:
            name = r.get("ColumnName") or r.get("Name")
            ktype = r.get("ColumnType") or r.get("DataType") or "string"
            if name:
                fields.append(SchemaField(name, _kusto_to_bq(str(ktype))))
        count_rows = _execute("{} | count".format(adx_table))
        num_rows = 0
        if count_rows:
            for v in count_rows[0].values():
                try:
                    num_rows = int(v)
                except (TypeError, ValueError):
                    pass
        return Table(to_bigquery_ref(adx_table), schema=fields, num_rows=num_rows)

    # -- dataset DDL ------------------------------------------------------
    def dataset(self, dataset_id):
        return type("Ref", (), {
            "dataset_id": dataset_id,
            "project": self.project,
            "__str__": lambda self: "{}.{}".format(self.project, self.dataset_id),
        })()

    def get_dataset(self, dataset_ref):
        return Dataset(dataset_ref)

    def create_dataset(self, dataset, exists_ok=False, **_):
        # ADX databases are provisioned out of band; datasets are logical.
        if not exists_ok:
            raise RuntimeError("ADX database provisioning is out of band")
        return Dataset(getattr(dataset, "reference", dataset))


def _infer_kusto_type(value) -> str:
    if isinstance(value, bool):
        return "bool"
    if isinstance(value, int):
        return "long"
    if isinstance(value, float):
        return "real"
    if isinstance(value, (dict, list, tuple)):
        return "dynamic"
    return "string"


def _kusto_literal(value, ktype: str) -> str:
    if value is None:
        return "null()"
    if ktype == "dynamic":
        return _quote(json.dumps(value, default=str))
    if ktype == "bool":
        return "true" if value else "false"
    if ktype in ("long", "real"):
        return str(value)
    if ktype == "datetime":
        return "datetime({})".format(_quote(str(value)))
    return _quote(str(value))


_Client = Client
_BigQueryNamespace.Client = _Client

bigquery = _BigQueryNamespace()
