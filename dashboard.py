"""
VLM 비교 분석 대시보드 (간소화 버전)
- 탭 1: 분석 요약
- 탭 2: 상세 비교표 (F&F / Gemini / 오드컨셉)
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
from datetime import datetime
from io import BytesIO
from PIL import Image
import base64

# 페이지 설정
st.set_page_config(
    page_title="VLM 비교 분석",
    layout="wide"
)

# 경로 설정
BASE_DIR = Path(__file__).parent
FNF_FILE = BASE_DIR / "fnf정답지.xlsx"
ODDCONCEPT_FILE = BASE_DIR / "오드컨셉결과.xlsx"
OUTPUT_DIR = BASE_DIR / "output"  # Gemini 분석 결과 폴더
IMAGES_DIR = BASE_DIR / "images"  # 이미지 폴더

def normalize_image_name(name):
    """이미지 이름 정규화 (확장자 제거, 소문자 변환)"""
    if pd.isna(name) or not name:
        return ""
    name = str(name).strip().lower()
    # 확장자 제거
    for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp']:
        if name.endswith(ext):
            name = name[:-len(ext)]
            break
    return name

# =============================================================================
# 데이터 로드
# =============================================================================

@st.cache_data(ttl=1)  # 1초 캐시로 즉시 갱신
def load_fnf_data(_file_mtime=None):
    """F&F 정답지를 로드합니다.
    
    Args:
        _file_mtime: 파일 수정 시간 (캐시 무효화용)
    """
    if not FNF_FILE.exists():
        return None, f"F&F 정답지 파일을 찾을 수 없습니다: {FNF_FILE}"
    
    try:
        df = pd.read_excel(FNF_FILE)
        
        # 필수 컬럼 확인
        required_cols = ['Image', 'Cat', 'Subcat', 'Key', 'Value']
        if not all(col in df.columns for col in required_cols):
            return None, f"필수 컬럼이 없습니다. 필요: {required_cols}"
        
        # 이미지 컬럼 ffill (그룹 첫 행의 이미지명을 아래로 채움)
        df['Image'] = df['Image'].ffill()
        
        # 모든 값 소문자로 통일 (Cat 비교를 위해)
        for col in ['Cat', 'Subcat', 'Key', 'Value']:
            if col in df.columns:
                df[col] = df[col].fillna('').astype(str).str.lower()
        
        return df[required_cols], None
        
    except Exception as e:
        return None, str(e)


@st.cache_data(ttl=1)  # 1초 캐시로 즉시 갱신
def load_oddconcept_data(_file_mtime=None):
    """오드컨셉 결과를 로드합니다.
    
    Args:
        _file_mtime: 파일 수정 시간 (캐시 무효화용)
    """
    if not ODDCONCEPT_FILE.exists():
        return None, f"오드컨셉 결과 파일을 찾을 수 없습니다: {ODDCONCEPT_FILE}"
    
    try:
        df = pd.read_excel(ODDCONCEPT_FILE)
        
        # 필수 컬럼 확인
        required_cols = ['Image', 'Cat', 'Subcat', 'Key', 'Value']
        if not all(col in df.columns for col in required_cols):
            return None, f"필수 컬럼이 없습니다. 필요: {required_cols}"
        
        # 이미지 컬럼 ffill (그룹 첫 행의 이미지명을 아래로 채움)
        df['Image'] = df['Image'].ffill()
        
        # 모든 값 소문자로 통일 (Cat 비교를 위해)
        for col in ['Cat', 'Subcat', 'Key', 'Value']:
            if col in df.columns:
                df[col] = df[col].fillna('').astype(str).str.lower()
        
        return df[required_cols], None
        
    except Exception as e:
        return None, str(e)


def load_gemini_results():
    """vlm_test.py 실행 결과 (최신 Gemini 분석)를 로드합니다."""
    OUTPUT_DIR.mkdir(exist_ok=True)
    
    # 최신 결과 파일 찾기
    result_files = sorted(OUTPUT_DIR.glob("vlm_analysis_result_*.xlsx"), reverse=True)
    
    if not result_files:
        return None, None
    
    latest_file = result_files[0]
    
    try:
        df = pd.read_excel(latest_file)
        # 컬럼명 정리
        if 'Image' in df.columns:
            df = df.rename(columns={'Image': 'Image_Name'})
        
        # 모든 값 소문자로 통일 (Cat 비교를 위해)
        for col in ['Cat', 'Subcat', 'Key', 'Value']:
            if col in df.columns:
                df[col] = df[col].fillna('').astype(str).str.lower()
        
        return df, latest_file.name
    except PermissionError:
        # 파일이 열려있으면 이전 파일 시도
        if len(result_files) > 1:
            try:
                df = pd.read_excel(result_files[1])
                if 'Image' in df.columns:
                    df = df.rename(columns={'Image': 'Image_Name'})
                
                # 모든 값 소문자로 통일
                for col in ['Cat', 'Subcat', 'Key', 'Value']:
                    if col in df.columns:
                        df[col] = df[col].fillna('').astype(str).str.lower()
                
                return df, result_files[1].name + " (이전 버전)"
            except:
                pass
        return None, "파일 열려있음"
    except Exception as e:
        return None, str(e)


@st.cache_data
def load_data(_fnf_mtime=None, _oddconcept_mtime=None):
    """모든 비교 데이터를 로드합니다.
    
    Args:
        _fnf_mtime: F&F 파일 수정 시간 (캐시 무효화용)
        _oddconcept_mtime: 오드컨셉 파일 수정 시간 (캐시 무효화용)
    """
    # F&F 정답지 로드
    df_fnf, fnf_error = load_fnf_data(_fnf_mtime)
    if fnf_error:
        return None, None, None, f"F&F 로드 실패: {fnf_error}"
    
    # Gemini 결과 로드 (vlm_test.py 실행 결과)
    df_gemini, gemini_file = load_gemini_results()
    if df_gemini is None:
        df_gemini = pd.DataFrame(columns=['Image', 'Cat', 'Subcat', 'Key', 'Value'])
    
    # 오드컨셉 결과 로드
    df_oddconcept, odd_error = load_oddconcept_data(_oddconcept_mtime)
    if odd_error:
        return None, None, None, f"오드컨셉 로드 실패: {odd_error}"
    
    return df_fnf, df_gemini, df_oddconcept, None


def merge_comparison_data(df_fnf, df_gemini, df_oddconcept):
    """3개 VLM 결과를 Key 기준으로 merge하여 한 테이블로 만듭니다."""
    
    # 각 DataFrame에 소스 표시 및 정리
    df_fnf_clean = df_fnf.copy()
    df_gemini_clean = df_gemini.copy()
    df_oddconcept_clean = df_oddconcept.copy()
    
    # 인덱스 생성 (행 번호)
    df_fnf_clean['row_idx'] = range(len(df_fnf_clean))
    df_gemini_clean['row_idx'] = range(len(df_gemini_clean))
    df_oddconcept_clean['row_idx'] = range(len(df_oddconcept_clean))
    
    # 컬럼명 변경
    df_fnf_clean = df_fnf_clean.rename(columns={
        'Cat': 'Cat',
        'Subcat': 'Subcat', 
        'Key': 'Key',
        'Value': 'F&F 정답'
    })
    
    df_gemini_clean = df_gemini_clean.rename(columns={
        'Value': 'Gemini'
    })
    
    df_oddconcept_clean = df_oddconcept_clean.rename(columns={
        'Value': '오드컨셉'
    })
    
    # row_idx 기준으로 merge (행 번호 맞춤)
    merged = df_fnf_clean[['row_idx', 'Cat', 'Subcat', 'Key', 'F&F 정답']].copy()
    
    # Gemini 값 추가
    if 'Gemini' in df_gemini_clean.columns:
        gemini_vals = df_gemini_clean[['row_idx', 'Gemini']].copy()
        merged = merged.merge(gemini_vals, on='row_idx', how='left')
    else:
        merged['Gemini'] = ''
    
    # 오드컨셉 값 추가
    if '오드컨셉' in df_oddconcept_clean.columns:
        odd_vals = df_oddconcept_clean[['row_idx', '오드컨셉']].copy()
        merged = merged.merge(odd_vals, on='row_idx', how='left')
    else:
        merged['오드컨셉'] = ''
    
    # 일치 여부 계산
    merged['Gemini 일치'] = merged.apply(
        lambda row: '✅' if str(row['F&F 정답']).strip() == str(row['Gemini']).strip() and str(row['F&F 정답']).strip() else 
                    ('⚠️' if pd.notna(row['F&F 정답']) and str(row['F&F 정답']).strip() else ''),
        axis=1
    )
    merged['오드컨셉 일치'] = merged.apply(
        lambda row: '✅' if str(row['F&F 정답']).strip() == str(row['오드컨셉']).strip() and str(row['F&F 정답']).strip() else 
                    ('⚠️' if pd.notna(row['F&F 정답']) and str(row['F&F 정답']).strip() else ''),
        axis=1
    )
    
    # row_idx 제거
    merged = merged.drop(columns=['row_idx'])
    
    # NaN을 빈 문자열로
    merged = merged.fillna('')
    
    return merged


def calculate_stats(df_fnf, df_gemini, df_oddconcept):
    """일치율 통계를 계산합니다."""
    stats = {}
    
    # 총 항목 수
    stats['total_items'] = len(df_fnf)
    
    # F&F에 일치 컬럼이 있으면 사용
    if '일치' in df_fnf.columns:
        match_col = df_fnf['일치'].fillna('')
        stats['match_count'] = (match_col == 'O').sum()
        stats['match_rate'] = stats['match_count'] / stats['total_items'] * 100 if stats['total_items'] > 0 else 0
    
    # Value 비교로 일치율 계산
    fnf_vals = df_fnf['Value'].fillna('').astype(str).str.strip()
    
    # Gemini 일치율
    if len(df_gemini) > 0 and 'Value' in df_gemini.columns:
        gemini_vals = df_gemini['Value'].fillna('').astype(str).str.strip()
        min_len = min(len(fnf_vals), len(gemini_vals))
        if min_len > 0:
            gemini_match = (fnf_vals[:min_len].values == gemini_vals[:min_len].values).sum()
            stats['gemini_match_rate'] = gemini_match / min_len * 100
        else:
            stats['gemini_match_rate'] = 0
    else:
        stats['gemini_match_rate'] = 0
    
    # 오드컨셉 일치율
    if len(df_oddconcept) > 0 and 'Value' in df_oddconcept.columns:
        oddconcept_vals = df_oddconcept['Value'].fillna('').astype(str).str.strip()
        min_len = min(len(fnf_vals), len(oddconcept_vals))
        if min_len > 0:
            oddconcept_match = (fnf_vals[:min_len].values == oddconcept_vals[:min_len].values).sum()
            stats['oddconcept_match_rate'] = oddconcept_match / min_len * 100
        else:
            stats['oddconcept_match_rate'] = 0
    else:
        stats['oddconcept_match_rate'] = 0
    
    # 카테고리별 통계
    categories = df_fnf['Cat'].dropna().unique()
    stats['categories'] = [c for c in categories if pd.notna(c) and str(c).strip()]
    stats['category_count'] = len(stats['categories'])
    
    return stats


# =============================================================================
# 메인 앱
# =============================================================================

def main():
    st.title("VLM 비교 분석")
    st.caption("F&F 정답지 vs Gemini vs 오드컨셉")
    
    # 데이터 로드 (파일 수정 시간을 전달하여 파일 변경 시 자동 갱신)
    fnf_mtime = FNF_FILE.stat().st_mtime if FNF_FILE.exists() else None
    oddconcept_mtime = ODDCONCEPT_FILE.stat().st_mtime if ODDCONCEPT_FILE.exists() else None
    df_fnf, df_gemini, df_oddconcept, error = load_data(fnf_mtime, oddconcept_mtime)
    
    if error:
        st.error(f"❌ 데이터 로드 실패: {error}")
        st.info("💡 다음 파일들이 프로젝트 폴더에 있는지 확인하세요:")
        st.info(f"- `{FNF_FILE.name}` (F&F 정답지)")
        st.info(f"- `{ODDCONCEPT_FILE.name}` (오드컨셉 결과)")
        return
    
    # 통계 계산
    stats = calculate_stats(df_fnf, df_gemini, df_oddconcept)
    
    st.divider()
    
    # ==========================================================================
    # 전체 정답률 계산 (이미지별 정답률 평균)
    # ==========================================================================
    
    # Gemini 결과에서 이미지 목록 추출
    if df_gemini is not None and len(df_gemini) > 0:
        img_col = 'Image_Name' if 'Image_Name' in df_gemini.columns else 'Image'
        if img_col in df_gemini.columns:
            image_list = df_gemini[img_col].dropna().unique().tolist()
        else:
            image_list = []
    else:
        image_list = []
    
    # 총 비교 항목: F&F 정답지에서 중복 제외한 유니크 항목 수
    unique_items = df_fnf[['Cat', 'Subcat', 'Key', 'Value']].drop_duplicates()
    total_unique_items = len(unique_items)
    
    # 이미지별 정답률 계산을 위한 변수
    gemini_marketing_rates = []
    gemini_product_rates = []
    odd_marketing_rates = []
    odd_product_rates = []
    
    # ==========================================================================
    # 상세 비교표
    # ==========================================================================
    # 2단 열로 구성: 왼쪽(전체 정답률 요약), 오른쪽(범례)
    col_summary, col_legend = st.columns([1, 1])
    
    with col_summary:
        st.subheader("전체 정답률 요약")
        st.caption("(이미지별 평균 정답률)")
        
        # Placeholder - 나중에 업데이트
        summary_placeholder = st.empty()
    
    with col_legend:
        st.subheader("범례")
        
        # 범례
        st.markdown(""" 
        🟢 녹색 = F&F 정답에 없는 **추가 분석**  
        🔴 빨간색 = F&F 정답과 **불일치**, **누락**  
        ⬜ 무색 = F&F 정답과 **일치**
        """)
    
    st.divider()
    
    # None 값 정리 함수 + 소문자 통일
    def clean_none_values(df):
        df_clean = df.copy()
        for col in df_clean.columns:
            df_clean[col] = df_clean[col].fillna('')
            df_clean[col] = df_clean[col].astype(str).replace({
                'None': '', 'none': '', 'nan': '', 'NaN': '', 
                'N/A': '', 'n/a': '', 'null': '', 'NULL': '',
                '/': ''  # 오드컨셉의 빈 Subcat 처리
            })
            # 모든 값 소문자로 통일
            df_clean[col] = df_clean[col].str.lower()
        return df_clean
    
    # Gemini 결과에서 이미지 목록 추출
    if df_gemini is not None and len(df_gemini) > 0:
        img_col = 'Image_Name' if 'Image_Name' in df_gemini.columns else 'Image'
        if img_col in df_gemini.columns:
            image_list = df_gemini[img_col].dropna().unique().tolist()
        else:
            image_list = []
    else:
        image_list = []
    
    if not image_list:
        st.warning("⚠️ Gemini 분석 결과가 없습니다. `python vlm_test.py` 실행 후 새로고침하세요.")
    else:
        # 이미지별로 섹션 생성
        for img_idx, image_name in enumerate(image_list):
            st.markdown(f"이미지 {img_idx + 1}: `{image_name}`")
            
            # 이미지 미리보기 + 3개 테이블
            col_img, col_tables = st.columns([1, 4])
            
            with col_img:
                image_path = IMAGES_DIR / image_name
                if image_path.exists():
                    try:
                        img = Image.open(image_path)
                        st.image(img, use_container_width=True)
                    except:
                        st.text(f"📷 {image_name}")
                else:
                    st.info(f"이미지 없음")
            
            with col_tables:
                # 해당 이미지의 Gemini 데이터 필터링
                df_gemini_img = df_gemini[df_gemini[img_col] == image_name].copy()
                num_rows = len(df_gemini_img)
                
                # 이미지 이름 정규화하여 F&F, 오드컨셉 데이터 필터링
                normalized_img_name = normalize_image_name(image_name)
                
                # F&F 데이터에서 이미지 이름으로 필터링
                df_fnf['_norm_img'] = df_fnf['Image'].apply(normalize_image_name)
                df_fnf_filtered = df_fnf[df_fnf['_norm_img'] == normalized_img_name].drop(columns=['_norm_img'])
                
                # 오드컨셉 데이터에서 이미지 이름으로 필터링
                df_oddconcept['_norm_img'] = df_oddconcept['Image'].apply(normalize_image_name)
                df_odd_filtered = df_oddconcept[df_oddconcept['_norm_img'] == normalized_img_name].drop(columns=['_norm_img'])
                
                # 카테고리 정렬 순서 정의 (마케팅 → Outer → Inner → Bottom → Shoes → 나머지)
                cat_order = {
                    # 마케팅 관련 (먼저)
                    'age group': 1, 'color tone filter': 2, 'coordination method': 3,
                    'gender': 4, 'skin tone': 5, 'pose': 6, 'hair style': 7,
                    'expression': 8, 'gaze direction': 9, 'fashion style': 10,
                    'location': 11, 'mood': 12,
                    'number of people': 13, 'overall fashion color tone': 14,
                    'season weather': 15, 'shooting composition': 16,
                    # 상품 카테고리 순서
                    'outer': 20, 'inner': 21, 'bottom': 22, 'shoes': 23,
                    'bag': 24, 'accessories': 25, 'neckwear': 26, 'headwear': 27,
                    'eyewear': 28, 'hosiery': 29, 'onepiece': 30, 'swimwear': 31
                }
                
                def get_cat_order(cat_val):
                    cat_lower = str(cat_val).strip().lower()
                    return cat_order.get(cat_lower, 100)
                
                # 정렬 함수 (3개 테이블 모두 적용)
                def sort_by_category(df_raw):
                    df = df_raw.copy()
                    df = clean_none_values(df)
                    
                    # 0. Cat과 Subcat에 쉼표가 있으면 첫 번째 값만 사용 (표시용)
                    def get_first_value(text):
                        if not text or pd.isna(text):
                            return ''
                        text_str = str(text).strip()
                        if ',' in text_str:
                            return text_str.split(',')[0].strip()
                        return text_str
                    
                    df['Cat'] = df['Cat'].apply(get_first_value)
                    df['Subcat'] = df['Subcat'].apply(get_first_value)
                    
                    # 1. 마케팅 카테고리 구분 (Key가 없으면 마케팅)
                    df['_is_marketing'] = df['Key'].apply(lambda x: 1 if x == '' else 0)
                    
                    # 2. 정렬용으로 Cat/Subcat을 ffill (그룹 유지)
                    df['_cat_filled'] = df['Cat'].replace('', pd.NA).ffill().fillna('')
                    df['_subcat_filled'] = df['Subcat'].replace('', pd.NA).ffill().fillna('')
                    
                    # 마케팅 행은 _subcat_filled를 강제로 빈칸으로 (ffill 무시)
                    df.loc[df['_is_marketing'] == 1, '_subcat_filled'] = ''
                    
                    # 3. 정렬 (마케팅은 먼저, 그 다음 의류)
                    df['_cat_order'] = df['_cat_filled'].apply(lambda x: get_cat_order(x) if x else 999)
                    df['_subcat_lower'] = df['_subcat_filled'].str.lower()
                    df['_key_lower'] = df['Key'].str.lower()
                    
                    df = df.sort_values(['_cat_order', '_is_marketing', '_subcat_lower', '_key_lower'], ascending=[True, False, True, True]).reset_index(drop=True)
                    
                    # 3. 정렬 후, 같은 Cat/Subcat 그룹에서 첫 행만 값 유지하고 나머지는 빈칸으로
                    prev_cat = None
                    prev_subcat = None
                    for idx in df.index:
                        curr_cat = df.at[idx, '_cat_filled']
                        curr_subcat = df.at[idx, '_subcat_filled']
                        is_marketing = df.at[idx, '_is_marketing'] == 1
                        
                        if curr_cat == prev_cat and curr_subcat == prev_subcat:
                            df.at[idx, 'Cat'] = ''
                            df.at[idx, 'Subcat'] = ''
                        else:
                            df.at[idx, 'Cat'] = curr_cat
                            # 마케팅 카테고리는 Subcat 무조건 빈칸
                            df.at[idx, 'Subcat'] = '' if is_marketing else curr_subcat
                            prev_cat = curr_cat
                            prev_subcat = curr_subcat
                    
                    # 4. 하이라이트용 숨김 컬럼 추가 (ffill된 값)
                    df['_cat_for_match'] = df['_cat_filled']
                    df['_subcat_for_match'] = df['_subcat_filled']
                    
                    # 5. 임시 컬럼 제거 (매칭용은 남김, _is_missing과 _is_key_only_missing은 유지)
                    return df.drop(columns=['_cat_order', '_subcat_lower', '_key_lower', '_cat_filled', '_subcat_filled', '_is_marketing'], errors='ignore')
                
                # === VLM 결과에서 중복 제거 함수 ===
                def remove_duplicates(vlm_df):
                    """같은 (Cat, Subcat, Key) 조합이 중복되면 첫 번째만 유지"""
                    if len(vlm_df) == 0:
                        return vlm_df
                    
                    # 정규화 함수
                    def normalize_for_dedup(text):
                        if not text or pd.isna(text):
                            return ''
                        return str(text).strip().lower().replace('-', '').replace(' ', '').replace('_', '')
                    
                    # 중복 체크를 위한 임시 컬럼 생성
                    vlm_df_copy = vlm_df.copy()
                    vlm_df_copy['_cat_norm'] = vlm_df_copy.get('_cat_for_match', vlm_df_copy.get('Cat', '')).apply(normalize_for_dedup)
                    vlm_df_copy['_subcat_norm'] = vlm_df_copy.get('_subcat_for_match', vlm_df_copy.get('Subcat', '')).apply(normalize_for_dedup)
                    vlm_df_copy['_key_norm'] = vlm_df_copy['Key'].apply(normalize_for_dedup)
                    
                    # (Cat, Subcat, Key) 조합으로 중복 제거 (첫 번째만 유지)
                    vlm_df_dedup = vlm_df_copy.drop_duplicates(subset=['_cat_norm', '_subcat_norm', '_key_norm'], keep='first')
                    
                    # 임시 컬럼 제거
                    vlm_df_dedup = vlm_df_dedup.drop(columns=['_cat_norm', '_subcat_norm', '_key_norm'])
                    
                    return vlm_df_dedup.reset_index(drop=True)
                
                # F&F 정답지 정렬 (이미지 이름으로 필터링된 데이터 사용)
                df_fnf_raw = df_fnf_filtered[['Cat', 'Subcat', 'Key', 'Value']].copy()
                df_fnf_img = sort_by_category(df_fnf_raw)
                
                # 오드컨셉 정렬 및 중복 제거
                df_odd_raw = df_odd_filtered[['Cat', 'Subcat', 'Key', 'Value']].copy()
                df_odd_img = sort_by_category(df_odd_raw)
                df_odd_img = remove_duplicates(df_odd_img)
                
                # Gemini 정렬 및 중복 제거
                df_gemini_raw = df_gemini_img[['Cat', 'Subcat', 'Key', 'Value']].copy()
                df_gemini_clean = sort_by_category(df_gemini_raw)
                df_gemini_clean = remove_duplicates(df_gemini_clean)
                
                # 3개 VLM 나란히 표시
                t1, t2, t3 = st.columns(3)
                
                with t1:
                    st.markdown("**🟩 F&F 정답지**")
                  
                    # 읽기 전용 테이블 표시
                    table_height_fnf = min(600, 35 * len(df_fnf_img) + 100)
                    
                    st.dataframe(
                        df_fnf_img,
                        use_container_width=True,
                        height=table_height_fnf,
                        hide_index=True,
                        column_config={
                            '_cat_for_match': None,  # 숨김
                            '_subcat_for_match': None  # 숨김
                        }
                    )
                    
                    # 정답지 사용 (엑셀에서 불러온 데이터)
                    edited_fnf_img = df_fnf_img
                
                with t2:
                    st.markdown("**🟦 Gemini**")
                    
                    # Gemini 데이터 처리 (엑셀 파일 기반, 편집 불가)
                    
                    # === F&F 정답지에 있는 항목 중 누락된 것 추가 ===
                    def add_missing_items(vlm_df, fnf_df):
                        """F&F에는 있지만 VLM에 없는 항목을 빈 값으로 추가"""
                        # 정규화 함수 (하이픈, 공백, 언더스코어 제거)
                        def normalize_for_compare(text):
                            if not text:
                                return ''
                            return str(text).strip().lower().replace('-', '').replace(' ', '').replace('_', '')
                        
                        
                        # Cat 단어 단위 매칭 함수
                        def match_cat_words(cat1, cat2):
                            """Cat이 단어 단위로 겹치는지 체크"""
                            if not cat1 or not cat2:
                                return False
                            
                            s1 = str(cat1).strip()
                            s2 = str(cat2).strip()
                            if not s1 or not s2:
                                return False
                            
                            vals1 = [v.strip().lower() for v in str(cat1).split(',')]
                            vals2 = [v.strip().lower() for v in str(cat2).split(',')]
                            
                            words1 = set()
                            for v in vals1:
                                for word in v.split():
                                    normalized = normalize_for_compare(word).rstrip('s')
                                    if normalized:
                                        words1.add(normalized)
                            
                            words2 = set()
                            for v in vals2:
                                for word in v.split():
                                    normalized = normalize_for_compare(word).rstrip('s')
                                    if normalized:
                                        words2.add(normalized)
                            
                            return bool(words1 & words2)
                        
                        # Subcat 단어 단위 매칭 함수 (fuzzy_match_subcat과 동일 로직)
                        def match_subcat_words(subcat1, subcat2):
                            """Subcat이 단어 단위로 겹치는지 체크 (t shirt와 t-shirt를 같은 것으로 인식)"""
                            # 둘 다 값이 있어야 비교 가능
                            if not subcat1 or not subcat2:
                                return False
                            
                            # 공백이나 빈 문자열인 경우 False
                            s1 = str(subcat1).strip()
                            s2 = str(subcat2).strip()
                            if not s1 or not s2:
                                return False
                            
                            vals1 = [v.strip().lower() for v in str(subcat1).split(',')]
                            vals2 = [v.strip().lower() for v in str(subcat2).split(',')]
                            
                            words1 = set()
                            for v in vals1:
                                # 전체 문구를 정규화한 버전도 추가 (t shirt -> tshirt, t-shirt -> tshirt)
                                full_normalized = normalize_for_compare(v).rstrip('s')
                                if full_normalized:
                                    words1.add(full_normalized)
                                # 단어별 정규화
                                for word in v.split():
                                    normalized = normalize_for_compare(word).rstrip('s')
                                    if normalized:
                                        words1.add(normalized)
                            
                            words2 = set()
                            for v in vals2:
                                # 전체 문구를 정규화한 버전도 추가
                                full_normalized = normalize_for_compare(v).rstrip('s')
                                if full_normalized:
                                    words2.add(full_normalized)
                                # 단어별 정규화
                                for word in v.split():
                                    normalized = normalize_for_compare(word).rstrip('s')
                                    if normalized:
                                        words2.add(normalized)
                            
                            return bool(words1 & words2)
                        
                        # VLM에 있는 항목들을 리스트로 저장 (원본 cat, subcat 포함)
                        vlm_items_list = []
                        
                        for _, row in vlm_df.iterrows():
                            cat_orig = str(row.get('_cat_for_match', row.get('Cat', ''))).strip().lower()
                            cat = normalize_for_compare(cat_orig)
                            subcat_orig = str(row.get('_subcat_for_match', row.get('Subcat', ''))).strip().lower()
                            subcat = normalize_for_compare(subcat_orig)
                            key = normalize_for_compare(row.get('Key', ''))
                            if cat or key:  # 빈 항목 제외
                                vlm_items_list.append({
                                    'cat': cat,
                                    'cat_orig': cat_orig,  # 단어 매칭용
                                    'subcat': subcat,
                                    'subcat_orig': subcat_orig,  # 단어 매칭용
                                    'key': key
                                })
                        
                        # F&F에는 있지만 VLM에 없는 항목 찾기
                        missing_rows = []
                        added_items = set()  # 이미 추가한 항목 추적 (중복 방지)
                        
                        for _, row in fnf_df.iterrows():
                            cat_orig = str(row.get('_cat_for_match', '')).strip().lower()
                            subcat_orig = str(row.get('_subcat_for_match', '')).strip().lower()
                            key_orig = str(row.get('Key', '')).strip().lower()
                            
                            # 정규화된 값
                            cat = normalize_for_compare(cat_orig)
                            subcat = normalize_for_compare(subcat_orig)
                            key = normalize_for_compare(key_orig)
                            
                            # 이미 추가한 항목이면 스킵
                            if (cat, subcat, key) in added_items:
                                continue
                            
                            # 마케팅 항목인지 확인 (Key가 없으면 마케팅)
                            is_marketing = not key
                            
                            # VLM에서 같은 항목 찾기
                            found_match = False
                            is_key_only_missing = False
                            matching_vlm_subcats = []
                            has_same_cat = False
                            
                            if is_marketing:
                                # 마케팅 항목: Cat만 단어 단위로 비교
                                for vlm_item in vlm_items_list:
                                    if match_cat_words(cat_orig, vlm_item['cat_orig']) and not vlm_item['key']:
                                        # Cat이 단어 단위로 일치하고 둘 다 마케팅 항목(key 없음)
                                        found_match = True
                                        has_same_cat = True
                                        break
                                
                                # ⚠️ 마케팅 항목에서 Cat 자체가 없으면 전체 행 빨간색
                                if not has_same_cat:
                                    is_key_only_missing = False
                            else:
                                # 상품 항목: Cat + Subcat + Key 비교 (Cat도 단어 단위)
                                for vlm_item in vlm_items_list:
                                    if match_cat_words(cat_orig, vlm_item['cat_orig']):
                                        has_same_cat = True  # Cat은 단어 단위로 존재
                                        # Cat이 같을 때, Subcat이 단어 단위로 일치하는지 체크
                                        if match_subcat_words(subcat_orig, vlm_item['subcat_orig']):
                                            matching_vlm_subcats.append(vlm_item)
                                
                                if matching_vlm_subcats:
                                    # Subcat이 단어 단위로 일치하는 항목이 VLM에 존재
                                    # 이제 Key가 있는지 체크
                                    for vlm_item in matching_vlm_subcats:
                                        if vlm_item['key'] == key:
                                            # Key도 일치: 완전 일치
                                            found_match = True
                                            break
                                    
                                    # Key가 없으면 Key만 누락
                                    if not found_match:
                                        is_key_only_missing = True
                                
                                # ⚠️ Cat 자체가 VLM에 없으면 Key만 누락이 아님 (전체 Cat-Subcat 누락)
                                if not has_same_cat:
                                    is_key_only_missing = False
                            
                            # 누락된 항목인 경우에만 추가
                            # 조건: cat이 있어야 하고, (마케팅은 key 없음 OR 상품은 key 있음)
                            is_valid_item = cat and (is_marketing or key)  # cat 필수, 마케팅이거나 key 있어야 함
                            
                            if not found_match and is_valid_item:
                                # 🆕 상품 항목: VLM이 같은 Cat을 이미 분석했다면 (다른 Subcat이라도)
                                # Subcat이 다른 것은 누락으로 추가하지 않음 (하이라이팅에서 처리)
                                if not is_marketing and has_same_cat and not matching_vlm_subcats and subcat:
                                    # VLM이 Cat은 인식했지만 Subcat이 완전히 다름
                                    # → 누락 추가 안 함 (VLM의 Subcat이 틀렸다고 빨간색 표시만)
                                    continue
                                
                                # 누락된 항목 추가
                                # Cat/Subcat이 빈값이면 _cat_for_match/_subcat_for_match 사용
                                cat_display = row.get('Cat', '')
                                subcat_display = row.get('Subcat', '')
                                if not cat_display or str(cat_display).strip() == '':
                                    cat_display = cat_orig
                                if not subcat_display or str(subcat_display).strip() == '':
                                    subcat_display = subcat_orig
                                
                                # ⚠️ Key만 누락인 경우, VLM에 이미 있는 Subcat을 사용
                                if is_key_only_missing and matching_vlm_subcats:
                                    # VLM의 Subcat을 사용 (단어 일치하는 첫 번째 항목)
                                    vlm_subcat_orig = matching_vlm_subcats[0]['subcat_orig']
                                    subcat_display = vlm_subcat_orig
                                    subcat_for_match = vlm_subcat_orig
                                else:
                                    subcat_for_match = subcat_orig
                                
                                missing_rows.append({
                                    'Cat': cat_display,
                                    'Subcat': subcat_display,
                                    'Key': row.get('Key', ''),
                                    'Value': '',  # 빈 값
                                    '_cat_for_match': cat_orig,
                                    '_subcat_for_match': subcat_for_match,
                                    '_is_missing': True,  # 누락 표시
                                    '_is_key_only_missing': is_key_only_missing  # Key만 누락인지
                                })
                                added_items.add((cat, subcat, key))
                        
                        if missing_rows:
                            vlm_df_updated = pd.concat([vlm_df, pd.DataFrame(missing_rows)], ignore_index=True)
                            # 다시 정렬
                            return sort_by_category(vlm_df_updated)
                        return vlm_df
                    
                    # 누락된 항목 추가 (F&F 데이터에서 _cat_for_match, _subcat_for_match 확인)
                    # edited_fnf_img에 _cat_for_match, _subcat_for_match가 없을 수 있으니 재생성
                    fnf_for_comparison = edited_fnf_img.copy()
                    if '_cat_for_match' not in fnf_for_comparison.columns or '_subcat_for_match' not in fnf_for_comparison.columns:
                        fnf_for_comparison['_cat_for_match'] = fnf_for_comparison['Cat'].replace('', pd.NA).ffill().fillna('').str.lower()
                        fnf_for_comparison['_subcat_for_match'] = fnf_for_comparison['Subcat'].replace('', pd.NA).ffill().fillna('').str.lower()
                    
                    # 누락 항목 추가 (중복 제거는 이미 위에서 수행됨)
                    df_gemini_clean = add_missing_items(df_gemini_clean, fnf_for_comparison)
                    
                    # 테이블 높이 계산 (누락 항목 포함)
                    table_height_gemini = min(600, 35 * len(df_gemini_clean) + 100)
                    
                    # === 정답률 계산 함수 ===
                    def calculate_accuracy(vlm_df, fnf_df, fnf_lookup, fnf_catsubcat, normalize_text, fuzzy_match_subcat, word_level_match):
                        """VLM 결과의 정답률을 계산합니다. (F&F 정답지 기준)"""
                        marketing_match = 0
                        marketing_total = 0
                        marketing_extra = 0
                        
                        product_match = 0
                        product_total = 0
                        product_extra = 0
                        subcat_errors = 0
                        
                        # 가산점: 브랜드/제품명 인식
                        has_brand = False
                        has_product_name = False
                        
                        # 1단계: VLM에서 (Cat, Subcat, Key) → Value 매핑 생성
                        vlm_lookup = {}
                        for _, vlm_row in vlm_df.iterrows():
                            v_cat = str(vlm_row.get('_cat_for_match', '')).strip().lower()
                            v_subcat = str(vlm_row.get('_subcat_for_match', '')).strip().lower()
                            v_key = str(vlm_row.get('Key', '')).strip().lower()
                            v_val = str(vlm_row.get('Value', '')).strip().lower()
                            
                            # 브랜드/제품명 체크 (가산점)
                            if v_key == 'brand' and v_val:
                                has_brand = True
                            if v_key == 'product_name' and v_val:
                                has_product_name = True
                            
                            # VLM 매핑 저장
                            vlm_lookup[(v_cat, v_subcat, v_key)] = v_val
                            vlm_lookup[(v_cat, v_key)] = v_val
                        
                        # 2단계: F&F 정답지를 순회하면서 VLM 결과와 비교 (F&F 기준)
                        for _, fnf_row in fnf_df.iterrows():
                            f_cat = str(fnf_row.get('_cat_for_match', '')).strip().lower()
                            f_subcat = str(fnf_row.get('_subcat_for_match', '')).strip().lower()
                            f_key = str(fnf_row.get('Key', '')).strip().lower()
                            f_val = str(fnf_row.get('Value', '')).strip().lower()
                            
                            # 마케팅 카테고리 (Key 없음)
                            is_marketing = not f_key
                            
                            # VLM 값 찾기 (Cat도 단어 단위로 매칭)
                            v_val = ''
                            # 먼저 정확한 조합으로 시도
                            v_val = vlm_lookup.get((f_cat, f_subcat, f_key), 
                                                   vlm_lookup.get((f_cat, f_key), ''))
                            
                            # 없으면 단어 단위로 일치하는 Cat 찾기
                            if not v_val:
                                if not f_key:  # 마케팅 항목
                                    # Cat만 단어 단위로 매칭
                                    for key, val in vlm_lookup.items():
                                        if len(key) == 2 and key[1] == '' and word_level_match(f_cat, key[0]):
                                            v_val = val
                                            break
                                else:  # 상품 항목
                                    for key, val in vlm_lookup.items():
                                        if len(key) == 3:
                                            v_cat, v_subcat, v_key = key
                                            # Cat 단어 일치 + Key 정확 일치 + Subcat 퍼지 매칭
                                            if word_level_match(f_cat, v_cat) and v_key == f_key:
                                                if not f_subcat or not v_subcat or fuzzy_match_subcat(f_subcat, v_subcat):
                                                    v_val = val
                                                    break
                            
                            if is_marketing and f_val:  # 마케팅
                                marketing_total += 1
                                if v_val:  # VLM이 해당 항목 분석함
                                    # 단어 단위 매칭 체크
                                    if word_level_match(f_val, v_val):
                                        marketing_match += 1
                                # VLM이 누락하면 marketing_match 증가 안함 (자동 감점)
                            
                            elif not is_marketing and f_val:  # 상품
                                product_total += 1
                                
                                # Subcat 검증 (Cat도 단어 단위로 매칭)
                                if f_cat and f_subcat and f_key and v_val:
                                    # VLM의 Subcat 찾기 (원본 데이터에서, Cat 단어 매칭)
                                    vlm_matching_rows = []
                                    for _, vlm_row in vlm_df.iterrows():
                                        vlm_cat = str(vlm_row.get('_cat_for_match', '')).strip().lower()
                                        vlm_key = str(vlm_row.get('Key', '')).strip().lower()
                                        if word_level_match(f_cat, vlm_cat) and vlm_key == f_key:
                                            vlm_matching_rows.append(vlm_row)
                                            break
                                    
                                    if vlm_matching_rows:
                                        v_subcat_check = str(vlm_matching_rows[0].get('_subcat_for_match', '')).strip().lower()
                                        if v_subcat_check:
                                            is_valid_subcat = fuzzy_match_subcat(v_subcat_check, f_subcat)
                                            if not is_valid_subcat:
                                                subcat_errors += 1
                                
                                # Value 검증
                                if v_val:  # VLM이 해당 항목 분석함
                                    # 단어 단위 매칭 체크
                                    if word_level_match(f_val, v_val):
                                        product_match += 1
                                # VLM이 누락하면 product_match 증가 안함 (자동 감점)
                        
                        # 3단계: VLM에만 있는 항목 체크 (추가 분석)
                        for _, vlm_row in vlm_df.iterrows():
                            v_cat = str(vlm_row.get('_cat_for_match', '')).strip().lower()
                            v_subcat = str(vlm_row.get('_subcat_for_match', '')).strip().lower()
                            v_key = str(vlm_row.get('Key', '')).strip().lower()
                            v_val = str(vlm_row.get('Value', '')).strip().lower()
                            
                            if not v_val:
                                continue
                            
                            # 마케팅 카테고리
                            is_marketing = not v_key
                            
                            # F&F에 없는지 체크 (Cat도 단어 단위로 매칭)
                            f_val = fnf_lookup.get((v_cat, v_subcat, v_key), 
                                                   fnf_lookup.get((v_cat, v_key), ''))
                            
                            # 없으면 단어 단위로 일치하는 Cat 찾기
                            if not f_val:
                                if not v_key:  # 마케팅 항목
                                    for key, val in fnf_lookup.items():
                                        if len(key) == 2 and key[1] == '' and word_level_match(v_cat, key[0]):
                                            f_val = val
                                            break
                                else:  # 상품 항목
                                    for key, val in fnf_lookup.items():
                                        if len(key) == 3:
                                            f_cat, f_subcat, f_key = key
                                            if word_level_match(v_cat, f_cat) and v_key == f_key:
                                                if not v_subcat or not f_subcat or fuzzy_match_subcat(v_subcat, f_subcat):
                                                    f_val = val
                                                    break
                            
                            if not f_val:  # F&F에 없음
                                if is_marketing:
                                    marketing_extra += 1
                                else:
                                    product_extra += 1
                        
                        # 정답률 계산
                        marketing_acc = (marketing_match / marketing_total * 100) if marketing_total > 0 else 0
                        
                        # 상품 정답률 - 복합 계산 (Value 60% + Subcat 40%)
                        if product_total > 0:
                            value_acc = (product_match / product_total) * 100  # Value 정확도
                            subcat_acc = ((product_total - subcat_errors) / product_total) * 100  # Subcat 정확도
                            product_acc = (value_acc * 0.6) + (subcat_acc * 0.4)  # 가중 평균
                        else:
                            value_acc = 0
                            subcat_acc = 0
                            product_acc = 0
                        
                        return {
                            'marketing_acc': marketing_acc,
                            'marketing_match': marketing_match,
                            'marketing_total': marketing_total,
                            'marketing_extra': marketing_extra,
                            'product_acc': product_acc,
                            'value_acc': value_acc,  # 추가
                            'subcat_acc': subcat_acc,  # 추가
                            'product_match': product_match,
                            'product_total': product_total,
                            'product_extra': product_extra,
                            'subcat_errors': subcat_errors,
                            'has_brand': has_brand,
                            'has_product_name': has_product_name
                        }
                    
                    # 정규화 함수: 하이픈, 공백, 언더스코어 제거
                    def normalize_text(text):
                        if not text:
                            return ''
                        return str(text).strip().lower().replace('-', '').replace(' ', '').replace('_', '')
                    
                    # 단어 단위 매칭 함수
                    def word_level_match(val1, val2):
                        """두 값이 단어 단위로 하나라도 겹치면 True (공백/하이픈 무시)"""
                        if not val1 or not val2:
                            return False
                        
                        def normalize_word(word):
                            """단어 정규화: 소문자 + 공백/하이픈/언더스코어 제거"""
                            return word.strip().lower().replace(' ', '').replace('-', '').replace('_', '')
                        
                        # 쉼표로 split (여러 값 처리)
                        vals1 = [v.strip().lower() for v in str(val1).split(',')]
                        vals2 = [v.strip().lower() for v in str(val2).split(',')]
                        
                        # 각 값에서 단어 추출 및 정규화
                        words1 = set()
                        for v in vals1:
                            # 공백으로 구분된 단어들
                            for word in v.split():
                                normalized = normalize_word(word)
                                if normalized:
                                    words1.add(normalized)
                            # 전체 문구도 정규화하여 추가 (예: "sky blue" → "skyblue")
                            full_normalized = normalize_word(v)
                            if full_normalized:
                                words1.add(full_normalized)
                        
                        words2 = set()
                        for v in vals2:
                            for word in v.split():
                                normalized = normalize_word(word)
                                if normalized:
                                    words2.add(normalized)
                            full_normalized = normalize_word(v)
                            if full_normalized:
                                words2.add(full_normalized)
                        
                        # 단어가 하나라도 겹치면 True
                        return len(words1 & words2) > 0
                    
                    
                    # Subcat 퍼지 매칭 함수: 복수형 제거 + 부분 일치
                    def fuzzy_match_subcat(subcat1, subcat2):
                        """Subcat이 유사한지 체크 (단어 단위 매칭, 복수형 허용)"""
                        if not subcat1 or not subcat2:
                            return False
                        
                        # 쉼표로 split (여러 값 처리: "running shoes, sneakers")
                        vals1 = [v.strip().lower() for v in str(subcat1).split(',')]
                        vals2 = [v.strip().lower() for v in str(subcat2).split(',')]
                        
                        # 각 값에서 단어 추출 (정규화 + 복수형 제거)
                        words1 = set()
                        for v in vals1:
                            # 단어별로 정규화 + 복수형 제거
                            for word in v.split():
                                normalized = normalize_text(word).rstrip('s')
                                if normalized:  # 빈 문자열 제외
                                    words1.add(normalized)
                        
                        words2 = set()
                        for v in vals2:
                            for word in v.split():
                                normalized = normalize_text(word).rstrip('s')
                                if normalized:
                                    words2.add(normalized)
                        
                        # 단어가 하나라도 겹치면 True
                        return bool(words1 & words2)
                    
                    # F&F에서 (Cat, Subcat, Key) → Value 매핑 + Cat/Subcat 조합 저장
                    # 편집된 데이터(edited_fnf_img)를 사용하여 매핑 생성
                    fnf_lookup = {}
                    fnf_catsubcat = {}  # Cat별 가능한 Subcat 저장 (정규화된 값)
                    
                    for _, r in edited_fnf_img.iterrows():
                        cat = str(r.get('_cat_for_match', r.get('Cat', ''))).strip().lower()
                        subcat = str(r.get('_subcat_for_match', r.get('Subcat', ''))).strip().lower()
                        key = str(r.get('Key', '')).strip().lower()
                        val = str(r.get('Value', '')).strip().lower()
                        
                        # Value가 실제로 있는 경우만 저장 (빈 값은 건너뛰기)
                        if not val or val == 'nan':
                            continue
                        
                        # Value 매핑 (중복 키가 있으면 첫 번째 값만 유지)
                        key3 = (cat, subcat, key)
                        key2 = (cat, key)
                        
                        if key3 not in fnf_lookup:
                            fnf_lookup[key3] = val
                        if key2 not in fnf_lookup:
                            fnf_lookup[key2] = val
                        
                        # Cat별 Subcat 수집 (원본 값 저장, fuzzy_match_subcat에서 정규화 처리)
                        if cat and subcat:
                            if cat not in fnf_catsubcat:
                                fnf_catsubcat[cat] = set()
                            fnf_catsubcat[cat].add(subcat)  # 원본 값 저장 (lower만 적용)
                    
                    def highlight_gemini(row):
                        # 전체 컬럼 수에 맞춰 스타일 배열 생성
                        styles = [''] * len(row)
                        
                        # 누락된 항목인지 체크 (문자열로 변환되었을 수 있으므로 명시적 비교)
                        is_missing = row.get('_is_missing', False)
                        is_key_only_missing = row.get('_is_key_only_missing', False)
                        
                        # boolean이든 문자열이든 True/true로 처리
                        if isinstance(is_missing, str):
                            is_missing = is_missing.lower() == 'true'
                        if isinstance(is_key_only_missing, str):
                            is_key_only_missing = is_key_only_missing.lower() == 'true'
                        
                        if is_missing:
                            if is_key_only_missing:
                                # Cat-Subcat은 분석됐는데 Key만 누락: Value만 빨간색
                                value_idx = list(row.index).index('Value') if 'Value' in row.index else 3
                                styles[value_idx] = 'background-color: #f8d7da'
                                return styles
                            else:
                                # Cat-Subcat 자체가 누락: 전체 행 빨간색
                                return ['background-color: #f8d7da'] * len(row)
                        
                        # 매칭에는 ffill된 값 사용
                        g_cat = str(row.get('_cat_for_match', '')).strip().lower()
                        g_subcat = str(row.get('_subcat_for_match', '')).strip().lower()
                        g_key = str(row.get('Key', '')).strip().lower()
                        g_val = str(row.get('Value', '')).strip().lower()
                        
                        # 컬럼 인덱스 찾기
                        subcat_idx = list(row.index).index('Subcat') if 'Subcat' in row.index else 1
                        value_idx = list(row.index).index('Value') if 'Value' in row.index else 3
                        
                        # (cat, subcat) 조합이 F&F에 있는지 체크 (상품 카테고리만)
                        is_new_catsubcat = False
                        is_subcat_wrong = False  # 🆕 Subcat이 틀렸는지 추적
                        
                        if g_cat and g_subcat and g_key:  # 마케팅 제외
                            # F&F에 정확히 일치하는 Cat이 있는지 확인
                            if g_cat in fnf_catsubcat:
                                # F&F에 같은 Cat이 있으면 Subcat 검증 (단어 단위로 비교)
                                is_valid_subcat = any(
                                    fuzzy_match_subcat(g_subcat, fnf_sub)
                                    for fnf_sub in fnf_catsubcat[g_cat]
                                )
                                
                                if not is_valid_subcat:
                                    # Subcat이 틀렸으면 Subcat 빨간색
                                    styles[subcat_idx] = 'background-color: #f8d7da'
                                    is_subcat_wrong = True  # 🆕 플래그 설정
                            else:
                                # F&F에 해당 Cat이 아예 없으면 신규 Cat-Subcat 조합
                                is_new_catsubcat = True
                        
                        # Value 검증
                        # F&F에서 같은 (Cat, Subcat, Key) 찾기 (Cat도 단어 단위로)
                        # 마케팅 항목(Key가 빈 문자열)의 경우 (cat, '') 조합으로도 조회
                        f_val = ''
                        if not g_key:  # 마케팅 카테고리
                            # 마케팅 카테고리는 정확히 일치해야 함 (word_level_match 사용 안함)
                            lookup_key = (g_cat, '')
                            if lookup_key in fnf_lookup:
                                f_val = fnf_lookup[lookup_key].lower()
                        else:  # 상품 카테고리
                            # 🆕 Subcat이 틀린 경우 (cat, key)만으로 조회
                            if is_subcat_wrong:
                                f_val = fnf_lookup.get((g_cat, g_key), '').lower()
                            else:
                                # 정확한 (Cat, Subcat, Key) 조합으로 조회
                                f_val = fnf_lookup.get((g_cat, g_subcat, g_key), '').lower()
                                
                                # 없으면 Subcat을 정규화해서 재시도 (하이픈, 공백, 언더스코어 무시)
                                if not f_val:
                                    g_subcat_normalized = normalize_text(g_subcat)
                                    for fnf_cat_key in fnf_lookup.keys():
                                        if len(fnf_cat_key) == 3:  # (cat, subcat, key) 조합
                                            fnf_cat, fnf_subcat, fnf_key = fnf_cat_key
                                            # Cat과 Key는 정확히 일치, Subcat은 정규화해서 비교
                                            if (g_cat == fnf_cat and g_key == fnf_key and 
                                                g_subcat_normalized == normalize_text(fnf_subcat)):
                                                f_val = fnf_lookup[fnf_cat_key].lower()
                                                break
                        
                        if f_val:  # F&F에 값이 있을 때
                            # 🆕 VLM Value가 실제로 값이 있는지 명확히 체크 (공백, nan 등 제외)
                            g_val_str = str(g_val).strip().lower()
                            has_valid_value = g_val_str and g_val_str not in ['nan', 'none', 'null', 'n/a', '']
                            
                            # 단어 단위 매칭 체크
                            if has_valid_value and word_level_match(f_val, g_val):
                                pass  # 일치: 무색
                            elif has_valid_value:
                                styles[value_idx] = 'background-color: #f8d7da'  # 불일치: 빨간색
                            else:
                                # F&F에 값이 있는데 VLM이 누락 (빈 값)
                                styles[value_idx] = 'background-color: #f8d7da'  # 누락: 빨간색
                        else:
                            # F&F에 값이 없는 경우
                            # VLM Value가 실제로 값이 있는지 체크 (유효한 값인지)
                            g_val_str = str(g_val).strip().lower()
                            has_valid_value = g_val_str and g_val_str not in ['nan', 'none', 'null', 'n/a', '']
                            
                            if has_valid_value:  # F&F에 없는데 Gemini가 추가 분석한 값
                                if is_new_catsubcat:
                                    # 🆕 상품 카테고리에서 F&F에 없는 Cat → 오류 (빨간색)
                                    return ['background-color: #f8d7da'] * len(row)
                                else:
                                    # 기존 Cat-Subcat에서 Key만 추가된 경우 Value만 초록색
                                    styles[value_idx] = 'background-color: #d4edda'
                        
                        return styles
                    
                    # 원본 데이터 사용 (읽기 전용)
                    df_gemini_display = df_gemini_clean.copy()
                    
                    # 하이라이팅 테이블 표시
                    table_height_gemini = min(600, 35 * len(df_gemini_display) + 100)
                    st.dataframe(
                        df_gemini_display.style.apply(highlight_gemini, axis=1),
                        use_container_width=True, height=table_height_gemini, hide_index=True,
                        column_config={
                            '_cat_for_match': None,  # 숨김
                            '_subcat_for_match': None,  # 숨김
                            '_is_missing': None,  # 숨김
                            '_is_key_only_missing': None  # 숨김
                        }
                    )
                    
                    # Gemini 정답률 계산 및 표시 (맨 하단) - 편집된 데이터 사용
                    gemini_acc = calculate_accuracy(df_gemini_display, edited_fnf_img, fnf_lookup, fnf_catsubcat, normalize_text, fuzzy_match_subcat, word_level_match)
                    
                    # 전체 정답률 계산을 위해 리스트에 추가
                    gemini_marketing_rates.append(gemini_acc['marketing_acc'])
                    gemini_product_rates.append(gemini_acc['product_acc'])
                    
                    # 가산점 텍스트 생성
                    bonus_text = ""
                    if gemini_acc['has_brand'] or gemini_acc['has_product_name']:
                        bonus_items = []
                        if gemini_acc['has_brand']:
                            bonus_items.append("🏷️브랜드")
                        if gemini_acc['has_product_name']:
                            bonus_items.append("📦제품명")
                        bonus_text = f" +{', '.join(bonus_items)}"
                    
                    st.caption(f"""
                    **정답률** (F&F 기준)  
                    마케팅: **{gemini_acc['marketing_acc']:.1f}%** ({gemini_acc['marketing_match']}/{gemini_acc['marketing_total']}개 정답{f", 누락 {gemini_acc['marketing_total'] - gemini_acc['marketing_match']}개" if gemini_acc['marketing_match'] < gemini_acc['marketing_total'] else ""}{f", +{gemini_acc['marketing_extra']}개 추가분석" if gemini_acc['marketing_extra'] > 0 else ""})  
                    상품: **{gemini_acc['product_acc']:.1f}%** (정답 {gemini_acc['product_match']}/{gemini_acc['product_total']}개, Value×0.6 + Subcat×0.4{f", Subcat오류 {gemini_acc['subcat_errors']}개" if gemini_acc['subcat_errors'] > 0 else ""}{f", +{gemini_acc['product_extra']}개 추가" if gemini_acc['product_extra'] > 0 else ""}){bonus_text}
                    """)
                
                with t3:
                    st.markdown("**🟨 오드컨셉**")
                    
                    # 오드컨셉 데이터 처리 (엑셀 파일 기반, 편집 불가)
                    
                    # 누락 항목 추가 (중복 제거는 이미 위에서 수행됨)
                    df_odd_img = add_missing_items(df_odd_img, fnf_for_comparison)
                    
                    # 테이블 높이 계산 (누락 항목 포함)
                    table_height_odd = min(600, 35 * len(df_odd_img) + 100)
                    
                    def highlight_odd(row):
                        # 전체 컬럼 수에 맞춰 스타일 배열 생성
                        styles = [''] * len(row)
                        
                        # 누락된 항목인지 체크 (문자열로 변환되었을 수 있으므로 명시적 비교)
                        is_missing = row.get('_is_missing', False)
                        is_key_only_missing = row.get('_is_key_only_missing', False)
                        
                        # boolean이든 문자열이든 True/true로 처리
                        if isinstance(is_missing, str):
                            is_missing = is_missing.lower() == 'true'
                        if isinstance(is_key_only_missing, str):
                            is_key_only_missing = is_key_only_missing.lower() == 'true'
                        
                        if is_missing:
                            if is_key_only_missing:
                                # Cat-Subcat은 분석됐는데 Key만 누락: Value만 빨간색
                                value_idx = list(row.index).index('Value') if 'Value' in row.index else 3
                                styles[value_idx] = 'background-color: #f8d7da'
                                return styles
                            else:
                                # Cat-Subcat 자체가 누락: 전체 행 빨간색
                                return ['background-color: #f8d7da'] * len(row)
                        
                        # 매칭에는 ffill된 값 사용
                        o_cat = str(row.get('_cat_for_match', '')).strip().lower()
                        o_subcat = str(row.get('_subcat_for_match', '')).strip().lower()
                        o_key = str(row.get('Key', '')).strip().lower()
                        o_val = str(row.get('Value', '')).strip().lower()
                        
                        # 컬럼 인덱스 찾기
                        subcat_idx = list(row.index).index('Subcat') if 'Subcat' in row.index else 1
                        value_idx = list(row.index).index('Value') if 'Value' in row.index else 3
                        
                        # (cat, subcat) 조합이 F&F에 있는지 체크 (상품 카테고리만)
                        is_new_catsubcat = False
                        is_subcat_wrong = False  # 🆕 Subcat이 틀렸는지 추적
                        
                        if o_cat and o_subcat and o_key:  # 마케팅 제외
                            # F&F에 정확히 일치하는 Cat이 있는지 확인
                            if o_cat in fnf_catsubcat:
                                # F&F에 같은 Cat이 있으면 Subcat 검증 (단어 단위로 비교)
                                is_valid_subcat = any(
                                    fuzzy_match_subcat(o_subcat, fnf_sub)
                                    for fnf_sub in fnf_catsubcat[o_cat]
                                )
                                
                                if not is_valid_subcat:
                                    # Subcat이 틀렸으면 Subcat 빨간색
                                    styles[subcat_idx] = 'background-color: #f8d7da'
                                    is_subcat_wrong = True  # 🆕 플래그 설정
                            else:
                                # F&F에 해당 Cat이 아예 없으면 신규 Cat-Subcat 조합
                                is_new_catsubcat = True
                        
                        # Value 검증
                        # F&F에서 같은 (Cat, Subcat, Key) 찾기 (Cat도 단어 단위로)
                        # 마케팅 항목(Key가 빈 문자열)의 경우 (cat, '') 조합으로도 조회
                        f_val = ''
                        if not o_key:  # 마케팅 카테고리
                            # 마케팅 카테고리는 정확히 일치해야 함 (word_level_match 사용 안함)
                            lookup_key = (o_cat, '')
                            if lookup_key in fnf_lookup:
                                f_val = fnf_lookup[lookup_key].lower()
                        else:  # 상품 카테고리
                            # 🆕 Subcat이 틀린 경우 (cat, key)만으로 조회
                            if is_subcat_wrong:
                                f_val = fnf_lookup.get((o_cat, o_key), '').lower()
                            else:
                                # 정확한 (Cat, Subcat, Key) 조합으로 조회
                                f_val = fnf_lookup.get((o_cat, o_subcat, o_key), '').lower()
                                
                                # 없으면 Subcat을 정규화해서 재시도 (하이픈, 공백, 언더스코어 무시)
                                if not f_val:
                                    o_subcat_normalized = normalize_text(o_subcat)
                                    for fnf_cat_key in fnf_lookup.keys():
                                        if len(fnf_cat_key) == 3:  # (cat, subcat, key) 조합
                                            fnf_cat, fnf_subcat, fnf_key = fnf_cat_key
                                            # Cat과 Key는 정확히 일치, Subcat은 정규화해서 비교
                                            if (o_cat == fnf_cat and o_key == fnf_key and 
                                                o_subcat_normalized == normalize_text(fnf_subcat)):
                                                f_val = fnf_lookup[fnf_cat_key].lower()
                                                break
                        
                        if f_val:  # F&F에 값이 있을 때
                            # 🆕 VLM Value가 실제로 값이 있는지 명확히 체크 (공백, nan 등 제외)
                            o_val_str = str(o_val).strip().lower()
                            has_valid_value = o_val_str and o_val_str not in ['nan', 'none', 'null', 'n/a', '']
                            
                            # 단어 단위 매칭 체크
                            if has_valid_value and word_level_match(f_val, o_val):
                                pass  # 일치: 무색
                            elif has_valid_value:
                                styles[value_idx] = 'background-color: #f8d7da'  # 불일치: 빨간색
                            else:
                                # F&F에 값이 있는데 VLM이 누락 (빈 값)
                                styles[value_idx] = 'background-color: #f8d7da'  # 누락: 빨간색
                        else:
                            # F&F에 값이 없는 경우
                            # VLM Value가 실제로 값이 있는지 체크 (유효한 값인지)
                            o_val_str = str(o_val).strip().lower()
                            has_valid_value = o_val_str and o_val_str not in ['nan', 'none', 'null', 'n/a', '']
                            
                            if has_valid_value:  # F&F에 없는데 오드컨셉이 추가 분석한 값
                                if is_new_catsubcat:
                                    # 🆕 상품 카테고리에서 F&F에 없는 Cat → 오류 (빨간색)
                                    return ['background-color: #f8d7da'] * len(row)
                                else:
                                    # 기존 Cat-Subcat에서 Key만 추가된 경우 Value만 초록색
                                    styles[value_idx] = 'background-color: #d4edda'
                        return styles
                    
                    # 원본 데이터 사용 (읽기 전용)
                    df_odd_display = df_odd_img.copy()
                    
                    # 하이라이팅 테이블 표시
                    table_height_odd = min(600, 35 * len(df_odd_display) + 100)
                    st.dataframe(
                        df_odd_display.style.apply(highlight_odd, axis=1),
                        use_container_width=True, height=table_height_odd, hide_index=True,
                        column_config={
                            '_cat_for_match': None,  # 숨김
                            '_subcat_for_match': None,  # 숨김
                            '_is_missing': None,  # 숨김
                            '_is_key_only_missing': None  # 숨김
                        }
                    )
                    
                    # 오드컨셉 정답률 계산 및 표시 (맨 하단) - 편집된 데이터 사용
                    odd_acc = calculate_accuracy(df_odd_display, edited_fnf_img, fnf_lookup, fnf_catsubcat, normalize_text, fuzzy_match_subcat, word_level_match)
                    
                    # 전체 정답률 계산을 위해 리스트에 추가
                    odd_marketing_rates.append(odd_acc['marketing_acc'])
                    odd_product_rates.append(odd_acc['product_acc'])
                    
                    # 가산점 텍스트 생성
                    odd_bonus_text = ""
                    if odd_acc['has_brand'] or odd_acc['has_product_name']:
                        odd_bonus_items = []
                        if odd_acc['has_brand']:
                            odd_bonus_items.append("🏷️브랜드")
                        if odd_acc['has_product_name']:
                            odd_bonus_items.append("📦제품명")
                        odd_bonus_text = f" +{', '.join(odd_bonus_items)}"
                    
                    st.caption(f"""
                    **정답률** (F&F 기준)  
                    마케팅: **{odd_acc['marketing_acc']:.1f}%** ({odd_acc['marketing_match']}/{odd_acc['marketing_total']}개 정답{f", 누락 {odd_acc['marketing_total'] - odd_acc['marketing_match']}개" if odd_acc['marketing_match'] < odd_acc['marketing_total'] else ""}{f", +{odd_acc['marketing_extra']}개 추가분석" if odd_acc['marketing_extra'] > 0 else ""})  
                    상품: **{odd_acc['product_acc']:.1f}%** (정답 {odd_acc['product_match']}/{odd_acc['product_total']}개, Value×0.6 + Subcat×0.4{f", Subcat오류 {odd_acc['subcat_errors']}개" if odd_acc['subcat_errors'] > 0 else ""}{f", +{odd_acc['product_extra']}개 추가" if odd_acc['product_extra'] > 0 else ""}){odd_bonus_text}
                    """)
            
            st.divider()
    
    # ==========================================================================
    # 전체 정답률 요약 업데이트
    # ==========================================================================
    with summary_placeholder.container():
        # 평균 정답률 계산
        avg_gemini_marketing = sum(gemini_marketing_rates) / len(gemini_marketing_rates) if gemini_marketing_rates else 0
        avg_gemini_product = sum(gemini_product_rates) / len(gemini_product_rates) if gemini_product_rates else 0
        avg_gemini = (avg_gemini_marketing + avg_gemini_product) / 2
        
        avg_odd_marketing = sum(odd_marketing_rates) / len(odd_marketing_rates) if odd_marketing_rates else 0
        avg_odd_product = sum(odd_product_rates) / len(odd_product_rates) if odd_product_rates else 0
        avg_odd = (avg_odd_marketing + avg_odd_product) / 2
        
        st.markdown(f"""
        <span style="font-size: 20px; font-weight: bold;">총 비교 항목 (중복 제외): {total_unique_items}개</span>
        """, unsafe_allow_html=True)
        
        sum_col1, sum_col2 = st.columns(2)
        with sum_col1:
            st.markdown(f"""
            **Gemini 평균 정답률**  
            <span style="font-size: 28px; font-weight: bold;">{avg_gemini:.1f}%</span>  
            마케팅: {avg_gemini_marketing:.1f}% / 상품: {avg_gemini_product:.1f}%
            """, unsafe_allow_html=True)
        with sum_col2:
            st.markdown(f"""
            **오드컨셉 평균 정답률**  
            <span style="font-size: 28px; font-weight: bold;">{avg_odd:.1f}%</span>  
            마케팅: {avg_odd_marketing:.1f}% / 상품: {avg_odd_product:.1f}%
            """, unsafe_allow_html=True)
    
    # ==========================================================================
    # 시스템 정보
    # ==========================================================================
    st.divider()
    st.subheader("시스템 정보")
    
    # Gemini 결과 파일 정보 표시
    df_gemini_raw, gemini_file = load_gemini_results()
    if gemini_file:
        st.success(f"Gemini 분석 결과: `{gemini_file}` 로드됨")
    else:
        st.warning("⚠️ Gemini 분석 결과가 없습니다. `python vlm_test.py` 실행 후 새로고침하세요.")
    
    # 데이터 새로고침 버튼 (캐시 삭제)
    if st.button("🔄 데이터 새로고침"):
        st.cache_data.clear()
        st.rerun()


if __name__ == "__main__":
    main()
