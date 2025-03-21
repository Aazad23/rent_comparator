import fitz  # PyMuPDF for PDF parsing
import re
from openai import OpenAI
import json
from config import API_KEY, BASE_URL,MODEL
import pandas as pd


print(BASE_URL,'\n',API_KEY)
def extract_text_from_pdf(pdf_path):
    text = ""
    with fitz.open(pdf_path) as doc:
        for page in doc:
            text += page.get_text()
    return text

def extract_key_terms(text):
    client = OpenAI(api_key=API_KEY,base_url=BASE_URL)
    prompt = f'''extract folling details in json format with keys 
        "Property Address",
        "Rental Amount"
        "Security Deposit"
        "Lease Duration" (in months) 
        "Notice Period" (in months)
        "Utilities Responsibility" (single string format)
        "monthly payment deadline"
        "Late Payment Clause"
        "Termination Clause" from {text}'''.format(text)
    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "system", "content": '''You are an assistant expert in extracting information from renteal agreement text''' },
                  {"role": "user", "content": prompt}],
        temperature=0.2
    )
    return response.choices[0].message.content.strip()


def get_json(text):
    text = text.replace("\n", "")
    json_pattern = r"```json({.*?})"
    match = re.search(json_pattern, text, re.DOTALL)
    if not match:
        print(f"No JSON pattern match found in text: {text[:100]}...")
        return
    json_str = match.group(1)
    json_dict = json.loads(json_str)
    return json_dict


def compare_rental_terms(term1, term2):
    prompt = f"""
    Compare the following two rental agreement terms and highlight the key differences:

    Agreement 1:
    {term1}

    Agreement 2:
    {term2}

    Provide a concise comparison highlighting differences in:
    - 'Property Address',
    - 'Rental Amount',
    - 'Security Deposit', 
    - 'Lease Duration'
    - 'Notice Period',
    - 'Utilities Responsibility'
    - 'Monthly Payment Deadline'
    - 'Late Payment Clause'
    - 'Termination Clause'
    
    Format the comparison in JSON clearly with headings for each term and 
    with values as "comment;inference" separated by a semicolon.
    Comment should only return "matched" or "mismatched".
    The inference should explain the implications of this mismatch explaaining
    the potential legal, financial, or practical consequences.
    and return "null" in case of matched terms.
    Sample schema >> {{"heading": "comment;inference"}}

    Example output format:
    {{
        "Security Deposit": "Mismatched;Agreement 1 requires a significantly larger security deposit which may indicate stricter tenant selection criteria or potential risks associated with the property/tenant relationship that need to be covered financially",
        "Termination Clause": "matched;null"
    }}"""
    client = OpenAI(api_key=API_KEY,base_url=BASE_URL)
    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "system", "content": "You are a helpful assistant in comparing legal terms"},
                  {"role": "user", "content": prompt}],
        max_tokens=1000,
        temperature=0.2
    )

    return response.choices[0].message.content.strip()

def detect_critical_terms(text):
    client = OpenAI(api_key=API_KEY,base_url=BASE_URL)
    prompt = f"""
    Analyze the following rental agreement text and identify critical terms related to property damage, maintenance, subletting, etc. 
    Flag any terms that are significant but not predefined, assess their importance, and provide an inference.

    Rental Agreement Text:
    {text}

    Example Output Format:
    List[{{"flagged term":
    "details":,
    "inference":}}]
    """      
    response = client.chat.completions.create(
        model="Mistral-Nemo-Krutrim",
        messages=[{"role": "system", "content": "You are a legal assistant specializing in identifying critical clauses in rental agreements."},
                  {"role": "user", "content": prompt}],
        temperature=0.15,
        max_tokens=1000
    )
    return response.choices[0].message.content.strip()


def compare_rental_documents(path1,path2):
    agreement_text_1 = extract_text_from_pdf(path1)
    agreement_text_2 = extract_text_from_pdf(path2)

    term1 = extract_key_terms(agreement_text_1)
    term2 = extract_key_terms(agreement_text_2)
    comparision = compare_rental_terms(term1,term2)

    t1_df = pd.DataFrame([get_json(term1)]).T
    t2_df = pd.DataFrame([get_json(term2)]).T
    comp_df = pd.DataFrame([get_json(comparision)]).T

    result_df = pd.concat([t1_df, t2_df, comp_df], axis=1)
    result_df.columns = ['document_1', 'document_2', 'comparision']

    infer = result_df.comparision.str.split(";",expand=True)
    infer.columns = ['comment','inferenece']
    infer['inferenece'] = infer.inferenece.str.replace("Inferences:","")

    results  = pd.concat([result_df,infer],axis=1).drop(columns=['comparision']).T
    results.fillna("",inplace=True)
    results.replace("null","",inplace=True)
    results_dict = results.to_dict()
    print('Finished')
    return results_dict



