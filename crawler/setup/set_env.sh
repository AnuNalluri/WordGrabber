export DATA_DIR=$VIRTUAL_ENV"/../data/"
export URL_LIST=$VIRTUAL_ENV"/../urls"
export VISITED_URLS=$VIRTUAL_ENV"/../visited.db"
export NEO_DB_IMPORT=$VIRTUAL_ENV"/../database/import/"
export NEO_DB_URL="bolt://localhost"
export NEO_DB_USER="kunal"
export NEO_DB_PASS="fnab"
export NEO_DATA="edges.csv"

pip install -r $VIRTUAL_ENV"/../requirements.txt"

