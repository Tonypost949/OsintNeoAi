# Public Redaction Policy

## Core rule

Local/private data is the source of truth and is never masked locally. The
public mirror is a separate export. A file is published only after it passes
the scanner.

## Names

Full names are **kept**. Do not replace a name with initials.

## Partial masking

| Data type | Public form | Rule |
|---|---|---|
| SSN | `***-**-1234` | keep last 4 |
| Phone | `(***) ***-1234` | keep last 4 |
| Email | `j***@example.com` | keep first character and domain |
| Street address | `123 M*** St` | keep house number and suffix |
| Date of birth | `**/**/1984` | keep year |
| ZIP | `123**` | keep first 3 |
| Driver license | `****1234` | keep last 4 |
| Passport | `****1234` | keep last 4 |
| Account / loan / policy | `****1234` | keep last 4 |
| IP, private/residential | `[PRIVATE_IP]` | never publish |
| IP, public infrastructure | unchanged | only with source/authority |

## Already-public records

If a record is already public, it is not masked — but only when the record
contains:

1. a direct `https://` source URL to the authoritative publisher, and
2. an authority citation (agency, court, recorder, statute, or official
   publication), and
3. a retrieved date.

The scanner still masks SSNs, financial account numbers, credentials, private
keys, and private/residential IPs in public records. Personal email addresses
and phone numbers are also masked: only official government/military
mailboxes, and phone numbers printed on a line that itself carries an
official `.gov`/`.us` URL, pass through. Do not republish a fullz-style record
just because one field appeared in a public index.

## Citation coverage

The export ships `CITATION_COVERAGE.json` and `CITATION_GAPS.csv` so missing
source URLs, authority lines, and legal-section links are visible instead of
silently implied. Records that lack required structured citations stay in
`review_queue/`.

## Citation requirements

Each published record should include:

```json
{
  "source_url": "https://...",
  "authority": "Orange County Superior Court",
  "citation": "Case No. ...; Cal. Civ. Code § ...",
  "retrieved_at": "2026-10-19T00:00:00Z",
  "legal_section": "https://.../LEGAL#..."
}
```

Missing source, authority, or legal-section linkage goes to `review_queue/`.

## Fail-closed behavior

- Secrets/tokens/private keys: quarantine the whole file.
- Unsupported binaries, PDFs, images, archives, databases: do not publish.
- Scanner error: abort the export; do not push partial output.
