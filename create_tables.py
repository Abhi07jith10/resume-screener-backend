from database import Base, engine
from models import models

Base.metadata.create_all(bind=engine)

print("Tables created successfully!")