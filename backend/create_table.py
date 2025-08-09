from infrastructure.db.session import engine
from infrastructure.models import model  # Import all your models

model.Base.metadata.create_all(bind=engine)
