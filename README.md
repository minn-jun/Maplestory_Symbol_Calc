# MapleStory Symbol Optimizer

메이플스토리 캐릭터의 심볼 정보를 Nexon Open API로 조회하고, 목표 포스까지 도달하는 최소 비용 강화 경로를 계산하는 데스크톱 프로그램입니다.

## 주요 기능

- Nexon Open API 기반 최신 캐릭터/심볼 정보 조회
- 아케인심볼, 어센틱심볼, 그랜드 어센틱심볼 구분
- 어센틱 포스 계산 시 일반 어센틱 + 그랜드 어센틱 합산
- 기어드락 심볼 비용 및 요구 레벨 반영
- PySide6 기반 GUI
- meet-in-the-middle 방식의 최소 비용 경로 계산

## 실행 준비

```bash
pip install -r requirements.txt
```

API 키는 `.env` 파일로 관리합니다.

```bash
NEXON_API_KEY=your_nexon_open_api_key_here
```

`.env`는 Git에 포함되지 않습니다. 처음 설정할 때는 `.env.example`을 참고해 `.env` 파일을 만들면 됩니다.

## 실행

```bash
python main.py
```

## 파일 구조

- `main.py`: 앱 실행 진입점
- `app.py`: PySide6 GUI
- `api_handler.py`: Nexon Open API 호출
- `symbol_data.py`: 심볼 지역, 비용, 포스 데이터
- `optimizer.py`: 최소 비용 경로 계산
- `config.py`: `.env` 기반 API 키 로드

## 데이터 기준

심볼 강화 비용은 코드 내부에서 만 메소 단위로 보관하고, 계산 결과는 메소 단위로 출력합니다.

예: `3650` -> `36,500,000` 메소
