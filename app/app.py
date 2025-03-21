from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import tempfile
import os
from model import compare_rental_documents

app = FastAPI(
    title="Rental Agreement Comparison API",
    description="API for comparing rental agreement PDFs"
)

@app.post("/rent_agreement_comparator")
async def compare_documents(file1: UploadFile = File(...), file2: UploadFile = File(...)):
    """
    Compare two rental agreement PDFs and return comparison json
    """
    try:
        # Create temporary files to store uploads
        with tempfile.NamedTemporaryFile(delete=False) as tmp1, \
                tempfile.NamedTemporaryFile(delete=False) as tmp2:
            
            # Save uploaded files
            tmp1.write(await file1.read())
            tmp2.write(await file2.read())
            
            # Get file paths
            path1 = tmp1.name
            path2 = tmp2.name

        # Compare documents
        response = compare_rental_documents(path1, path2)

        return JSONResponse(status_code=200, content=response)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

    finally:
        # Clean up temp files safely
        for path in [path1, path2]:
            if os.path.exists(path):
                os.unlink(path)
