"""
Apify를 사용하여 플랫폼 포스트 데이터를 가져오고 이미지를 저장하는 스크립트
"""
import os
import json
import requests
from pathlib import Path
from datetime import datetime
from urllib.parse import urlparse
from apify_client import ApifyClient
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

# 기본 저장 경로 설정
BASE_DIR = Path(__file__).parent
IMAGES_DIR = BASE_DIR / "images"
DATA_DIR = BASE_DIR / "data"


def create_directories():
    """필요한 디렉토리를 생성합니다."""
    IMAGES_DIR.mkdir(exist_ok=True)
    DATA_DIR.mkdir(exist_ok=True)


def download_image(image_url: str, save_path: Path) -> bool:
    """
    이미지를 다운로드하여 저장합니다.
    
    Args:
        image_url (str): 다운로드할 이미지 URL
        save_path (Path): 저장할 경로
    
    Returns:
        bool: 다운로드 성공 여부
    """
    try:
        response = requests.get(image_url, timeout=30, stream=True)
        response.raise_for_status()
        
        # 파일 저장
        with open(save_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        print(f"✓ 이미지 저장 완료: {save_path.name}")
        return True
        
    except Exception as e:
        print(f"✗ 이미지 다운로드 실패 ({image_url}): {e}")
        return False


def save_metadata(post_data: dict, save_path: Path):
    """
    포스트 메타데이터를 JSON 파일로 저장합니다.
    
    Args:
        post_data (dict): 포스트 데이터
        save_path (Path): 저장할 경로
    """
    try:
        with open(save_path, 'w', encoding='utf-8') as f:
            json.dump(post_data, f, ensure_ascii=False, indent=2)
        print(f"✓ 메타데이터 저장 완료: {save_path.name}")
    except Exception as e:
        print(f"✗ 메타데이터 저장 실패: {e}")


def fetch_platform_posts(actor_id: str, run_input: dict, save_images: bool = True):
    """
    Apify Actor를 실행하여 플랫폼 포스트 데이터를 가져오고 이미지를 저장합니다.
    
    Args:
        actor_id (str): Apify Actor ID (예: 'apify/instagram-scraper')
        run_input (dict): Actor 실행에 필요한 입력 파라미터
        save_images (bool): 이미지 자동 저장 여부 (기본: True)
    
    Returns:
        list: 수집된 포스트 데이터 리스트
    """
    # Apify API 토큰 가져오기
    api_token = os.getenv('APIFY_API_TOKEN')
    
    if not api_token:
        raise ValueError("APIFY_API_TOKEN이 설정되지 않았습니다. .env 파일을 확인하세요.")
    
    # 디렉토리 생성
    if save_images:
        create_directories()
    
    # Apify 클라이언트 초기화
    client = ApifyClient(api_token)
    
    print(f"\n{'='*60}")
    print(f"Actor 실행 중: {actor_id}")
    print(f"입력 파라미터: {run_input}")
    print(f"{'='*60}\n")
    
    # Actor 실행
    run = client.actor(actor_id).call(run_input=run_input)
    
    # 결과 가져오기 및 처리
    results = []
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    for idx, item in enumerate(client.dataset(run["defaultDatasetId"]).iterate_items(), 1):
        results.append(item)
        
        if save_images:
            print(f"\n--- 포스트 {idx} 처리 중 ---")
            process_post_images(item, idx, timestamp)
    
    print(f"\n{'='*60}")
    print(f"✓ 총 {len(results)}개의 포스트를 수집했습니다.")
    print(f"✓ 이미지 저장 위치: {IMAGES_DIR}")
    print(f"✓ 메타데이터 저장 위치: {DATA_DIR}")
    print(f"{'='*60}\n")
    
    return results


def process_post_images(post_data: dict, post_idx: int, timestamp: str):
    """
    포스트에서 이미지를 추출하고 저장합니다.
    
    Args:
        post_data (dict): 포스트 데이터
        post_idx (int): 포스트 인덱스
        timestamp (str): 타임스탬프
    """
    # 이미지 URL 추출 (다양한 키 이름 시도)
    image_urls = []
    possible_keys = [
        'displayUrl', 'imageUrl', 'url', 'images', 
        'displayUrls', 'imageUrls', 'media', 'mediaUrls'
    ]
    
    for key in possible_keys:
        if key in post_data:
            value = post_data[key]
            if isinstance(value, str):
                image_urls.append(value)
            elif isinstance(value, list):
                image_urls.extend([url for url in value if isinstance(url, str)])
    
    # 중복 제거
    image_urls = list(set(image_urls))
    
    if not image_urls:
        print(f"  이미지 URL을 찾을 수 없습니다.")
        return
    
    print(f"  발견된 이미지: {len(image_urls)}개")
    
    # 각 이미지 다운로드
    for img_idx, image_url in enumerate(image_urls, 1):
        # 파일명 생성
        ext = Path(urlparse(image_url).path).suffix or '.jpg'
        filename = f"post_{post_idx}_{timestamp}_img{img_idx}{ext}"
        save_path = IMAGES_DIR / filename
        
        # 이미지 다운로드
        download_image(image_url, save_path)
    
    # 메타데이터 저장
    metadata_filename = f"post_{post_idx}_{timestamp}_metadata.json"
    metadata_path = DATA_DIR / metadata_filename
    save_metadata(post_data, metadata_path)


def main():
    """
    메인 실행 함수
    
    URL만 입력하면 자동으로:
    1. Apify를 통해 포스트 데이터 수집
    2. 이미지를 images/ 폴더에 저장
    3. 메타데이터를 data/ 폴더에 JSON으로 저장
    """
    # 예시: Instagram 포스트 스크래핑
    # 실제 사용 시 적절한 Actor ID와 파라미터로 변경하세요
    
    actor_id = "apify/instagram-scraper"  # 사용할 Actor ID
    
    # URL만 입력하면 됩니다!
    run_input = {
        "directUrls": [
            "https://www.instagram.com/p/DQdRQseE1t0/",
            "https://www.instagram.com/p/DQ_mqcIE8FB/?img_index=7"
        ],
        "resultsLimit": 10
    }
    
    try:
        # 포스트 수집 및 이미지 자동 저장
        posts = fetch_platform_posts(actor_id, run_input, save_images=True)
        
        print(f"\n완료! 수집된 포스트: {len(posts)}개")
        print(f"이미지 확인: {IMAGES_DIR.absolute()}")
        print(f"메타데이터 확인: {DATA_DIR.absolute()}")
            
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")


if __name__ == "__main__":
    main()

