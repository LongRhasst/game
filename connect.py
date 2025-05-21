from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import importlib.util
import sys

# Check if cryptography package is installed
cryptography_installed = importlib.util.find_spec("cryptography") is not None

# Database connection URL
DATABASE_URL = 'mysql+pymysql://root:123465@localhost:3306/game'

# Configure connection based on available packages
try:
    if cryptography_installed:
        # Use SSL connection with cryptography
        engine = create_engine(
            DATABASE_URL,
            connect_args={"ssl": {"ssl_verify_identity": False}}
        )
    else:
        # Try connecting without SSL (may fail with newer MySQL versions)
        print("Warning: 'cryptography' package not installed. Authentication might fail.")
        print("Run: pip install cryptography")
        engine = create_engine(DATABASE_URL)
    
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base = declarative_base()
    
    # Test connection
    with engine.connect() as conn:
        pass
        
except Exception as e:
    # If connection fails, create a fallback storage method
    print(f"Database connection error: {e}")
    print("Using local file storage as fallback for scores")
    
    # Define fallback session and base that won't use a real database
    class FallbackSessionLocal:
        def __init__(self):
            self.scores = []
        
        def query(self, model):
            class QueryObj:
                def __init__(self, scores):
                    self.scores = scores
                
                def order_by(self, _):
                    return self
                
                def limit(self, _):
                    return self.scores
            
            return QueryObj(self.scores)
        
        def add(self, score):
            self.scores.append(score)
        
        def commit(self):
            # Save to a local file
            with open("local_scores.txt", "a") as f:
                f.write(f"{score.name},{score.high_score}\n")
        
        def close(self):
            pass
    
    SessionLocal = FallbackSessionLocal
    Base = type('Base', (), {})