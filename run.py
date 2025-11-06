import sys
import os

# Ensure project root is on Python path so 'ecopulse' package can be imported
sys.path.append(os.path.dirname(__file__))

from ecopulse.app.main import app

# This makes the app available for uvicorn
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("run:app", host="0.0.0.0", port=8000, reload=True)