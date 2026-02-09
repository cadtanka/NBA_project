# TO ACCESS:
# brew services start postgresql
# psql nba_tracking

from sqlalchemy import create_engine

DB_URL = "postgresql://localhost/nba_tracking"
engine = create_engine(DB_URL)