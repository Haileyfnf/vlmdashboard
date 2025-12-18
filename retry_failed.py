"""
실패한 이미지만 재분석하는 스크립트
"""
import pandas as pd
from pathlib import Path
from vlm_test import analyze_single_image, load_all_references

# 최신 결과 파일 찾기
OUTPUT_DIR = Path("output")
result_files = sorted(OUTPUT_DIR.glob("vlm_analysis_result_*.xlsx"), key=lambda x: x.stat().st_mtime, reverse=True)

if not result_files:
    print("❌ 결과 파일이 없습니다.")
    exit(1)

latest_file = result_files[0]
print(f"📂 최신 결과 파일: {latest_file.name}")

# 에러 행 찾기
df = pd.read_excel(latest_file)
error_rows = df[df['Cat'] == 'Error']

if len(error_rows) == 0:
    print("✅ 실패한 이미지가 없습니다!")
    exit(0)

print(f"\n⚠️ 실패한 이미지 {len(error_rows)}개 발견:")
failed_images = error_rows['Image'].unique().tolist()
for img in failed_images:
    print(f"  - {img}")

print("\n🔄 재분석 시작...")

# 기준정보 로드
references = load_all_references()

# 각 이미지 재분석
for img_name in failed_images:
    img_path = Path(img_name)
    if not img_path.exists():
        print(f"❌ 파일을 찾을 수 없습니다: {img_name}")
        continue
    
    print(f"\n🔍 재분석 중: {img_name}")
    try:
        result = analyze_single_image(str(img_path), references)
        print(f"  ✅ 성공")
    except Exception as e:
        print(f"  ❌ 실패: {e}")

print("\n✅ 재분석 완료! vlm_test.py를 다시 실행하거나 수동으로 결과를 추가하세요.")



