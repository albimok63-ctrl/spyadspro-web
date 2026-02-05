"""
Avvio uvicorn con access_log=False per evitare log duplicati.
Log richieste gestiti dal middleware (JSON strutturato su stdout).
Compatibile Docker: stdout/stderr invariati.
"""

import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        access_log=False,
    )
