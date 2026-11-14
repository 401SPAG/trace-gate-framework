# Contributing

**English guide and terms translation** | [한국어 원문](CONTRIBUTING.md)

Improvements to TRACE-GATE are welcome. This English guide translates the current workflow and explains **TRACE-GATE Contribution Terms 1.1** in [CONTRIBUTING.md](CONTRIBUTING.md). It is not a separate contribution agreement and does not change existing permissions. A consent record must identify the original terms, their commit or preserved text, the recipient, and the contribution being licensed.

## Proposal principles

- Explain the actual failure pattern a new procedure addresses.
- Make Gates mechanically decidable where possible.
- Separate implementation completion from operating-authority promotion.
- Keep failures and unknown outcomes visible.
- Do not include secrets, personal data, or internal system identifiers in evidence examples.

## Change workflow

1. Describe the problem and expected outcome in an issue.
2. Use a narrowly scoped branch and pull request.
3. Update examples and templates affected by the changed principle.
4. Check Markdown/Mermaid rendering, language-counterpart meaning and links. Label a partial translation's scope.
5. Include document versions and migration notes for breaking changes.
6. For a subframework change, state its Framework ID, independent version and compatible Core version.

## Pull request checklist

- [ ] The problem and purpose are clear.
- [ ] Unrelated changes are excluded.
- [ ] Affected templates and language counterparts are current.
- [ ] Mermaid fences are closed and the document renders correctly.
- [ ] No secrets or internal paths are exposed.
- [ ] Subframework compatibility and relevant templates have been checked.
- [ ] Remaining limitations and follow-up work are recorded.
- [ ] Review permission is distinguished from integration/distribution permission, and any required express consent is recorded.
- [ ] Third-party material, earlier licenses and required permissions are identified.

## Local validation

```bash
python3.12 -m venv .venv
.venv/bin/python -m pip install -e '.[dev]'
.venv/bin/python scripts/update_document_manifest.py
.venv/bin/python scripts/validate_templates.py
.venv/bin/python -m pytest -q
```

For a new Markdown document, first register a metadata envelope in `docs/managed-document-manifest.yaml`; otherwise the refresh command rejects it. Refresh revisions, SHA-256, sizes and freshness after edits. Do not embed a document's own hash in its body. Link translations to their sources with distinct artifact identities.

A new execution contract needs its JSON Schema, negative semantic tests and documentation examples. Do not hard-code a successful Gate status in a fixture; let the evaluator derive it from reproducible evidence.

## Contribution permissions

Documentation is published under [CC BY-NC-ND 4.0](LICENSE) and covered software under [401SPAG Noncommercial Software License 1.1](LICENSE-CODE). [LICENSING.md](LICENSING.md) identifies material scope and preserves earlier permissions, including code license 1.0 and CC BY. Public recipient permissions and additional grants from a contributor to a named recipient are separate.

### Proposals to the official repository

For existing software, **LICENSE-CODE section 5** is the operative contribution exception. For existing documentation, the rights holder separately permits, within the rights they can grant, copying, modification and sharing of patches, review branches and forks needed to propose, review, test and integrate improvements into [401SPAG/trace-gate-framework](https://github.com/401SPAG/trace-gate-framework). This limited purpose also covers commercially sponsored contributions. Documentation reviewers may copy, review and test for that same purpose.

Label contribution copies as unofficial review copies, retain notices, and preserve reasonable evidence of the contribution purpose, such as an issue, PR or draft proposal. Rejected or withdrawn proposals may remain as contribution history, but may not become a general modified release under this exception. The exception does not authorize general modified distributions, customer delivery or commercial operation. Permission to work on existing material does not itself grant rights in a contributor's new work.

The documentation permission is separate from the CC legal text and does not alter it. Publishing a full translation outside the contribution purpose requires another applicable permission. Independent viewing/forking rights under GitHub's terms remain independent. Default contribution permissions under applicable platform terms must also be distinguished from the **additional** integration/commercial-sublicensing agreement below. Submission alone is not treated as assent to that additional agreement.

### Express confirmation of rights

Contributors distinguish review-only permission from permission to integrate, publish and commercially sublicense. The confirmations below describe an additional agreement only when a contributor actually checks or records agreement to the identified terms. A review-only grant is not, by itself, permission to merge and distribute. Independently granted rights remain available.

Record the following in the PR or a linked agreement. Keep a contract containing personal information private when appropriate and put only its reference in the PR.

| Field | Required record |
|---|---|
| Rights holder and signing authority | Actual individual/legal name and any employer or representative authority needed |
| Integration-grant recipient | The actual person or business receiving permission, whether D. JEONG or a 401SPAG-related party, and a reference identifying that party. The brand name alone does not establish a separate entity or joint recipients |
| Subject | PR, covered commit SHA/files, third-party material and exclusions |
| Terms version | TRACE-GATE Contribution Terms 1.1 and the source document's commit or preserved agreement text |
| Consent | Review-only or integration/distribution grant, person assenting and time; identify whether later commits are covered or obtain a new confirmation |

**Translation of the review-only confirmation**

> I have authority to license the identified part of my contribution. I grant review participants a nonexclusive, royalty-free right to copy, run, modify and share that part for reviewing a proposal to the official repository. This includes commercially sponsored review, but this permission alone does not authorize an official release, customer delivery, commercial operation or commercial sublicensing. If the proposal is rejected or withdrawn, review copies already made may be retained as proposal history. This grant is limited to my rights in protected expression and does not withdraw separately granted rights.

**Translation of the integration/distribution confirmation**

> I hold the necessary rights in the identified contribution and have obtained required permissions, including from my employer where applicable. I have identified third-party material and exclusions. I grant the recipient identified in the agreement record a worldwide, nonexclusive, royalty-free right, for the copyright term, to copy, modify, integrate, publish, distribute and sublicense that part. This includes publication under the applicable CC BY-NC-ND 4.0 or code license 1.1 and separate sublicensing that permits commercial use and distribution of modified versions. While the recipient complies, I will not revoke this grant to the extent permitted by law. I retain copyright; I do not transfer ownership, automatically sublicense third-party rights, or make a blanket waiver of moral rights. Patent and trademark rights are not granted without a separate agreement, and rights that cannot lawfully be restricted remain intact.

Use the identified [Korean source terms](CONTRIBUTING.md) and a clear agreement record when documenting consent; these translated passages are not an independent replacement for that record.

Consent verification is currently a **manual merge requirement**. Passing CI or leaving a checklist unchecked is not proof of consent. Do not merge new contributions when the recipient, subject, authority, terms version or consent is unclear. A rights holder maintaining their own material is recorded separately from obtaining new permissions from an outside contributor. A later CONTRIBUTING revision does not automatically amend earlier agreements or contributions.

Questions and separate permissions: **[mail@401spag.com](mailto:mail@401spag.com)**.
