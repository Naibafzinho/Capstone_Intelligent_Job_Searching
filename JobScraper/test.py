import requests

files = {
    "skills_file": open("skills.txt", "rb")
}

res = requests.post("http://127.0.0.1:8002/scrape-jobs", files=files)

print("Status:", res.status_code)
print(res.json())