import os

# Timezone for stamping output files
TZ_NAME = "Asia/Taipei"

# Default unit conversion (approx): 1 ton ≈ 7.33 bbl
BBL_PER_TON = 7.33

# Output directories
OUTPUT_DIR = os.getenv("OUTPUT_DIR", "logs")
DATA_DIR = os.getenv("DATA_DIR", "data")

# Sources
OIL_PRIMARY_SOURCE = "Reuters"
OIL_FALLBACK_SOURCE = "Yahoo Finance"
