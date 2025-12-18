# Apify 플랫폼 포스트 데이터 수집기

Apify를 사용하여 다양한 플랫폼(Instagram, Facebook, Twitter 등)의 포스트 데이터를 수집하고 **이미지를 자동으로 저장**하는 Python 프로젝트입니다.

## 주요 기능

✨ **URL만 입력하면 자동으로:**
- 포스트 데이터 수집
- 이미지 다운로드 및 저장 (`images/` 폴더)
- 메타데이터 JSON 저장 (`data/` 폴더)

## 설치 방법

1. 가상환경 활성화:
```bash
# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

2. 패키지 설치:
```bash
pip install -r requirements.txt
```

3. 환경 변수 설정:
   - `.env.example` 파일을 `.env`로 복사
   - Apify API 토큰을 입력 (https://console.apify.com/account/integrations 에서 발급)

```bash
cp .env.example .env
```

## 사용 방법

### 1. 기본 사용법

`apify_scraper.py` 파일의 `main()` 함수에서 URL만 입력:

```python
run_input = {
    "directUrls": [
        "https://www.instagram.com/p/your_post_id/",  # 원하는 포스트 URL
    ],
    "resultsLimit": 10
}
```

실행:

```bash
python apify_scraper.py
```

### 2. 저장 위치

실행하면 자동으로 다음 구조가 생성됩니다:

```
vlm_image/
├── images/                          # 📷 다운로드된 이미지
│   ├── post_1_20231130_143025_img1.jpg
│   ├── post_1_20231130_143025_img2.jpg
│   └── ...
├── data/                            # 📄 메타데이터 (JSON)
│   ├── post_1_20231130_143025_metadata.json
│   └── ...
└── apify_scraper.py
```

### 3. 파일명 규칙

- 이미지: `post_{번호}_{타임스탬프}_img{이미지번호}.jpg`
- 메타데이터: `post_{번호}_{타임스탬프}_metadata.json`

## 설정

`apify_scraper.py` 파일에서 다음 항목을 수정하세요:

- `actor_id`: 사용할 Apify Actor ID (예: 'apify/instagram-scraper')
- `run_input["directUrls"]`: 수집할 포스트 URL 리스트

## 참고 자료

- [Apify 공식 문서](https://docs.apify.com/)
- [Apify Python Client](https://docs.apify.com/api/client/python)
- [Apify Store](https://apify.com/store) - 다양한 Actor 검색

