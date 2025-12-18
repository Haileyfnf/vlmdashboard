"""
카테고리별 분석 속성 정의
"""

# =============================================================================
# 공통 속성 (모든 의류 카테고리에 적용)
# =============================================================================
COMMON_ATTRIBUTES = {
    "brand": ["Nike", "Adidas", "Zara", "H&M", "Uniqlo", "Gucci", "Prada", "Louis Vuitton", "Chanel", "New Balance", "Converse", "Vans", "Fila", "Puma", "etc"],
    "product_name": ["(specific product name if identifiable)", "etc"],
    "color": ["red", "blue", "white", "black", "navy", "gray", "beige", "brown", "green", "yellow", "pink", "orange", "purple", "burgundy", "cream", "ivory", "khaki", "olive", "coral", "mint", "sky blue", "light gray", "dark gray", "charcoal", "camel", "tan", "gold", "silver", "etc"],
    "color coordination": ["multi color", "single color", "two tone", "gradient", "color block", "etc"],
    "fabrication": ["jersey knit", "woven", "denim", "leather", "cotton", "polyester", "wool", "silk", "linen", "velvet", "satin", "chiffon", "lace", "mesh", "fleece", "corduroy", "tweed", "cashmere", "nylon", "etc"],
    "pattern": ["solid", "stripe", "check", "plaid", "floral", "polka dot", "animal print", "leopard pattern", "camouflage", "graphic", "logo", "abstract", "geometric", "paisley", "houndstooth", "gingham", "tartan", "tie-dye", "etc"]
}

# =============================================================================
# Inner (이너/상의) 속성
# =============================================================================
INNER_ATTRIBUTES = {
    "inner neckline": ["turtle neck", "cowl neck", "mock neck", "crew neck", "round neck", "scoop neck", "v neck", "split neck", "square neck", "sweetheart neck", "halter neck", "hooley neck", "shirt collar", "scallop collar", "camp collar", "shawl collar", "mandarin collar", "peter pan collar", "cascade collar", "tie neck collar", "sailor collar", "hood", "wide collar", "polo collar", "asymmetrical neck", "boat neck", "collarless"],
    "inner front detail": ["eyelet", "lace", "wrap", "cut-out", "twisted", "ruched", "drape", "braid trim", "ribbon", "elastic", "shirring", "belt", "buckle", "suspender", "zipper", "button", "pom-pom", "piping", "stitching", "beads", "embroidery", "applique", "patchwork", "fringe", "sequins", "tassel", "raw hem", "metal stud", "quilting", "pleats", "pintuck", "ruffle"],
    "inner shoulder type": ["off the shoulder", "one shoulder", "raglan"],
    "inner strap style": ["strapless", "asymmetric-strap", "spaghetti-strap", "adjustable-strap", "multi-way-strap", "halter strap", "cross-back strap"],
    "inner front closure": ["half zip up", "full zip up", "full-button", "half-button", "lace-up front", "toggle-closure", "velcro-closure", "open-front"],
    "inner sleeve type": ["dolman sleeves", "bell sleeves", "petal sleeves", "puff sleeves", "balloon sleeves", "bishop sleeves", "split sleeves"],
    "inner cuff detail": ["one button cuff", "two buttons cuff", "triple buttons cuff", "draped cuff", "shirred cuff", "bib cuff", "pleated cuff", "velcro cuff", "elastic cuff", "tie cuff", "zippered cuff", "french cuff", "frill-cuff", "rolled cuff", "split-cuff", "strapped cuff"],
    "inner fabric sheerness": ["opaque", "sheer", "slightly-sheer", "partial-sheer", "ultra-sheer"],
    "sleeve length": ["extra-long sleeves", "long sleeves", "three-quarter sleeves", "short sleeves", "cap sleeves", "sleeveless"],
    "inner back detail": ["keyhole", "cut-out", "twisted", "ruched", "drape", "braid trim", "ribbon", "elastic", "drawstring", "belt", "buckle", "suspender", "D-ring", "strap", "eyelet lace", "patchwork", "ruffle", "pleats", "smocked", "ruching", "sequined", "embroidery", "applique", "piping", "stitching", "beads", "tassel", "raw hem"],
    "inner side detail": ["slit", "cut-out", "zipper", "button", "velcro", "lace up", "drawstring", "buckle", "D-ring", "strap", "clasp", "elastic", "piping", "braid trim", "stitching", "embroidery", "applique", "patchwork", "stud", "fringe", "ruffle", "pleats", "pintuck", "shirred-smocked", "ruching", "sequined", "beads", "eyelet lace", "ribbon", "raw hem", "pocket"],
    "inner silhouette": ["slim fit", "regular fit", "oversize fit"],
    "inner length": ["cropped length", "waist length", "hip length", "mid thigh length"]
}

# =============================================================================
# Outer (아우터) 속성
# =============================================================================
OUTER_ATTRIBUTES = {
    "outer neckline": ["notched collar", "peak-lapel", "shirt collar", "camp collar", "shawl collar", "band collar", "mandarin collar", "wide collar", "cascade collar", "fur neck", "collarless", "asymmetrical neck", "hood"],
    "outer front detail": ["lapel", "collar", "hood", "storm-flap", "pocket", "button", "zipper", "velcro", "belt", "buckle", "D-ring", "chain", "strap", "drawstring", "elastic", "epaulette", "stud", "metal stud", "piping", "quilting", "ruffle", "pleats", "pintuck", "shirred-smocked", "ruching", "embroidery", "applique", "patchwork", "fringe", "sequins", "beads", "tassel", "pom-pom", "raw hem", "stitching", "eyelet lace", "braid trim"],
    "outer back detail": ["epaulette", "yoke", "vent", "slit", "fishtail hem", "belt", "buckle", "D-ring", "strap", "drawstring", "elastic", "piping", "quilting", "pleats", "pintuck", "shirred-smocked", "ruching", "embroidery", "applique", "patchwork", "fringe", "sequins", "beads", "tassel", "raw hem", "stitching", "metal stud"],
    "outer side detail": ["slit", "zipper", "button", "velcro", "lace-up", "drawstring", "buckle", "D-ring", "strap", "chain", "elastic", "piping", "braid trim", "stitching", "embroidery", "applique", "patchwork", "studs", "fringe", "ruffle", "pleats", "pintuck", "shirred-smocked", "ruching", "sequins", "beads", "tassel", "eyelet lace", "ribbon", "raw hem", "pocket", "welt pocket", "zipper pocket", "flap pocket"],
    "outer shoulder type": ["off the shoulder", "one shoulder", "raglan", "cape shoulder", "drop shoulder"],
    "outer front closure": ["open front", "toggle closure", "velcro closure", "full zip up", "half zip up", "pullover", "double breasted", "hidden placket", "single breasted", "snap button"],
    "outer sleeve type": ["bell sleeves", "bishop sleeves", "dolman sleeves", "puff sleeves", "raglan sleeves", "split sleeves", "balloon sleeve", "cape sleeve", "drop shoulder", "sleeveless"],
    "outer cuff detail": ["one button cuff", "triple buttons cuff", "two buttons cuff", "drawstring-cuff", "elastic cuff", "shirred cuff", "french cuff", "frill-cuff", "pleated-cuff", "rolled cuff", "split-cuff", "strapped cuff", "tie-cuff", "velcro cuff", "zippered-cuff"],
    "sleeve length": ["extra long sleeves", "long sleeves", "three-quarter sleeves", "elbow-sleeve", "short sleeves", "cap sleeves", "sleeveless"],
    "outer silhouette": ["slim fit", "regular fit", "boxy fit", "oversize fit"],
    "outer length": ["cropped length", "waist length", "hip length", "mid thigh length", "knee-length", "calf length", "ankle-length"]
}

# =============================================================================
# Bottom (하의) 속성
# =============================================================================
BOTTOM_ATTRIBUTES = {
    "pants silhouette": ["skinny", "slim", "straight", "bootcut", "flare", "wide", "tapered", "baggy", "fitted", "straight-cut"],
    "shorts silhouette": ["flared", "baggy", "fitted", "straight-cut", "bermuda"],
    "skirts silhouette": ["a-line", "h-line", "pencil", "flared", "pleated", "tiered", "wrap", "mermaid", "bubble", "tulip", "handkerchief", "asymmetrical", "tutu"],
    "pants length": ["capri length", "cropped length", "ankle length", "top of shoe"],
    "shorts length": ["mini length", "mid thigh length", "knee length"],
    "leggings length": ["mid thigh length", "knee length", "cropped length", "ankle length"],
    "skirts length": ["micro mini length", "mini length", "above knee length", "knee length", "mid length", "tea length", "maxi length", "floor length"],
    "bottoms front detail": ["pocket", "flap pocket", "welt pocket", "patch pocket", "button", "zipper", "velcro", "belt", "buckle", "D-ring", "chain", "strap", "drawstring", "elastic", "metal stud", "piping", "quilting", "ruffle", "pleats", "pintuck", "shirred-smocked", "ruching", "embroidery", "applique", "patchwork", "fringe", "sequins", "beads", "tassel", "pom-pom", "raw hem", "stitching", "eyelet lace", "braid trim"],
    "bottoms back detail": ["yoke", "vent", "slit", "belt", "buckle", "D-ring", "strap", "drawstring", "elastic", "piping", "quilting", "pleats", "pintuck", "shirred-smocked", "ruching", "embroidery", "applique", "patchwork", "fringe", "sequins", "beads", "tassel", "raw hem", "stitching", "metal stud"],
    "bottoms side detail": ["slit", "zipper", "button", "velcro", "lace-up", "drawstring", "buckle", "D-ring", "strap", "chain", "elastic", "piping", "braid trim", "stitching", "embroidery", "applique", "patchwork", "studs", "fringe", "ruffle", "pleats", "pintuck", "shirred-smocked", "ruching", "sequins", "beads", "tassel", "eyelet lace", "ribbon", "raw hem", "pocket", "welt pocket", "zipper pocket", "flap pocket"],
    "bottoms fabric sheerness": ["opaque", "slightly-sheer", "partial-sheer", "ultra-sheer"],
    "bottoms closure": ["button-fly", "side-zip", "back-zip", "elastic-waist", "drawstring-waist", "wrap-tie", "zip-fly"],
    "waist line": ["low rise", "mid rise", "high rise"]
}

# =============================================================================
# Bag (가방) 속성
# =============================================================================
BAG_ATTRIBUTES = {
    "bags size": ["micro", "small", "medium", "large", "oversized"],
    "bags closure type": ["zip-top", "zip-around", "magnetic-flap", "buckle-flap", "turn-lock", "drawstring", "snap-button", "open-top", "toggle-closure"],
    "bags detail": ["ring", "d-ring", "buckle", "center bar buckle", "zipper", "chain", "bag charm", "metal stud", "bag feet", "clasp", "button", "lock", "wheel", "mesh pocket", "shirred-smocked", "patch", "quilting", "sequins", "label", "beads", "embroidery", "applique", "pintuck", "piping", "mini-pouch", "hook"],
    "bags exterior pocket": ["side-pocket", "front-pocket"],
    "bags handle and strap type": ["backpack strap", "top handle", "double handle", "single shoulder strap", "cross body", "wristlet"]
}

# =============================================================================
# Shoes (신발) 속성
# =============================================================================
SHOES_ATTRIBUTES = {
    "shoes closure type": ["boa dial", "lace-up", "quick lacing", "strap", "velcro", "zipper", "back open", "closed back"],
    "shoes detail": ["D-ring", "beads", "buckle", "center bar buckle", "chain", "eyelet", "label", "patch", "pearl", "pull tab", "rhinestone", "ring", "shoe decoration", "studs", "zipper puller", "raw hem"],
    "heel height": ["high heel", "low heel", "mid heel"],
    "heel type": ["block heel", "wedge heel"],
    "shaft height": ["high top", "knee high", "low top", "mid calf", "mid top", "thigh high"],
    "lacing hardware": ["lace lock", "shoelace stopper"],
    "lacing type": ["flat shoelaces", "round shoelaces", "shoelaces"],
    "outsole feature": ["grip sole", "chunky sole", "flat sole", "platform sole"],
    "strap placement": ["ankle strap"],
    "toe openness": ["open toe", "peep toe", "closed toe"],
    "toe shape": ["almond toe", "pointed toe", "round toe", "square toe", "tabi toe"],
    "shoes upper construction": ["cut-out", "embossed texture", "embroidery", "layered panel", "perforated", "plain upper", "quilting"],
    "vamp ornament": ["horsebit", "penny", "tassel"]
}

# =============================================================================
# Onepiece (원피스) 속성
# =============================================================================
ONEPIECE_ATTRIBUTES = {
    "onepiece upper neckline": ["turtle neck", "cowl neck", "mock neck", "crew neck", "round neck", "scoop neck", "v neck", "split neck", "square neck", "sweetheart neck", "asymmetrical neck", "boat neck", "halter neck", "hooley neck", "shirt collar", "scallop collar", "camp collar", "original collar", "v-shaped collar", "peter pan collar", "sailor collar", "wide collar", "off the shoulder", "one shoulder", "hood", "collarless"],
    "onepiece strap style": ["strapless", "asymmetric-strap", "spaghetti-strap", "adjustable-strap", "halter-strap", "multi-way-strap"],
    "onepiece sleeve type": ["dolman sleeves", "bell sleeves", "flutter sleeves", "bishop sleeves", "split sleeves", "puff sleeves", "soft sleeves", "balloon sleeves"],
    "onepiece cuff detail": ["one button cuff", "two buttons cuff", "triple buttons cuff", "dropped cuff", "drawstring-cuff", "shirred cuff", "bib cuff", "fill-cuff", "pleated-cuff", "rolled cuff", "velcro cuff", "elastic cuff", "split-cuff", "tie-cuff", "zippered-cuff"],
    "onepiece fabric sheerness": ["opaque", "slightly-sheer", "partial-sheer", "ultra-sheer"],
    "sleeve length": ["extra-long sleeves", "three-quarter sleeves", "short sleeves", "cap sleeves", "sleeveless", "long sleeves"],
    "onepiece front detail": ["wrap", "cut-out", "twist", "coat", "ruched", "lace", "collar", "drawstring", "belt", "buckle", "suspender", "chain", "strap", "elastic", "metal stud", "eyelet lace", "braid trim", "fringe", "patchwork", "pleats", "pintuck", "shirred-smocked", "sequins", "ruching", "tassel", "embroidery", "applique", "pom-pom", "stitching", "beads", "zipper", "button"],
    "onepiece front closure": ["half zip up", "full zip up", "tie in", "half-button", "lace-up-front", "wrap-closure", "velcro-closure", "invisible", "snap", "wrap", "full-button", "open-front"],
    "onepiece back detail": ["collar", "ruched", "lace", "keyhole", "braid trim", "elastic", "drawstring", "belt", "buckle", "suspender", "D-ring", "chain", "strap", "metal stud", "piping", "quilting", "pleats", "pintuck", "shirred-smocked", "ruching", "sequins", "beads", "pom-pom", "tassel", "raw hem", "stitching", "eyelet lace"],
    "onepiece back closure": ["back-zip", "wrap-tie-back", "lace-up-back"],
    "onepiece side detail": ["slit", "cut-out", "zipper", "velcro", "lace-up", "drawstring", "buckle", "D-ring", "strap", "chain", "elastic", "piping", "braid trim", "stitching", "embroidery", "applique", "patchwork", "studs", "pleats", "pintuck", "shirred-smocked", "ruching", "sequins", "beads", "tassel", "eyelet lace", "ribbon", "raw hem", "pocket", "welt pocket"],
    "onepiece lower type": ["shorts", "skorts", "pants"],
    "onepiece skirt silhouette": ["a-line", "flare", "pencil", "wrap", "tiered", "mermaid", "handkerchief", "asymmetrical"],
    "onepiece skirt length": ["micro mini length", "mini length", "above knee length", "knee length", "midi length", "tea length", "maxi length", "floor length"],
    "onepiece shorts silhouette": ["fitted", "baggy", "flared", "straight-cut"],
    "onepiece shorts length": ["micro mini length", "mini length", "mid thigh length", "knee length"],
    "onepiece pants silhouette": ["skinny", "slim", "straight", "bootcut", "flare", "wide", "tapered"],
    "onepiece pants length": ["cropped length", "ankle length", "top of shoe"],
    "onepiece lower closure": ["button-fly", "side-zip", "drawstring", "elastic-waist"],
    "onepiece waist type": ["empire", "natural", "high-waisted", "drop-waist"],
    "onepiece silhouette": ["slim fit", "regular fit", "oversize fit"]
}

# =============================================================================
# Hosiery (양말/스타킹) 속성
# =============================================================================
HOSIERY_ATTRIBUTES = {
    "hosiery cuff": ["frill-cuff", "ribbed cuff", "lace-up"],
    "hosiery sheerness": ["opaque", "partial-sheer", "slightly-sheer", "ultra-sheer"],
    "hosiery height": ["ankle", "crew", "knee-high", "no-show", "over-the-knee", "thigh-high", "pantyhose"],
    "socks toe coverage": ["full-toe", "open-toe", "toe-separation"]
}

# =============================================================================
# Swimwear Onepiece 속성
# =============================================================================
SWIMWEAR_ONEPIECE_ATTRIBUTES = {
    "swimwear onepiece upper neckline": ["v neck", "scoop neck", "split neck", "boat neck", "shirt collar", "square neck", "sweetheart neck", "asymmetrical neck", "halter neck"],
    "swimwear onepiece sleeve length": ["sleeveless", "short sleeves", "long sleeves"],
    "swimwear onepiece detail": ["slit", "eyelet lace", "embroidery", "drawstring", "fringe", "ruffle", "keyhole", "twisted", "ruching", "shirred-smocked", "piping"],
    "swimwear onepiece front closure": ["open-front", "full-button", "half-button"],
    "swimwear onepiece fabric sheerness": ["slightly-sheer", "opaque"],
    "swimwear onepiece skirt length": ["mini length", "midi length", "maxi length"],
    "swimwear onepiece strap style": ["strapless", "spaghetti-strap", "halter-strap", "cross-back strap", "adjustable-strap", "cut-out", "lace-up"],
    "swimwear onepiece back closure": ["open-back", "lace-up-back", "sleeveless"]
}

# =============================================================================
# Swimwear Inner 속성
# =============================================================================
SWIMWEAR_INNER_ATTRIBUTES = {
    "swimwear inner neckline": ["crew neck", "mock neck", "scoop neck", "v neck", "square neck", "sweetheart neck", "halter neck"],
    "swimwear inner sleeve length": ["long sleeves", "short sleeves"],
    "swimwear inner front closure": ["half zip up", "full zip up"],
    "swimwear inner detail": ["piping", "stitching", "ruching", "shirred-smocked", "ruffle", "twisted", "keyhole", "cut-out"],
    "swimwear inner strap style": ["spaghetti-strap", "adjustable-strap", "halter-strap", "cross-back strap", "strapless"],
    "swimwear inner back closure": ["lace-up-back"]
}

# =============================================================================
# Swimwear Bottoms 속성
# =============================================================================
SWIMWEAR_BOTTOMS_ATTRIBUTES = {
    "swimwear bottom pants silhouette": ["slim", "straight", "tapered"],
    "swimwear bottom pants length": ["cropped length", "ankle length"],
    "swimwear bottom shorts silhouette": ["fitted", "straight-cut", "baggy", "bermuda"],
    "swimwear bottom shorts length": ["mid thigh length", "knee length"],
    "swimwear bottom skirts silhouette": ["a-line", "flared", "wrap"],
    "swimwear bottom skirts length": ["mini length", "above knee length"],
    "swimwear bottoms closure": ["elastic-waist", "drawstring-waist", "wrap-tie"],
    "swimwear bottoms waist line": ["low rise", "mid rise", "high rise"],
    "swimwear bottoms detail": ["pocket", "zipper pocket", "piping", "twisted", "ruching", "lace-up", "shirred-smocked", "ruffle"]
}

# =============================================================================
# Headwear 속성
# =============================================================================
HEADWEAR_ATTRIBUTES = {
    "headwear type": ["cap", "beanie", "bucket hat", "fedora", "beret", "visor", "headband", "bandana", "turban", "sun hat", "baseball cap", "snapback", "trucker hat", "newsboy cap"]
}

# =============================================================================
# Eyewear 속성
# =============================================================================
EYEWEAR_ATTRIBUTES = {
    "eyewear type": ["sunglasses", "glasses", "goggles", "reading glasses"],
    "frame shape": ["round", "square", "aviator", "cat-eye", "rectangular", "oval", "oversized"]
}

# =============================================================================
# Neckwear 속성
# =============================================================================
NECKWEAR_ATTRIBUTES = {
    "neckwear type": ["scarf", "necktie", "bow tie", "choker", "bandana", "neckerchief"]
}

# =============================================================================
# 마케팅 속성 - Background
# =============================================================================
BACKGROUND_ATTRIBUTES = {
    "location": ["street", "café", "shopping/store", "park/nature/forest", "beach", "gym", "festival-like", "party", "festival", "city", "campus", "car", "stadium", "flight", "outdoor-exercise", "travel", "pool", "home", "studio"],
    "mood": ["relaxed", "active", "chic", "luxurious", "hip", "lovely", "festive", "rebellious", "romantic"],
    "season/weather": ["sunny day", "rainy day", "spring", "summer", "autumn", "winter", "snowy day"],
    "shooting composition": ["close-up", "mid shot", "full body", "wide angle"],
    "color tone/filter": ["reddish", "yellowish", "blueish", "neutral", "contrast", "monochrome"]
}

# =============================================================================
# 마케팅 속성 - Styling
# =============================================================================
STYLING_ATTRIBUTES = {
    "fashion style": ["casual", "street", "business", "formal", "sporty", "luxury", "feminine", "gorpcore", "workwear", "y2k", "old money look", "preppy", "bodycon"],
    "coordination method": ["layered", "tone-on-tone", "set-up", "mix & match", "low-rise", "oversized"],
    "overall fashion color tone": ["neutral tone", "pastel tone", "vivid", "tone-on-tone", "monotone"]
}

# =============================================================================
# 마케팅 속성 - Model
# =============================================================================
MODEL_ATTRIBUTES = {
    "gender": ["male", "female"],
    "skin tone": ["cool", "warm", "neutral"],
    "age group": ["child", "teenager", "youth", "adult", "middle-aged", "elderly"],
    "hair style": ["short hair", "wave", "straight hair", "braided", "ponytail", "pigtails", "bangs", "crew cut", "dyed hair", "layered cut", "high bun", "low bun"],
    "expression": ["smile", "expressionless", "surprised", "cool", "wink"],
    "gaze direction": ["front", "side", "upward", "downward", "avoiding gaze"],
    "pose": ["full body shot", "sitting", "walking", "looking back", "aerial shot", "exercise (running/tennis etc)", "low angle shot"],
    "number of people": ["single", "group", "couple", "family"]
}

# =============================================================================
# 카테고리별 속성 매핑
# =============================================================================
CATEGORY_ATTRIBUTES_MAP = {
    "Inner": INNER_ATTRIBUTES,
    "Outer": OUTER_ATTRIBUTES,
    "Bottom": BOTTOM_ATTRIBUTES,
    "Bag": BAG_ATTRIBUTES,
    "Shoes": SHOES_ATTRIBUTES,
    "Onepiece": ONEPIECE_ATTRIBUTES,
    "Hosiery": HOSIERY_ATTRIBUTES,
    "Swimwear": {**SWIMWEAR_ONEPIECE_ATTRIBUTES, **SWIMWEAR_INNER_ATTRIBUTES, **SWIMWEAR_BOTTOMS_ATTRIBUTES},
    "Headwear": HEADWEAR_ATTRIBUTES,
    "eyewear": EYEWEAR_ATTRIBUTES,
    "neckwear": NECKWEAR_ATTRIBUTES
}

