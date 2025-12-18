"""
Gemini VLM(Vision Language Model) 이미지 분석 테스트 스크립트

기능:
1. 기준정보 엑셀 파싱 (마케팅 기준정보 + 의류 카테고리)
2. 이미지 분석 (Gemini Pro Vision)
3. 결과를 엑셀로 출력 (Cat, Subcat, Key, Value 형식)
"""
import os
import json
import time
from pathlib import Path
from datetime import datetime
from io import BytesIO
from google import genai
from google.genai import types
import pandas as pd
from PIL import Image as PILImage
from openpyxl.drawing.image import Image as XLImage
from dotenv import load_dotenv

# 기준정보 Python 파일에서 import
from category_attributes import (
    COMMON_ATTRIBUTES,
    CATEGORY_ATTRIBUTES_MAP,
    BACKGROUND_ATTRIBUTES,
    STYLING_ATTRIBUTES,
    MODEL_ATTRIBUTES
)

# 환경 변수 로드
load_dotenv()

# 기본 경로 설정
BASE_DIR = Path(__file__).parent
IMAGES_DIR = BASE_DIR  # 루트 폴더의 이미지 분석
DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = BASE_DIR / "output"
REFERENCE_DIR = BASE_DIR / "reference"

# 기준정보 엑셀 파일 경로
MARKETING_REF_FILE = BASE_DIR / "마케팅 기준정보.xlsx"
CATEGORY_REF_FILE = BASE_DIR / "F&F_odd key_values_ver.02_251201.xlsx"


def setup_gemini():
    """Gemini API 설정"""
    api_key = os.getenv('GOOGLE_API_KEY')
    
    if not api_key:
        raise ValueError(
            "GOOGLE_API_KEY가 설정되지 않았습니다.\n"
            ".env 파일에 다음을 추가하세요:\n"
            "GOOGLE_API_KEY=your_api_key_here\n\n"
            "API 키 발급: https://aistudio.google.com/app/apikey"
        )
    
    # 새로운 SDK 방식
    client = genai.Client(api_key=api_key)
    return client


# =============================================================================
# 기준정보 파싱 함수들
# =============================================================================

def parse_marketing_reference(file_path: str = None) -> dict:
    """마케팅 기준정보 엑셀을 파싱합니다."""
    file_path = file_path or MARKETING_REF_FILE
    
    if not Path(file_path).exists():
        print(f"⚠️ 마케팅 기준정보 파일이 없습니다: {file_path}")
        return {}
    
    df = pd.read_excel(file_path, header=None)
    reference = {}
    
    for col_idx in range(1, len(df.columns)):
        col_data = df.iloc[:, col_idx].dropna().tolist()
        
        if len(col_data) >= 2:
            key_name = str(col_data[0]).strip()
            values = [str(v).strip() for v in col_data[1:] if pd.notna(v) and str(v).strip()]
            
            if key_name and not key_name[0].isascii():
                reference[key_name] = values
    
    print(f"✓ 마케팅 기준정보 로드 완료: {len(reference)}개 카테고리")
    return reference


def parse_category_reference(file_path: str = None) -> dict:
    """의류 카테고리 기준정보 엑셀을 파싱합니다."""
    file_path = file_path or CATEGORY_REF_FILE
    
    if not Path(file_path).exists():
        print(f"⚠️ 카테고리 기준정보 파일이 없습니다: {file_path}")
        return {}
    
    df = pd.read_excel(file_path)
    
    reference = {}
    for cat in df['cat'].unique():
        sub_cats = df[df['cat'] == cat]['sub_cat'].dropna().tolist()
        reference[cat] = sub_cats
    
    print(f"✓ 카테고리 기준정보 로드 완료: {len(reference)}개 대분류")
    return reference


def load_all_references() -> dict:
    """모든 기준정보를 로드합니다."""
    return {
        "marketing": parse_marketing_reference(),
        "category": parse_category_reference()
    }


def save_references_to_json(references: dict, output_path: str = None):
    """파싱된 기준정보를 JSON 파일로 저장합니다."""
    REFERENCE_DIR.mkdir(exist_ok=True)
    output_path = output_path or (REFERENCE_DIR / "parsed_references.json")
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(references, f, ensure_ascii=False, indent=2)
    
    print(f"✓ 기준정보 JSON 저장 완료: {output_path}")
    return output_path


# =============================================================================
# 이미지 분석 함수들
# =============================================================================

def encode_image(image_path: str) -> bytes:
    """이미지를 바이트로 읽습니다."""
    with open(image_path, 'rb') as f:
        return f.read()


def analyze_image(client, image_path: str, analysis_prompt: str) -> dict:
    """Gemini를 사용하여 이미지를 분석합니다."""
    try:
        image_data = encode_image(image_path)
        
        # 새로운 SDK 방식으로 이미지 파트 생성
        image_part = types.Part.from_bytes(
            data=image_data,
            mime_type="image/jpeg"
        )
        
        response = client.models.generate_content(
            model="gemini-3-pro-preview",
            contents=[analysis_prompt, image_part]
        )
        
        return {
            "success": True,
            "result": response.text,
            "image_path": str(image_path)
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "image_path": str(image_path)
        }


def create_analysis_prompt(references: dict = None) -> str:
    """명시적으로 모든 속성을 나열하여 정확도를 높인 프롬프트를 생성합니다."""
    
    prompt = """Analyze this fashion image. Extract ALL visible clothing items separately.

## OUTPUT FORMAT (JSON only, English values):
{
    "Clothing": [
        {
            "cat": "Category name",
            "subcat": "Item type",
            "brand": "Brand if visible, else empty",
            "product_name": "Product name if identifiable, else empty",
            "attributes": { /* category-specific attributes below */ }
        }
    ],
    "Marketing": {
        "age group": "",
        "color tone filter": "",
        "coordination method": "",
        "gender": "",
        "skin tone": "",
        "pose": "",
        "hair style": "",
        "expression": "",
        "gaze direction": "",
        "fashion style": "",
        "location": "",
        "mood": "",
        "number of people": "",
        "overall fashion color tone": "",
        "season weather": "",
        "shooting composition": ""
    }
}

## MARKETING (MUST fill ALL 16 fields - multiple values allowed with comma):
- "age group": child/teenager/youth/adult/middle-aged/elderly
- "color tone filter": reddish/yellowish/blueish/neutral/contrast/monochrome
- "coordination method": layered/tone-on-tone/set-up/mix & match/low-rise/oversized (e.g., "layered, mix & match")
- "gender": male/female
- "skin tone": cool/warm/neutral
- "pose": full body shot/sitting/walking/looking back/aerial shot/exercise/low angle shot (e.g., "sitting, full body shot")
- "hair style": short hair/wave/straight hair/braided/ponytail/pigtails/bangs/crew cut/dyed hair/layered cut/high bun/low bun (e.g., "short hair, bangs")
- "expression": smile/expressionless/surprised/cool/wink
- "gaze direction": front/side/upward/downward/avoiding gaze
- "fashion style": casual/street/business/formal/sporty/luxury/feminine/gorpcore/workwear/y2k/old money look/preppy/bodycon (e.g., "casual, street")
- "location": street/café/shopping-store/park-nature/beach/gym/festival/party/city/campus/car/stadium/flight/outdoor-exercise/travel/pool/home/studio (e.g., "street, city")
- "mood": relaxed/active/chic/luxurious/hip/lovely/festive/rebellious/romantic (e.g., "relaxed, chic")
- "number of people": single/couple/group
- "overall fashion color tone": warm tone/cool tone/neutral tone/vivid/pastel/dark/bright
- "season weather": spring/summer/fall/winter
- "shooting composition": full body/upper body/close-up/side view/back view/mid shot

## COMMON ATTRIBUTES (apply to ALL clothing items):
- "color": [array of colors] red/blue/white/black/navy/gray/beige/brown/green/yellow/pink/orange/purple/burgundy/cream/ivory/khaki/olive/coral/mint/sky blue/etc
- "color coordination": multi color/single color/two tone/gradient/color block
- "fabrication": jersey knit/woven/denim/leather/cotton/polyester/wool/silk/linen/velvet/satin/chiffon/lace/mesh/fleece/corduroy/tweed/cashmere/nylon
- "pattern": solid/stripe/check/plaid/floral/polka dot/animal print/leopard pattern/camouflage/graphic/logo/abstract/geometric/paisley/houndstooth/gingham/tartan/tie-dye

## INNER ATTRIBUTES (cat="Inner"):
- "inner neckline": turtle neck/cowl neck/mock neck/crew neck/round neck/scoop neck/v neck/square neck/halter neck/shirt collar/hood/polo collar/boat neck
- "inner front detail": eyelet/lace/wrap/cut-out/twisted/ruched/drape/ribbon/shirring/belt/buckle/zipper/button/piping/stitching/embroidery/applique/patchwork/ruffle
- "inner fabric sheerness": opaque/sheer/slightly-sheer
- "sleeve length": extra-long sleeves/long sleeves/three-quarter sleeves/short sleeves/cap sleeves/sleeveless
- "inner silhouette": slim fit/regular fit/oversize fit
- "inner length": cropped length/waist length/hip length/mid thigh length

## OUTER ATTRIBUTES (cat="Outer"):
- "outer neckline": notched collar/peak-lapel/shirt collar/shawl collar/mandarin collar/wide collar/fur neck/collarless/hood
- "outer front closure": open front/toggle closure/velcro closure/full zip up/half zip up/pullover/double breasted/single breasted/snap button
- "sleeve length": extra long sleeves/long sleeves/three-quarter sleeves/short sleeves/sleeveless
- "outer silhouette": slim fit/regular fit/boxy fit/oversize fit
- "outer length": cropped length/waist length/hip length/mid thigh length/knee-length/calf length/ankle-length

## BOTTOM ATTRIBUTES (cat="Bottom"):
- "pants silhouette": skinny/slim/straight/bootcut/flare/wide/tapered/baggy/fitted
- "skirts silhouette": a-line/h-line/pencil/flared/pleated/tiered/wrap/mermaid
- "pants length": capri length/cropped length/ankle length/top of shoe
- "skirts length": mini length/above knee length/knee length/mid length/maxi length
- "bottoms front detail": pocket/flap pocket/welt pocket/button/zipper/belt/buckle/drawstring/pleats/ruffle
- "waist line": low rise/mid rise/high rise

## BAG ATTRIBUTES (cat="Bag"):
- "bags size": micro/small/medium/large/oversized
- "bags closure type": zip-top/zip-around/magnetic-flap/buckle-flap/turn-lock/drawstring/snap-button/open-top
- "bags detail": ring/d-ring/buckle/zipper/chain/bag charm/metal stud/clasp/quilting/embroidery
- "bags handle and strap type": backpack strap/top handle/double handle/single shoulder strap/cross body/wristlet

## SHOES ATTRIBUTES (cat="Shoes"):
- "heel height": high heel/low heel/mid heel/flat
- "shaft height": high top/knee high/low top/mid calf/mid top/thigh high
- "outsole feature": grip sole/chunky sole/flat sole/platform sole
- "toe shape": almond toe/pointed toe/round toe/square toe
- "material": leather/suede/canvas/mesh/synthetic/patent leather
- "finish": glossy/matte/metallic

## ONEPIECE ATTRIBUTES (cat="Onepiece"):
- "onepiece upper neckline": turtle neck/cowl neck/mock neck/crew neck/round neck/scoop neck/v neck/square neck/sweetheart neck/halter neck/shirt collar/hood/collarless/off the shoulder/one shoulder
- "onepiece strap style": strapless/asymmetric-strap/spaghetti-strap/adjustable-strap/halter-strap
- "sleeve length": extra-long sleeves/long sleeves/three-quarter sleeves/short sleeves/cap sleeves/sleeveless
- "onepiece sleeve type": dolman sleeves/bell sleeves/flutter sleeves/bishop sleeves/puff sleeves/balloon sleeves
- "onepiece fabric sheerness": opaque/slightly-sheer/partial-sheer/ultra-sheer
- "onepiece front detail": wrap/cut-out/twist/ruched/lace/belt/buckle/zipper/button/pleats/embroidery/sequins
- "onepiece front closure": half zip up/full zip up/tie in/half-button/full-button/wrap-closure
- "onepiece back detail": ruched/lace/keyhole/belt/buckle/zipper/pleats/sequins
- "onepiece back closure": back-zip/wrap-tie-back/lace-up-back
- "onepiece skirt silhouette": a-line/flare/pencil/wrap/tiered/mermaid/asymmetrical
- "onepiece skirt length": micro mini length/mini length/above knee length/knee length/midi length/maxi length
- "onepiece waist type": empire/natural/high-waisted/drop-waist
- "onepiece silhouette": slim fit/regular fit/oversize fit

## HOSIERY ATTRIBUTES (cat="Hosiery"):
- "hosiery cuff": frill-cuff/ribbed cuff/lace-up
- "hosiery sheerness": opaque/partial-sheer/slightly-sheer/ultra-sheer
- "hosiery height": ankle/crew/knee-high/no-show/over-the-knee/thigh-high/pantyhose
- "socks toe coverage": full-toe/open-toe/toe-separation

## SWIMWEAR ONEPIECE ATTRIBUTES (cat="Swimwear Onepiece"):
- "swimwear onepiece upper neckline": v neck/scoop neck/boat neck/square neck/sweetheart neck/halter neck
- "swimwear onepiece sleeve length": sleeveless/short sleeves/long sleeves
- "swimwear onepiece detail": slit/eyelet lace/embroidery/fringe/ruffle/keyhole/twisted/ruching
- "swimwear onepiece front closure": open-front/full-button/half-button
- "swimwear onepiece fabric sheerness": slightly-sheer/opaque
- "swimwear onepiece skirt length": mini length/midi length/maxi length
- "swimwear onepiece strap style": strapless/spaghetti-strap/halter-strap/cross-back strap/adjustable-strap/cut-out
- "swimwear onepiece back closure": open-back/lace-up-back

## SWIMWEAR INNER ATTRIBUTES (cat="Swimwear Inner"):
- "swimwear inner neckline": crew neck/mock neck/scoop neck/v neck/square neck/sweetheart neck/halter neck
- "swimwear inner sleeve length": long sleeves/short sleeves
- "swimwear inner front closure": half zip up/full zip up
- "swimwear inner detail": piping/stitching/ruching/ruffle/twisted/keyhole/cut-out
- "swimwear inner strap style": spaghetti-strap/adjustable-strap/halter-strap/cross-back strap/strapless
- "swimwear inner back closure": lace-up-back

## SWIMWEAR BOTTOMS ATTRIBUTES (cat="Swimwear Bottoms"):
- "swimwear bottom pants silhouette": slim/straight/tapered
- "swimwear bottom pants length": cropped length/ankle length
- "swimwear bottom shorts silhouette": fitted/straight-cut/baggy/bermuda
- "swimwear bottom shorts length": mid thigh length/knee length
- "swimwear bottom skirts silhouette": a-line/flared/wrap
- "swimwear bottom skirts length": mini length/above knee length
- "swimwear bottoms closure": elastic-waist/drawstring-waist/wrap-tie
- "swimwear bottoms waist line": low rise/mid rise/high rise
- "swimwear bottoms detail": pocket/zipper pocket/piping/twisted/ruching/lace-up/ruffle

## HEADWEAR ATTRIBUTES (cat="Headwear"):
- "headwear type": cap/beanie/bucket hat/fedora/beret/visor/headband/bandana/sun hat/baseball cap/snapback

## EYEWEAR ATTRIBUTES (cat="Eyewear"):
- "eyewear type": sunglasses/glasses/goggles/reading glasses
- "frame shape": round/square/aviator/cat-eye/rectangular/oval/oversized

## NECKWEAR ATTRIBUTES (cat="Neckwear"):
- "neckwear type": scarf/necktie/bow tie/choker/bandana/neckerchief

## RULES:
1. Analyze EACH visible item separately
2. MUST fill ALL 16 Marketing fields
3. MUST fill ALL common attributes (color, color coordination, fabrication, pattern) for each clothing item
4. Use category-specific attributes based on item type
5. Values in English only. Empty string "" if unknown
6. MULTI-VALUE ALLOWED: If multiple values apply, use comma-separated format (e.g., "sitting, full body shot", "smile, wink", "street, casual")
7. color should be an array if multiple colors visible (e.g., ["red", "white", "blue"])
"""
    return prompt


def parse_gemini_response(response_text: str) -> dict:
    """Gemini 응답에서 JSON을 파싱합니다."""
    try:
        if "```json" in response_text:
            json_str = response_text.split("```json")[1].split("```")[0]
        elif "```" in response_text:
            json_str = response_text.split("```")[1].split("```")[0]
        else:
            json_str = response_text
        
        return json.loads(json_str.strip())
    except json.JSONDecodeError:
        return {"raw_response": response_text}


def flatten_to_vertical(parsed_data: dict, image_name: str) -> list:
    """
    JSON을 Cat, Subcat, Key, Value 형식으로 변환합니다.
    """
    rows = []
    
    if "raw_response" in parsed_data:
        rows.append({
            "Image": image_name,
            "Cat": "Error",
            "Subcat": "Parse Failed",
            "Key": "Raw Response",
            "Value": parsed_data["raw_response"][:500]
        })
        return rows
    
    # Unknown, None 값을 빈 문자열로 변환하는 함수
    def clean_value(v):
        if v is None:
            return ""
        v_str = str(v).strip()
        if v_str.lower() in ["unknown", "none", "n/a", "null", "undefined"]:
            return ""
        return v_str
    
    # 의류 정보 처리 (Clothing) - 배열로 여러 아이템 처리
    clothing_list = parsed_data.get("Clothing", [])
    
    # 단일 객체인 경우 배열로 변환
    if isinstance(clothing_list, dict):
        clothing_list = [clothing_list]
    
    for clothing in clothing_list:
        cat = clean_value(clothing.get("cat", ""))
        subcat = clean_value(clothing.get("subcat", ""))
        brand = clean_value(clothing.get("brand", ""))
        product_name = clean_value(clothing.get("product_name", ""))
        attributes = clothing.get("attributes", {})
        
        first_row = True
        
        # 브랜드 정보 추가
        if brand:
            rows.append({
                "Image": image_name,
                "Cat": cat if first_row else "",
                "Subcat": subcat if first_row else "",
                "Key": "brand",
                "Value": brand
            })
            first_row = False
        
        # 제품명 정보 추가
        if product_name:
            rows.append({
                "Image": image_name,
                "Cat": cat if first_row else "",
                "Subcat": subcat if first_row else "",
                "Key": "product_name",
                "Value": product_name
            })
            first_row = False
        
        for key, value in attributes.items():
            if isinstance(value, list):
                # 배열인 경우 쉼표로 합쳐서 한 행으로
                cleaned_values = [clean_value(v) for v in value if clean_value(v)]
                if cleaned_values:
                    rows.append({
                        "Image": image_name,
                        "Cat": cat if first_row else "",
                        "Subcat": subcat if first_row else "",
                        "Key": key,
                        "Value": ", ".join(cleaned_values)
                    })
                    first_row = False
            else:
                cleaned = clean_value(value)
                if cleaned:  # 빈 값이 아닌 경우만 추가
                    rows.append({
                        "Image": image_name,
                        "Cat": cat if first_row else "",
                        "Subcat": subcat if first_row else "",
                        "Key": key,
                        "Value": cleaned
                    })
                    first_row = False
        
        # 속성이 하나도 없으면 cat, subcat만이라도 추가
        if first_row and (cat or subcat):
            rows.append({
                "Image": image_name,
                "Cat": cat,
                "Subcat": subcat,
                "Key": "",
                "Value": ""
            })
    
    # 마케팅 속성 처리 (Marketing)
    marketing = parsed_data.get("Marketing", {})
    for attr_name, attr_value in marketing.items():
        cleaned = clean_value(attr_value)
        if cleaned:  # 빈 값이 아닌 경우만 추가
            rows.append({
                "Image": image_name,
                "Cat": attr_name,
                "Subcat": "",
                "Key": "",
                "Value": cleaned
            })
    
    return rows


# =============================================================================
# 배치 분석 및 저장
# =============================================================================

def analyze_images_batch(
    image_paths: list,
    output_excel: str = None,
    references: dict = None,
    batch_size: int = 1  # 1장씩 분석 (정확도 최우선)
) -> pd.DataFrame:
    """이미지를 개별 분석합니다. (정확도 최우선)"""
    OUTPUT_DIR.mkdir(exist_ok=True)
    
    print("🔧 Gemini 클라이언트 초기화 중...")
    client = setup_gemini()
    
    # 배치 분석을 위한 프롬프트 수정 (여러 장을 처리하라고 지시)
    base_prompt = create_analysis_prompt(references)
    batch_instruction = """
    
    ## BATCH ANALYSIS INSTRUCTION:
    - You will receive multiple images.
    - Analyze EACH image sequentially.
    - Return a JSON Object with a key "results" containing a list of analysis for each image.
    - The order of the list must match the order of images provided.
    
    Example Output Structure:
    {
        "results": [
            { "file_name": "image1.jpg", "analysis": { ... analysis for image 1 ... } },
            { "file_name": "image2.jpg", "analysis": { ... analysis for image 2 ... } }
        ]
    }
    """
    final_prompt = base_prompt + batch_instruction

    all_rows = []
    total = len(image_paths)
    
    # 이미지 리스트를 배치 사이즈만큼 자르기 (chunking)
    chunks = [image_paths[i:i + batch_size] for i in range(0, total, batch_size)]
    
    print(f"\n📊 총 {total}개 이미지, {len(chunks)}개 배치로 분석 시작 (배치크기: {batch_size})...\n")
    
    total_start_time = time.time()
    
    for batch_idx, chunk in enumerate(chunks, 1):
        print(f"📦 배치 [{batch_idx}/{len(chunks)}] 처리 중 ({len(chunk)}장)...")
        
        try:
            # 1. 이번 배치의 이미지 데이터들 준비
            contents = [final_prompt] # 프롬프트 먼저 넣고
            batch_files = [] # 파일명 매핑용
            
            for img_path in chunk:
                img_data = encode_image(img_path)
                image_part = types.Part.from_bytes(data=img_data, mime_type="image/jpeg")
                contents.append(image_part) # 이미지 계속 추가
                batch_files.append(Path(img_path).name)

            # 2. API 한 번 호출로 여러 이미지 동시 분석
            response = client.models.generate_content(
                model="gemini-3-pro-preview",
                contents=contents,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json" # JSON 강제 모드 (토큰 절약)
                )
            )
            
            # 3. 결과 파싱 및 매핑 (JSON 정제 - Extra data 에러 방지)
            response_text = response.text.strip()
            
            # JSON 외 텍스트 제거 (```json ... ``` 형태 처리)
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0]
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0]
            
            # 첫 번째 유효한 JSON 객체만 추출 (raw_decode 사용)
            response_text = response_text.strip()
            try:
                # raw_decode는 첫 번째 완전한 JSON만 파싱하고 나머지 무시
                decoder = json.JSONDecoder()
                result_json, _ = decoder.raw_decode(response_text)
            except json.JSONDecodeError:
                # { 로 시작하는 부분 찾기
                start_idx = response_text.find('{')
                if start_idx != -1:
                    result_json, _ = decoder.raw_decode(response_text[start_idx:])
                else:
                    raise
            
            results_list = result_json.get("results", [])
            
            # 개수 불일치 안전장치: 결과가 이미지 수보다 적을 경우 대비
            if isinstance(result_json, list): # 혹시 리스트로 바로 줄 경우
                results_list = result_json
            
            # 4. 각 이미지별 결과 저장
            for i, img_name in enumerate(batch_files):
                if i < len(results_list):
                    # 구조에 따라 분석 데이터 추출
                    analysis_data = results_list[i].get("analysis", results_list[i])
                    # 기존 flatten 함수 재사용
                    rows = flatten_to_vertical(analysis_data, img_name)
                    all_rows.extend(rows)
                else:
                    # 누락된 경우
                    all_rows.append({"Image": img_name, "Cat": "Error", "Key": "Batch Error", "Value": "Missing in response"})

            print(f"  ✓ 배치 완료")
            
        except Exception as e:
            print(f"  ❌ 배치 실패: {str(e)}")
            for img_path in chunk:
                all_rows.append({
                    "Image": Path(img_path).name,
                    "Cat": "Error",
                    "Subcat": "",
                    "Key": "Exception",
                    "Value": str(e)
                })
    
    # 소요 시간 계산
    total_elapsed = time.time() - total_start_time
    
    # DataFrame 생성
    df = pd.DataFrame(all_rows, columns=["Image", "Cat", "Subcat", "Key", "Value"])
    
    # 성공/실패 카운트
    success_count = len([r for r in all_rows if r.get("Cat") != "Error"])
    fail_count = len([r for r in all_rows if r.get("Cat") == "Error"])
    
    if output_excel is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_excel = OUTPUT_DIR / f"vlm_analysis_result_{timestamp}.xlsx"
    
    with pd.ExcelWriter(output_excel, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='분석결과')
        
        worksheet = writer.sheets['분석결과']
        
        # 열 너비 설정
        worksheet.column_dimensions['A'].width = 15  # Image
        worksheet.column_dimensions['B'].width = 25  # Cat
        worksheet.column_dimensions['C'].width = 20  # Subcat
        worksheet.column_dimensions['D'].width = 25  # Key
        worksheet.column_dimensions['E'].width = 40  # Value
        
        # 이미지 썸네일 삽입
        print("\n🖼️ 엑셀에 이미지 썸네일 삽입 중...")
        inserted_images = set()
        
        for row_idx, row in enumerate(df.itertuples(), start=2):
            image_name = row.Image
            
            if image_name not in inserted_images:
                image_path = IMAGES_DIR / image_name
                
                if image_path.exists():
                    try:
                        img = PILImage.open(image_path)
                        img.thumbnail((80, 80))
                        
                        img_buffer = BytesIO()
                        img.save(img_buffer, format='JPEG')
                        img_buffer.seek(0)
                        
                        xl_img = XLImage(img_buffer)
                        xl_img.width = 80
                        xl_img.height = 80
                        
                        cell = f'A{row_idx}'
                        worksheet.add_image(xl_img, cell)
                        
                        worksheet.row_dimensions[row_idx].height = 65
                        
                        inserted_images.add(image_name)
                    except Exception as e:
                        print(f"  ⚠️ 이미지 삽입 실패 ({image_name}): {e}")
        
        print(f"  ✓ {len(inserted_images)}개 이미지 썸네일 삽입 완료")
    
    avg_time = total_elapsed / total if total > 0 else 0
    
    print(f"\n{'='*60}")
    print(f"✅ 분석 완료!")
    print(f"📈 성공: {success_count}개 항목 / 실패: {fail_count}개 항목")
    print(f"📊 총 {len(df)}개 행 생성")
    print(f"⏱️ 총 소요시간: {total_elapsed:.1f}초 (평균 {avg_time:.1f}초/이미지)")
    print(f"💾 결과 저장: {output_excel}")
    print(f"{'='*60}\n")
    
    return df


def analyze_single_image(image_path: str, references: dict = None) -> dict:
    """단일 이미지를 분석합니다. (테스트용)"""
    client = setup_gemini()
    
    prompt = create_analysis_prompt(references)
    
    print(f"🔍 이미지 분석 중: {image_path}")
    result = analyze_image(client, image_path, prompt)
    
    if result["success"]:
        parsed = parse_gemini_response(result["result"])
        print("\n📋 분석 결과 (JSON):")
        print(json.dumps(parsed, ensure_ascii=False, indent=2))
        
        rows = flatten_to_vertical(parsed, Path(image_path).name)
        print("\n📋 분석 결과 (테이블 형식):")
        print("-" * 100)
        print(f"{'Cat':<25} {'Subcat':<20} {'Key':<25} {'Value':<25}")
        print("-" * 100)
        for row in rows:
            val = row['Value'][:25] if len(row['Value']) > 25 else row['Value']
            print(f"{row['Cat']:<25} {row['Subcat']:<20} {row['Key']:<25} {val:<25}")
        
        return parsed
    else:
        print(f"\n❌ 분석 실패: {result.get('error')}")
        return result


def get_image_list(folder_path: str = None, pattern: str = "*.jpg") -> list:
    """폴더에서 이미지 파일 목록을 가져옵니다."""
    folder = Path(folder_path) if folder_path else IMAGES_DIR
    images = [f for f in folder.glob(pattern) if f.is_file() and not f.name.startswith('.')]
    print(f"📁 {folder}에서 {len(images)}개 이미지 발견")
    return sorted(images)


# =============================================================================
# 메인 실행
# =============================================================================

def main():
    """메인 실행 함수"""
    
    print("="*60)
    print("🖼️  Gemini VLM 이미지 분석 (카테고리별 속성)")
    print("="*60)
    
    # 기준정보 파싱 및 저장
    print("\n[1] 기준정보 파싱 중...")
    references = load_all_references()
    save_references_to_json(references)
    
    # 기준정보 요약 출력
    print("\n📋 마케팅 기준정보:")
    for key, values in references["marketing"].items():
        print(f"  - {key}: {len(values)}개 값")
    
    print("\n📋 의류 카테고리:")
    for cat, sub_cats in references["category"].items():
        print(f"  - {cat}: {len(sub_cats)}개 소분류")
    
    # 이미지 목록 가져오기
    test_images = get_image_list()
    
    if test_images:
        # 단일 이미지 테스트
        print(f"\n[2] 단일 이미지 테스트 (총 {len(test_images)}개 이미지 발견)")
        result = analyze_single_image(str(test_images[0]), references)
        
        # 배치 분석
        if len(test_images) > 1:
            print(f"\n[3] 배치 분석 ({len(test_images)}개 이미지)")
            df = analyze_images_batch(
                image_paths=[str(img) for img in test_images],
                references=references
            )
    else:
        print(f"⚠️ 분석할 이미지가 없습니다. vlm_image 폴더에 jpg 파일을 넣어주세요.")


if __name__ == "__main__":
    main()
