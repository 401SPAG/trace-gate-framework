# 참조 예제

[English](README.md) | **한국어** · [저장소 소개](../README.ko.md)

README의 가상환경 설치를 마친 뒤 저장소 루트에서 실행합니다.

## Gate 평가

```bash
.venv/bin/python scripts/evaluate_gate.py \
  templates/gate-decision.yaml examples/gate-facts.yaml
```

[예제 입력](gate-facts.yaml)의 성공률은 99.5%이고 중복 쓰기와 금지된 변경은 각각 0건입니다. 복구 리허설도 통과했습니다. 이 값들이 최소 성공률 99%를 포함한 [정책 조건](../templates/gate-decision.yaml)을 충족하므로 평가기는 상태가 `pass`인 영수증을 반환합니다. 운영 환경에서는 신뢰할 수 있는 확인 주체가 인용된 증거의 진위를 검증하고, 권한을 가진 주체가 승격을 별도로 승인해야 합니다.

## 결정적 에이전트 예제

```bash
.venv/bin/python examples/runtime_demo.py
```

[실행 예제](runtime_demo.py)는 로컬 도구 `status.read`로 수집기 상태를 조회합니다. 도구는 `staging-only`를 반환하고 검증기는 미리 정해진 답변에 이 문구가 들어 있는지 확인합니다. 출력은 이 로컬 실행의 기록입니다. 실제 모델 호출, 원격 쓰기, 운영 권한 부여는 일어나지 않습니다.

실제 도구를 연결하기 전에 검증된 Request Receipt, 범위가 제한된 Tool Definition, 승인 확인, 효과 관측과 적절한 실행기를 갖추십시오. [adapter 요구사항과 한계](../docs/REFERENCE-IMPLEMENTATION.ko.md)를 확인해야 합니다. 미확정 효과는 차단을 유지하며, 타임아웃이나 저장된 체크포인트만으로 재실행이 안전하다고 판단하지 않습니다.

실행 예제는 [LICENSE-CODE](../LICENSE-CODE), 주변 설명은 [문서 조건](../LICENSING.md)을 따릅니다.
