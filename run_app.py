import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "app")))
from dotenv import load_dotenv

load_dotenv()

# Debug: Print the Python path
print("Python Path:", sys.path)

import uvicorn

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
