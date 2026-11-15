from sqlalchemy import text
from app.database import SessionLocal

db = SessionLocal()

result = db.execute(text('SELECT 1'))
value = result.scalar()
print({"database": value})
db.close()
