# order-pdf-workflow

주문 정보를 조회하고 선택한 상품의 PDF를 내려받아 가공·저장하며, 송장 등록 업무를 지원하는 PyQt 응용 프로그램입니다.

## 처리 흐름

`주문·상품 정보 입력 → 고객 API 조회 → PDF 다운로드·파일 처리 → 진행 상태 표시 및 결과 저장`

## 기술

- Python, PyQt5
- QThread, QMutex, QWaitCondition
- Requests, pypdf, pandas
- Qt Designer

## 개인 기여

- UI가 멈추지 않도록 PDF 다운로드 작업을 `QThread`로 분리했습니다.
- 이미 저장된 PDF를 확인해 중복 다운로드를 건너뛰도록 처리했습니다.
- `QMutex`와 `QWaitCondition`을 사용해 다운로드 일시정지·재개 흐름을 구현했습니다.
- 네트워크 또는 파일 처리 실패 시 다운로드를 재시도하도록 구성했습니다.
- 다운로드 중지 과정에서 발생하던 크래시와 멈춤 문제를 수정했습니다.

## 협업 범위

로그인, 주문 조회, 필터링, 송장 처리와 전체 UI는 공동 개발 범위입니다.

## 코드 위치

| 파일 | 내용 |
| --- | --- |
| [`download.py`](./download.py) | PDF 다운로드 스레드, 중복 확인, 일시정지·재개와 재시도 |
| [`main.py`](./main.py) | 주문 목록, 필터링, 다운로드·송장 처리 화면 흐름 |
| [`login.py`](./login.py) | 로그인 화면과 API 요청 시작점 |
| [`config.py`](./config.py) | 응용 프로그램 설정 화면 |
| [`ui/`](./ui/) | Qt Designer UI 원본 |

## 공개본 안내

API 주소는 `ORDER_API_BASE_URL` 환경변수로 대체했으며, 운영 계정·주문 데이터, PDF·Excel 문서, 이미지·폰트, 로컬 설정과 실행 파일을 제외했습니다.

이 저장소는 별도의 오픈소스 라이선스를 제공하지 않습니다.
