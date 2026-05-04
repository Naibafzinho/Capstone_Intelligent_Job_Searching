# Full Project Code File Manifest

This file lists the code-related files for the four main modules:
- `DB`
- `Extractor`
- `JobScraper`
- `WebServer`

Each entry includes the file path relative to the project root.

---

## DB Module

- `DB/check_services.py`
- `DB/cleanup_database.py`
- `DB/DB_Management.py`
- `DB/DeletePoisonQueueEntries.py`
- `DB/HowToRun.txt`
- `DB/PoisonQueueInspection.py`
- `DB/main.py`
- `DB/pydanticSchemes.py`
- `DB/queue_manager.py`
- `DB/requirements.txt`
- `DB/worker.py`
- `DB/test.py`

---

## Extractor Module

- `Extractor/database.py`
- `Extractor/main.py`
- `Extractor/extractor.py`
- `Extractor/Skills.csv`
- `Extractor/extracted_skills.txt`
- `Extractor/job_description.txt`
- `Extractor/resumes/my_resume.pdf`

---

## JobScraper Module

- `JobScraper/main.py`
- `JobScraper/services.py`
- `JobScraper/test.py`
- `JobScraper/requirements.txt`

---

## WebServer Module

### Root files

- `WebServer/JobRush.sln`
- `WebServer/JobRush.csproj`
- `WebServer/Program.cs`
- `WebServer/JobRush.csproj`
- `WebServer/JobListing.cs`
- `WebServer/ResumeDisplayer.cs`
- `WebServer/Resume.cs`
- `WebServer/ResumeHandler.cs`
- `WebServer/SessionManager.cs`
- `WebServer/appsettings.json`
- `WebServer/appsettings.Development.json`
- `WebServer/ProjectOrganization.txt`
- `WebServer/Remaining-Integration-Tasks.txt`

### Component files

- `WebServer/Components/_Imports.razor`
- `WebServer/Components/App.razor`
- `WebServer/Components/Routes.razor`

#### Layout

- `WebServer/Components/Layout/MainLayout.razor`
- `WebServer/Components/Layout/MainLayout.razor.css`
- `WebServer/Components/Layout/ReconnectModal.razor`
- `WebServer/Components/Layout/ReconnectModal.razor.css`
- `WebServer/Components/Layout/ReconnectModal.razor.js`

#### Pages

- `WebServer/Components/Pages/Home.razor`
- `WebServer/Components/Pages/Login.razor`
- `WebServer/Components/Pages/Login.razor.css`
- `WebServer/Components/Pages/Signup.razor`
- `WebServer/Components/Pages/Signup.razor.css`
- `WebServer/Components/Pages/Upload.razor`
- `WebServer/Components/Pages/Upload.razor.css`
- `WebServer/Components/Pages/Matches.razor`
- `WebServer/Components/Pages/Matches.razor.css`
- `WebServer/Components/Pages/Resumes.razor`
- `WebServer/Components/Pages/Resumes.razor.css`
- `WebServer/Components/Pages/Edit.razor`
- `WebServer/Components/Pages/Edit.razor.css`
- `WebServer/Components/Pages/Analysis.razor`
- `WebServer/Components/Pages/Weather.razor`
- `WebServer/Components/Pages/Error.razor`
- `WebServer/Components/Pages/NotFound.razor`

#### Subcomponents

- `WebServer/Components/Subcomponents/Navbar.razor`
- `WebServer/Components/Subcomponents/Navbar.razor.css`
- `WebServer/Components/Subcomponents/JobCard.razor`
- `WebServer/Components/Subcomponents/JobCard.razor.css`
- `WebServer/Components/Subcomponents/ProgressBarCircle.razor`
- `WebServer/Components/Subcomponents/ResumeBox.razor`
- `WebServer/Components/Subcomponents/ResumeBox.razor.css`
- `WebServer/Components/Subcomponents/Redirect.cs`

### Properties

- `WebServer/Properties/launchSettings.json`

### Static assets and styles

- `WebServer/wwwroot/app.css`
- `WebServer/wwwroot/favicon.png`
- `WebServer/wwwroot/resumelogo.png`

### Third-party library files

The project also contains Bootstrap library files under:
- `WebServer/wwwroot/lib/bootstrap/dist/...`

---

## Notes

- This manifest includes all primary source and configuration files for the four main modules.
- Third-party vendor files are noted under `wwwroot/lib/bootstrap` but are not individually enumerated here.
- If you need a separate file that includes only source code files and excludes assets, I can generate that too.
