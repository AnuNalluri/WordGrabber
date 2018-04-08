export DATA_DIR=$VIRTUAL_ENV"/../data/"
export URL_LIST=$VIRTUAL_ENV"/../urls"
export VISITED_URLS=$VIRTUAL_ENV"/../visited.db"
export NEO_DB_IMPORT=$VIRTUAL_ENV"/var/lib/neo4j/import/"
export NEO_DB_URL="bolt://localhost"
export NEO_DB_USER="neo4j"
export NEO_DB_PASS="fnab"
export NEO_DATA="edges"

pip install -r $VIRTUAL_ENV"/../requirements.txt"

