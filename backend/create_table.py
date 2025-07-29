from db.session import engine
from models import model  # Import all your models

model.Base.metadata.create_all(bind=engine)
