from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
import pymongo
from fastapi.templating import Jinja2Templates as templates
import os
import googleapiclient.discovery
from auth import spreadsheet_service
from bson.objectid import ObjectId
import uvicorn

app = FastAPI()

# MongoDB connection
client = pymongo.MongoClient("mongodb+srv://theeye146:AobQERqGoW94KP9K@cluster0.dpdhe.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = client["feedback_db"]
collection = db["feedback"]

# Google Sheets API credentials
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SHEET_ID = '1qvP2m5i2C70i9qUNWQaR2MG1-uNfuZgBzzKjhrravO0'
RANGE_NAME = 'Sheet1'

templates = templates(directory="templates")

# Fetch form structure from Google Sheets
# Fetch form structure based on roll_no and attendance status
def getForm(roll_no: str):
    # Get the attendance data for the roll number
    roll_data = get_roll_number_data(roll_no)
    
    if not roll_data:
        return None

    # Fetch all form questions
    result = spreadsheet_service.spreadsheets().values().get(spreadsheetId=SHEET_ID, range="FeedbackFormQuestions").execute()
    rows = result.get('values', [])
    headers = rows[0]  # Assume first row is the header: ['type', 'prompt', 'desc', 'day1', 'day2', 'day3', 'overall']

    form_structure = []

    for row in rows[1:]:
        question = dict(zip(headers, row))
        
        # Add "overall" questions (always included)
        if question['overall'].upper() == 'TRUE':
            form_structure.append(question)
        
        # Conditionally add "day1" questions if ATTENDANCE is TRUE
        if roll_data['ATTENDANCE'].upper() == 'TRUE' and question['day1'].upper() == 'TRUE':
            form_structure.append(question)
        
        # Conditionally add "day2" questions if ATTENDANCE Day 2 is TRUE
        if roll_data['ATTENDANCE Day 2'].upper() == 'TRUE' and question['day2'].upper() == 'TRUE':
            form_structure.append(question)
        
        # Conditionally add "day3" questions if Winner or Honorable Mention is TRUE
        if (roll_data['Winner'].upper() == 'TRUE' or roll_data['Honorable Mention'].upper() == 'TRUE') and question['day3'].upper() == 'TRUE':
            form_structure.append(question)
    
    return form_structure


# Function to check roll number in Google Sheet
def get_roll_number_data(roll_number: str):
    result = spreadsheet_service.spreadsheets().values().get(spreadsheetId=SHEET_ID, range=RANGE_NAME).execute()
    rows = result.get('values', [])
    if not rows:
        return None

    jsonData = [dict(zip(rows[0], row)) for row in rows[1:]]
    for row in jsonData:
        if row.get("Roll Number:", "").upper() == roll_number.upper():
            return row
    return None

@app.get("/feedback", response_class=HTMLResponse)
async def feedback_form(name: str, phone: str, roll_number: str):
    # Check if roll number exists in Google Sheets
    roll_data = get_roll_number_data(roll_number)
    if not roll_data:
        raise HTTPException(status_code=404, detail="Roll number not found")

    # Redirect to the form
    return RedirectResponse(url=f"/form?name={name}&phone={phone}&roll_number={roll_number}")

@app.get("/form", response_class=HTMLResponse)
async def form_page(request: Request, name: str, phone: str, roll_number: str):
    # Fetch the form structure based on roll_number
    form_structure = getForm(roll_number)

    # Render the form with hidden inputs for name, phone, roll_number
    response = templates.TemplateResponse('form.html', {
        "request": request,
        "form_structure": form_structure,
        "name": name,
        "phone": phone,
        "roll_number": roll_number
    })

    return response

# Submit feedback route
@app.post("/submit_feedback")
async def submit_feedback(
    request: Request,
    name: str = Form(...),             # User's name
    phone: str = Form(...),            # User's phone number
    roll_number: str = Form(...)       # User's roll number
):
    # Extract form data from the request
    form_data = await request.form()

    # Extract feedback fields that start with 'feed-'
    feedback = {key: value for key, value in form_data.items() if key.startswith('feed-')}

    # Create the feedback document to store in MongoDB
    feedback_data = {
        "name": name,
        "phone": phone,
        "roll_number": roll_number,
        "feedback": feedback  # Store the extracted key-value pairs
    }

    # Insert feedback into the MongoDB collection
    collection.insert_one(feedback_data)

    # Fetch roll number data from Google Sheets for certificate links
    roll_data = get_roll_number_data(roll_number)
    if not roll_data:
        raise HTTPException(status_code=404, detail="Roll number not found")

    # Create certificate links based on attendance and other columns
    certificate_links = {}

    # Check attendance for Day 1 and Day 2, and create corresponding links
    if roll_data.get("ATTENDANCE") == "TRUE":
        certificate_links[f"https://qr.cseatheeye.com/etherx/participations/devsecops/{roll_number}"] = "DevSecOps Workshop Certificate"

    if roll_data.get("ATTENDANCE Day 2") == "TRUE":
        certificate_links[f"https://qr.cseatheeye.com/etherx/participations/ctf-osint/{roll_number}"] = "CTF and OSINT Workshop Certificate"

    # Check if the user won or received an honorable mention
    if roll_data.get("Winner") == "TRUE":
        certificate_links[f"https://qr.cseatheeye.com/etherx/participations/winners/{roll_number}"] = "Winner Certificate"

    if roll_data.get("Honorable Mention") == "TRUE":
        certificate_links[f"https://qr.cseatheeye.com/etherx/participations/honors/{roll_number}"] = "Honorable Mention Certificate"

    # Add a general event link if any attendance is true
    if roll_data.get("ATTENDANCE") == "TRUE" or roll_data.get("ATTENDANCE Day 2") == "TRUE":
        certificate_links[f"https://qr.cseatheeye.com/etherx/participations/event/{roll_number}"] = "Participation Certificate"

    # Render a styled page with links to the certificates
    links_html = "<br>".join([f'<br/><br/><a style="text-decoration:none" href="{link}" class="link">{name}</a>' for link, name in certificate_links.items()])
    styled_html = """
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>EtherX Certificate(s) | The Eye</title>
        <link rel="stylesheet" href="https://intellx.in/static/fonts/stylesheet.css" />
        <link rel="icon" href="https://www.cseatheeye.com/assets/LOGO-74e75b51.jpg" />
        <style>
            * {
                font-family: 'Aeonik' !important
            }

            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }

            a {
                width: 100%;
                padding: 15px;
                border-radius: 6px;
                border: none;
                background-color: var(--button-background, #000);
                color: var(--button-text, #fff);
                font-size: 1em;
                cursor: pointer;
                transition: background-color 0.3s ease, transform 0.3s ease;
            }

            a:hover {
                background-color: var(--button-hover-background, #333);
                transform: translateY(-3px);
            }

            body {
                font-family: 'Arial', sans-serif;
                background-color: var(--background-color, #ffffff);
                color: var(--text-color, #000);
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                transition: background-color 0.3s, color 0.3s;
                overflow: hidden; /* Prevent overflow on smaller screens */
            }

            .response-container {
                width: 100%;
                max-width: 800px;
                padding: 40px;
                text-align: center;
                background-color: var(--container-background, #fff);
                border-radius: 12px;
                box-shadow: 0 15px 30px rgba(0, 0, 0, 0.1);
                overflow: auto;
                max-height: 80vh;
            }

            h2 {
                margin-bottom: 20px;
                color: var(--button-background, #000);
            }
        </style>
    </head>
    <body>
        <div class="response-container">
            <h2>Feedback submitted!</h2>
            """+links_html+"""
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=styled_html)


@app.get("/responses", response_class=HTMLResponse)
async def view_responses(request: Request):
    # Fetch all responses from the MongoDB collection
    responses = list(collection.find())
    
    # Render responses in an HTML template
    return templates.TemplateResponse("responses.html", {"request": request, "responses": responses})

@app.get("/export_responses")
async def export_responses():
    # Fetch all responses from the MongoDB collection
    responses = list(collection.find())
    
    # Prepare CSV content
    if not responses:
        return Response(content="No data found", media_type="text/plain")

    # Convert MongoDB documents to CSV format
    headers = responses[0].keys()  # Get the headers from the first response
    csv_data = [",".join(headers)]  # Initialize CSV data with headers

    for response in responses:
        # Exclude the ObjectId if present
        response.pop("_id", None)
        # Join values by comma
        csv_data.append(",".join(str(value) for value in response.values()))

    # Create CSV content as a string
    csv_content = "\n".join(csv_data)

    # Return the CSV file as a response
    return Response(content=csv_content, media_type="text/csv", headers={"Content-Disposition": "attachment; filename=responses.csv"})


if __name__ == '__main__':
    uvicorn.run(app)