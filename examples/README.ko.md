# 참조 예제

[English](README.md) | **한국어** · [저장소 소개](../README.ko.md)

README의 가상환경 설치를 마친 뒤 저장소 루트에서 실행합니다.

## Gate 평가

```bash
.venv/bin/python scripts/evaluate_gate.py \
  templates/gate-decision.yaml examples/gate-facts.yaml
```

평가기는 정책과 합성 facts에서 결과와 receipt를 계산합니다. `pass`는 운영 승인이 아닙니다. 실제 적용에서는 신뢰된 확인 주체가 증거 참조의 진위를 검증해야 합니다.

## 결정적 에이전트 예제

```bash
.venv/bin/python examples/runtime_demo.py
```

예제는 모델·도구·검증기에 로컬 시험용 adapter를 사용합니다. 실제 모델을 호출하거나 원격 변경을 수행하지 않습니다. 출력은 런타임 계약의 예시이며 운영 승인 receipt로 사용하지 않습니다.

실제 도구를 연결하기 전에 검증된 Request Receipt, 범위가 제한된 Tool Definition, 승인 확인, 효과 관측과 적절한 실행기를 갖추십시오. [adapter 요구사항과 한계](../docs/REFERENCE-IMPLEMENTATION.ko.md)를 확인해야 합니다. 미확정 효과는 차단을 유지하며, 타임아웃이나 저장된 체크포인트만으로 재실행이 안전하다고 판단하지 않습니다.

실행 예제는 [LICENSE-CODE](../LICENSE-CODE), 주변 설명은 [문서 조건](../LICENSING.md)을 따릅니다.
