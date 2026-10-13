# V3 셀별 타이핑 위험 토큰

오타 재현 결과는 SYNTHETIC 검증이며 실결과가 아니다. 줄 번호는 계획서 코드 블록 기준이다.

| 셀 (줄 수) | 오류가 나는 오타 | 조용히 결과가 바뀌는 오타 / 대조할 토큰 |
|---|---|---|
| S1 (9) | 2~4줄 경로·r""·따옴표, 5~6줄 컬럼명; 한글 경로를 따옴표 안에 | 7줄 아동급식카드·완료; ENC utf-8 / utf-8-sig; 상수 밖 컬럼명은 M1·M6·A1에도 있음 |
| P1 (13) | 2~3줄 read_csv 괄호·콜론, 4~7줄 공백 4개, level=[0, 1] | .str[:6], keep_default_na=False, >0, <202306; 빈 ym을 이전 기간으로 읽지 않기 |
| P1b (1) | a.loc["아동급식카드"] 따옴표·대괄호, A1 뒤 a 덮어쓰기 | 급식 문자열 정확히; A1보다 먼저 실행 |
| P2 (6) | isin([...]), pivot 인자, unstack() | 행복페이·카드·대구로페이; .str[4:6], 01·02·08, .str[:4]; 빈 yr 줄 제외 |
| P3 (12) | set(), {}, \|=, set(sub[C_CUST]), groupby 들여쓰기 | <202306에는 빈 ym도 들어감; 해당 코드는 체크리스트대로 읽지 않기 |
| M1 (8) | GUNGU_NM·DONG_NM 직접 컬럼명, set_index("SHOP_ID") | 동 키의 "\|" 빠뜨림; Y 대소문자; 빈 군구·빈 동은 문자열 키로 남음 |
| M2 (13) | & 조건마다 괄호, np.where 두 번 괄호, d2 선행 실행 | MEAL·DONE; >=202306와 <=202506; 방학 01·02·08, 전환 07·12, 학기 |
| M3 (10) | ~ch[C_GBN].isin(MEAL), gs.append, level=0 | ~ 누락은 일반 결제를 급식으로 바꿈; DONE·기간; gp 합과 g 합 둘 다 확인 |
| M4 (9) | agg의 n=·n_shop=·n_cust=, \|, tt[bad]=np.nan | <5·<3·<5, k==1, 레짐 순서 방학·전환·학기; utf-8-sig |
| M5 (13) | .loc[mask, [열들]], [["n",...]], LQ 겹괄호 | k[k==1], .round(3), shops<3; 유효 억제 손계산 식; 분모와 분자 뒤바뀜 |
| M6 (12) | set_index, unstack(fill_value=0), e2[e2<3]=np.nan | Y·01·N, meal==0와 gen>0; 01의 선행 0 누락은 예외 없이 live 변경 |
| A1 (15) | NUM 두 줄 리스트, for 본문 들여쓰기·콜론, ar·gh | errors="coerce", fillna(0), //500, MEAL; 15줄 그대로 유지, a 덮어쓰기 |
| A2 (7) | .abs().le(1).mean(), quantile([.1,...]) | C_TOT·C_APP·C_DISC, -, >0, //500*500; round(3) |
| A3 (9) | .join(hg, how="outer"), .loc[bad,[...]] | //500 후 *500, <5, \|, index.name, utf-8-sig; 원본은 n_general을 가리지 않음 |
| A4 (4) | groupby(["ym","bin"]), reset_index(), tail(1) | sort_values("n"), //500*500; 현장 실행 조건은 여전히 해당 없음 |

한글 값은 오류가 없어도 다른 범주가 된다. 따옴표 안 값은 인쇄본과 글자 단위로 대조한다. 억제 임계값·기간·정의는 수정하지 않는다.
