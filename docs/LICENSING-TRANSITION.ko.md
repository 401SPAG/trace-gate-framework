# 2026-11-14 라이선스 전환 기록

- 목적: 문서의 상업적 이용·수정본 공유와 코드의 상업적 이용·수정본 외부 배포를 제한하는 신규 공개 정책 적용.
- 변경 전 기준: [`dd69c7711ce987e7f51bd9ea364148a63954ff03`](https://github.com/401SPAG/trace-gate-framework/tree/dd69c7711ce987e7f51bd9ea364148a63954ff03).
- 적용 시작: 해당 기준 커밋 뒤에서 이 전환 기록과 새 라이선스를 함께 도입하는 변경 커밋. Git 이력으로 식별하며 날짜만으로 기존 자료의 권한을 변경하지 않는다.
- 이전 원문: [`licenses/CC-BY-4.0.txt`](../licenses/CC-BY-4.0.txt). 기준 커밋의 `LICENSE`와 바이트 단위로 동일하게 보존한다.
- 기준 파일 목록: [`licensing/transition-2026-11-14.json`](licensing/transition-2026-11-14.json). 변경 전 전체 추적 파일의 Git blob ID, SHA-256, 크기를 기록한다.
- 현재 조건: [적용 범위](../LICENSING.md), [문서 CC BY-NC-ND 4.0](../LICENSE), [코드 조건](../LICENSE-CODE), [기여 허락](../CONTRIBUTING.md).

## 기존 공개분의 보존

기준 커밋에는 CC BY 4.0 법률문, 문서·도표·템플릿에 대한 README 고지와 기여물에 대한 CONTRIBUTING 고지가 있었다. 이 기록은 모든 파일의 권리 귀속이나 과거 허락 범위를 확정하는 법률 감사가 아니다. 코드에 과거 CC BY 등 허락이 유효하게 적용된 경우 그 권한도 유지한다. 불명확한 범위를 새 제한으로 소급하여 확정하지 않는다.

이미 유효하게 부여된 CC BY 권한은 해당 조건을 준수하는 한 유지된다. 예전 커밋·태그·배포물은 다시 작성하지 않으며, 동일한 기존 내용이 최신 버전에 포함되어 있다는 이유로 기존 이용 권한이 소멸하지 않는다. 신규 제한은 새로 허락할 수 있는 보호 대상 표현에 적용된다. 기존 표현을 변경 없이 재게시하거나 버전 번호만 올리는 것으로 새 독점권을 만들지 않는다.

제3자 기여물을 새 조건으로 제공하려면 필요한 권한을 확인해야 한다. 과거 기여를 현재 CONTRIBUTING 동의로 소급 간주하지 않는다. 새 기여에는 명시적 기여 확인을 받고, 확인되지 않은 기여는 병합하지 않는다.

## 변경 및 검증 범위

1. 공식 CC BY-NC-ND 4.0 법률문을 수정 없이 `LICENSE`에 수록한다.
2. 코드 조건을 별도 파일로 제공하고 공식 기여 목적의 수정·공유 예외를 둔다.
3. README, CONTRIBUTING 및 Core·DM·AH·Migration 문서의 현행 고지를 일치시킨다.
4. Python 배포 버전 `2.0.0`과 라이선스 메타데이터를 설정하고 wheel·sdist에 적용 범위와 역사적 근거를 동봉한다. 실행 로직과 Core·DM·AH 계약 버전은 유지한다.
5. TRACE-DM 문서 manifest의 등록·해시·크기를 갱신하고 템플릿 검증, 전체 회귀 테스트, 배포물 포함 파일을 확인한다. 실제 실행 결과와 게시 커밋은 연구 세션 TRACE-DM 검증 영수증에 기록한다.

이 기록의 작성만으로 독립 법률 검토·권리 귀속 감사·실제 서비스 운영 검증을 완료했다고 주장하지 않는다.

## 후속 코드 1.1 명확화

최초 전환은 [`4991ee4f1c2f9d472fc1e23ca5133fafe2b28826`](https://github.com/401SPAG/trace-gate-framework/commit/4991ee4f1c2f9d472fc1e23ca5133fafe2b28826)에서 반영되었다. 이를 기준으로 [1.1 검토 기록](LICENSING-REVIEW-1.1.ko.md)과 코드 라이선스 1.1을 함께 도입하는 후속 커밋부터 명확화된 새 허락을 제공한다. 패키지 버전은 `2.0.1`로 구별한다.

기준 커밋의 코드 1.0과 CONTRIBUTING은 각각 [`licenses/401SPAG-NC-ND-1.0.txt`](../licenses/401SPAG-NC-ND-1.0.txt), [`licenses/CONTRIBUTING-1.0.txt`](../licenses/CONTRIBUTING-1.0.txt)에 원문 그대로 보존한다. 이미 유효하게 부여된 1.0의 권한과 실제로 체결된 기여 합의를 후속 파일 편집만으로 바꾸지 않는다. 최초 CC BY 기준 파일 목록과 기존 배포 이력도 유지한다.

## 근거

- [CC BY-NC-ND 4.0 공식 법률문](https://creativecommons.org/licenses/by-nc-nd/4.0/legalcode.en): 비상업적 원본 공유와 비공개 개작, 개작물 공유 제한, 예외 및 권리 범위.
- [Creative Commons FAQ](https://creativecommons.org/faq/): 기존 허락의 철회 불가, 소프트웨어에 대한 별도 라이선스 고려.
- [Open Source Definition](https://opensource.org/osd): 상업적 사용·수정본 배포 제한과 오픈소스 표시의 구분.
- [Python Packaging User Guide](https://packaging.python.org/en/latest/guides/writing-pyproject-toml/#license-and-license-files): 배포 라이선스 표현과 동봉 파일.
