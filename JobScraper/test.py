import requests

with open(r"C:\Users\fabia\Downloads\Capstone Project\Extractor\extracted_skills.txt", "rb") as f:
    response = requests.post(
        "http://127.0.0.1:8080/scrape-jobs",
        files={"skills_file": f},
        params={
            "location": "Remote",
            "results_wanted": 5,
            "hours_old": 72
        }
    )
#print(response.json())
print(response.status_code)
print(response.text)
