# TO ACCESS:
# brew services start postgresql
# psql nba_tracking
# brew services start redis
# uvicorn api.app.main:app --reload
# http://127.0.0.1:8000/docs#/

from sqlalchemy import create_engine

DB_URL = "postgresql://localhost/nba_tracking"
engine = create_engine(DB_URL)