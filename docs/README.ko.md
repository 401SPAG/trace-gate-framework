# 문서 안내

[English](README.md) | **한국어** · [저장소 소개](../README.ko.md)

저장소 README에서 개념 아키텍처를 읽고, 구현 가이드와 예제로 실행 가능한 계약을 확인하십시오. 아래 상세 규격은 현재 국문입니다. 영문 문서 안내와 사용 가이드는 입문 경로이며 상세 규격 전체의 번역을 의미하지 않습니다.

## 목적별 읽기

| 목적 | 문서 | 언어·범위 |
|---|---|---|
| 프레임워크 이해 | [Core 규격](TRACE-GATE-FRAMEWORK.ko.md) | 국문; Core 전체 계약 |
| 문서·컨텍스트 관리 | [TRACE-DM](subframeworks/TRACE-DOCUMENT-MANAGEMENT.ko.md) | 국문; 정본 개정·접근·파생 표현·선택적 검색 |
| 에이전트 실행 중재 | [TRACE-AH](subframeworks/TRACE-AGENT-HARNESS.ko.md) | 국문; 모델·도구·검증기·체크포인트·제한된 하위 에이전트 |
| 범위별 이전 계획 | [TRACE-DM-MIGRATION](subframeworks/TRACE-DM-MIGRATION.ko.md) | 국문; 선택적 이전·참조·복구·전환 |
| 참조 구현 실행 | [국문 상세 가이드](REFERENCE-IMPLEMENTATION.ko.md) / [영문 사용 가이드](REFERENCE-IMPLEMENTATION.en.md) | 설치·adapter·한계·적합성 근거 |
| 결정적 예제 실행 | [한국어](../examples/README.ko.md) / [English](../examples/README.md) | 합성 로컬 입력 |
| 기여 | [국문 절차·합의](../CONTRIBUTING.md) / [영문 안내](../CONTRIBUTING.en.md) | 작업 절차·리뷰·통합 허락 |
| 이용 가능 범위 확인 | [한국어](../LICENSING.md) / [English](../LICENSING.en.md) | 자료별 적용 범위·기존 허락 |

## 공통 용어

| 용어 | 이 프로젝트에서의 의미 |
|---|---|
| TRACE | Trace, Restrict, Assemble, Confirm, Elevate의 다섯 원칙; 같은 이름의 별도 런타임 프레임워크와 구별 |
| Gate | 증거 기반 의사결정 지점; 판정 결과 자체가 운영 권한은 아님 |
| DM | Document Management, 문서 관리 |
| AH | Agent Harness, 에이전트 하네스 |
| 정본 문서(Canonical document) | 특정 주제의 기준으로 지정된 원본 |
| 파생 표현(Projection) | 요약·검색 인덱스 등 원본에서 유래한 표현; 원본을 대체하지 않음 |
| Receipt | 결정·관측을 관련 입력과 범위에 연결하는 기록 |
| 효과(Effect) | 대상 시스템에서 관측된 변경; 호출 시도·성공 보고와 구별 |
| 검증된 재개(Verified resumption) | 승인·컨텍스트·이력·범위·원래 한도를 확인한 후의 계속 실행 |
| 거버넌스 계약(Governance contract) | 책임 사이의 명시적 운영 조건; 소프트웨어 기록을 법적 계약으로 간주한다는 뜻은 아님 |

## 템플릿 묶음

- **Core:** [`request-receipt.yaml`](../templates/request-receipt.yaml), [`ticket.yaml`](../templates/ticket.yaml), [`evidence-manifest.yaml`](../templates/evidence-manifest.yaml), [`gate-decision.yaml`](../templates/gate-decision.yaml).
- **DM 접근·컨텍스트:** [`document-access-intent.yaml`](../templates/document-access-intent.yaml), [`document-read-profile.yaml`](../templates/document-read-profile.yaml), [`document-manifest.yaml`](../templates/document-manifest.yaml), [`document-gate-receipt.yaml`](../templates/document-gate-receipt.yaml).
- **선택적 의미 기반 검색:** [`document-embedding-profile.yaml`](../templates/document-embedding-profile.yaml), [`document-embedding-manifest.yaml`](../templates/document-embedding-manifest.yaml). 별도 벡터 그래프는 필수가 아닙니다.
- **AH 실행:** [`agent-run.yaml`](../templates/agent-run.yaml), [`tool-definition.yaml`](../templates/tool-definition.yaml), 선택적 [`subagent-task.yaml`](../templates/subagent-task.yaml).
- **연속성:** [`HANDOFF.md`](../templates/HANDOFF.md).
- **선택적 이전:** [`templates/`](../templates/)의 `document-migration-*`, `document-relocation-map.yaml`, `document-cutover-receipt.yaml`. 이전 규격에 따라 데이터 수신, 양측 전환, 업무 재개 허락을 구별합니다.

## 검증 근거와 유지관리

[관리 문서 manifest](managed-document-manifest.yaml)는 문서 식별자, 내용 기반 개정 식별자, 해시, 계보, 최신성, 접근 메타데이터를 기록합니다. 언어별 문서는 별도 artifact 식별자를 가지며 각 번역은 출처 정보로 원문을 식별합니다. 번역 갱신이 원문을 자동으로 개정하지 않습니다.

[공개 교정 기록](status/TRACE-GATE-HARDENING-PUBLIC-20261017.json)과 [상세 적합성 연결표](REFERENCE-IMPLEMENTATION.ko.md#9-교정-적합성-연결표--2026-10-17)는 합성 검증과 남은 운영 조건을 구별합니다. 호환성 변경은 [변경 기록](../CHANGELOG.md)을 확인하십시오. 문서를 갱신할 때 과거 receipt와 합의를 보존합니다.

[라이선스 전환](LICENSING-TRANSITION.ko.md)과 [1.1 명확화 검토](LICENSING-REVIEW-1.1.ko.md)는 보존하는 국문 이력입니다. 현행 법률 원문은 라이선스 안내에서 연결합니다.
