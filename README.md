# Rental Agreement Comparison API

This FastAPI-based application allows you to compare two rental agreement PDF documents and provides a structured JSON output highlighting the key differences.

## Features
- Accepts two rental agreement PDFs as input.
- Compares key terms like rental amount, security deposit, utilities responsibility, etc.
- Returns a structured JSON response with comments and inferences for each comparison.

---

## Installation

### Prerequisites
Ensure you have the following installed:
- **Python 3.9+**
- **Docker** (Recommended for deployment)
- **pip**

### Step 1: Clone the Repository
### Step 2: Update requirements and API key, model and bases url in properties.env file based on access
### Step 3: Run docker to host application
```
docker run -p 9090:9090 rental-comparator 
```

---

## Running the Application

### Option 1: Run with Docker (Recommended)

**Step 1:** Build the Docker image
```bash
docker build -t rental_comparator .
```

**Step 2:** Run the Container
```bash
docker run --env-file ./config/properties.env -p 9090:9090 rental_comparator
```

### Option 2: Run Locally
```bash
uvicorn app:app --host 0.0.0.0 --port 9090
```

---

## API Endpoints

### **POST** `/rent_agreement_comparator`
**Description:** Compares two rental agreement PDFs and returns differences in JSON format.

**Request:**
- **file1** (PDF) - First rental agreement file
- **file2** (PDF) - Second rental agreement file

**Example Request Using `curl`**
```bash
curl -X POST "http://localhost:9090/rent_agreement_comparator" \
     -F "file1=@/path/to/agreement1.pdf" \
     -F "file2=@/path/to/agreement2.pdf"
```


---

## File Structure
```
/
├── app/
│   ├── app.py          # FastAPI application code
│   ├── model.py        # Document comparison logic
│   └── config.py        # Utility functions
│
├── config/
│   └── properties.env      # Environment variables file
├── test/
│   └── test.py      # sample unittest file
│
├── requirements.txt    # Python dependencies
├── Dockerfile          # Docker build instructions
├── README.md           # Project documentation
```

---

## Error Handling
- **500 Internal Server Error** - Returned when there’s an issue in processing documents or comparing content.
- **422 Unprocessable Entity** - Returned when the uploaded files are not PDFs.

---

## Future Improvements
- Enhance NLP logic for better context extraction from rental agreements.
- Add support for comparing agreements in different languages.
- Integrate a UI for easier document upload and result visualization.

---

## Contributing
If you'd like to contribute, please fork the repository and create a pull request. For major changes, please open an issue to discuss what you would like to improve.

---

## License
This project is licensed under the [MIT License](LICENSE).

