# V3 현장 오류 사전 — SYNTHETIC 재현

모든 오류·빈 표 예시는 SYNTHETIC 파일에서 일부러 발생시켰다. 계획서 원본 셀은 수정하지 않았다.

셀은 실패한 줄부터 부분 실행하지 말고, 아래 최소 수정 줄을 고친 다음 해당 셀 전체를 다시 실행한다. 커널을 재시작했다면 선행 셀도 실행한다.

| 사례 / 셀 | 오류 마지막 줄 또는 관측 | 원인 | 다시 칠 최소 줄과 재실행 | 확인 방법 |
|---|---|---|---|---|
| usecols_typo / P1 | `ValueError: Usecols do not match columns, columns expected but not found: ['PAY_GBN_TYPO']` | usecols 컬럼명 불일치 | S1 5줄 C_GBN="PAY_GBN"; P1 전체 | ValueError 마지막 줄 |
| direct_column_typo / M1 | `AttributeError: 'DataFrame' object has no attribute 'GUNGU_TYPO'` | 셀 내부 컬럼명 오타 | M1 2줄 GUNGU_NM 복구; M1 전체 | S1 헤더와 대조 |
| keyerror_typo / A2 | `KeyError: 'CHILD_DISC_TYPO'` | DataFrame 조회 컬럼명 오타 | S1 6줄 C_DISC 복구; A2 전체 | KeyError |
| path_typo / S1 | `FileNotFoundError: [Errno 2] No such file or directory: SYNTHETIC_missing.csv (전체 경로는 로그)` | 경로 오타 | S1 2줄 PAY 수정; S1 전체 | FileNotFoundError |
| encoding / S1 | `UnicodeDecodeError: 'utf-8' codec can't decode byte 0xbe in position 0: invalid start byte` | cp949 파일을 utf-8로 읽음 | S1 4줄 ENC="cp949"; S1 전체 | UnicodeDecodeError |
| BOM_header / S1 | `SYNTHETIC: no exception (silent change or tolerated)` | UTF-8 BOM 실제 파일 | 로컬은 자동 제거; 현장 첫 헤더에 BOM이 남으면 ENC="utf-8-sig"; S1 | S1 첫 헤더가 SHOP_ID인지 확인 |
| parenthesis / P1 | `SyntaxError: '(' was never closed` | 닫는 괄호 누락 | P1 3줄 ): 복구; P1 전체 | SyntaxError |
| quote / S1 | `SyntaxError: unterminated string literal (detected at line 4)` | 닫는 따옴표 누락 | S1 4줄 따옴표 복구; S1 전체 | SyntaxError |
| indent / P1 | `IndentationError: expected an indented block after 'for' statement on line 2` | for 본문 들여쓰기 누락 | P1 4줄 앞 공백 4개; P1 전체 | IndentationError |
| skip_order / M5 | `NameError: name 'm' is not defined` | 커널 재시작 뒤 M5만 실행 | S1→M1→M2→M3→M4→M5 | NameError |
| duplicate_shop / M2 | `pandas.errors.InvalidIndexError: Reindexing only valid with uniquely valued Index objects` | SHOP_ID 중복으로 map의 키가 유일하지 않음 | 자동 삭제 금지; 중복 건수·키를 현장 내부 확인 후 보고, M1→M2 | InvalidIndexError |
| meal_value_typo / M2 | `SYNTHETIC: no exception (silent change or tolerated)` | 급식 코드 한글 값 오타 | S1 7줄 MEAL 복구; M2부터 필요한 후속 셀 | 예외 없음, M2 len=0을 독립 기대값과 대조 |
| done_value_typo / M2 | `SYNTHETIC: no exception (silent change or tolerated)` | 완료 값 오타 | S1 7줄 DONE 복구; M2부터 | 예외 없음, M2 len=0 |
| regime_방학 / M2 | `SYNTHETIC: no exception (silent change or tolerated)` | 레짐 한글 값 오타 | M2 10~11줄 해당 문자열 복구; M2→M4→M5 | 예외 없음; M4 레짐 이름·순서·합계 대조 |
| regime_전환 / M2 | `SYNTHETIC: no exception (silent change or tolerated)` | 레짐 한글 값 오타 | M2 10~11줄 해당 문자열 복구; M2→M4→M5 | 예외 없음; M4 레짐 이름·순서·합계 대조 |
| regime_학기 / M2 | `SYNTHETIC: no exception (silent change or tolerated)` | 레짐 한글 값 오타 | M2 10~11줄 해당 문자열 복구; M2→M4→M5 | 예외 없음; M4 레짐 이름·순서·합계 대조 |
| Y_typo / M6 | `SYNTHETIC: no exception (silent change or tolerated)` | 등록 Y 값 오타 | M6 5줄 Y 복구; M6 전체 | 예외 없음; U2 대상=0 |
| status01_typo / M6 | `SYNTHETIC: no exception (silent change or tolerated)` | 문자열 01의 선행 0 누락 | M6 11줄 01 복구; M6 전체 | 예외 없음; live=0, U2 총수는 그대로 |
| serviceN_typo / M6 | `SYNTHETIC: no exception (silent change or tolerated)` | 서비스 N 값 오타 | M6 11줄 N 복구; M6 전체 | 예외 없음; live=0 |
| after_A1_P1b / P1b | `KeyError: '아동급식카드'` | A1이 P1의 a를 덮어씀 | P1→P1b→P2 | KeyError 또는 중복 인덱스 pivot ValueError |
| after_A1_P2 / P2 | `KeyError: 'n'` | A1이 P1의 a를 덮어씀 | P1→P1b→P2 | KeyError 또는 중복 인덱스 pivot ValueError |

## 특히 위험한 조용한 실패 세 가지

1. MEAL 또는 DONE 오타: SYNTHETIC M2에서 0행이 돼도 셀은 성공한다. 현장 M2 확인 건수와 S1의 급식·완료 문자열을 함께 대조한다.
2. 방학·전환·학기 오타: SYNTHETIC M2의 전체 건수와 동 수는 바뀌지 않는다. 후속 M4를 실제 실행했을 때 레짐 문자열과 출력 순서가 달라지는 것을 확인했다. M4 마지막 세 행의 이름·순서·합계를 대조한다.
3. 01 또는 N 오타: SYNTHETIC U2 총수와 상태 교차표는 그대로인데 live만 0이 됐다. 체크리스트에는 live의 고정 기대값이 없어서 0만으로는 확실히 잡히지 않는다. M6 11줄의 `01`(문자열, 0 포함)과 `N`을 직접 대조한다.

UTF-8 BOM은 로컬 pandas 2.2.3에서 자동 제거돼 예외가 없었다. BOM을 오류로 꾸며 기록하지 않았다. 현장 S1 첫 헤더가 실제로 `\ufeffSHOP_ID`라면 체크리스트대로 ENC를 utf-8-sig로 바꾼다.

SHOP_ID 중복은 SYNTHETIC M2에서 InvalidIndexError로 재현했다. 임의로 중복을 제거하면 D-012 정의가 바뀔 수 있으므로 현장 내부에서 확인하고 보고한다.

A1 이후 P1b는 KeyError(아동급식카드), P2는 KeyError(n)로 재현했다. P1→P1b→P2를 실행해 복구했다. 커널 재시작 뒤 M5만 실행하면 NameError(m), S1→M1→M2→M3→M4→M5로 복구했다.

전체 traceback·경고·실행 줄·stdout은 `C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_errors.json` 및 `C:\Users\dieuetla22382\OneDrive - KookminUNIV\바탕 화면\2026_데이터안심구역_경진대회\synthetic\visit3\out_SYNTHETIC\SYNTHETIC_errors`에 있다.
