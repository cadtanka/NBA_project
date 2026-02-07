# TO ACCESS:
# brew services start postgresql
# psql nba_tracking

from sqlalchemy import create_engine
from data.schema import create_tables

DB_URL = "postgresql://localhost/nba_tracking"
engine = create_engine(DB_URL)
create_tables()