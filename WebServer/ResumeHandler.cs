using System.Text.Json;

namespace JobRush;
/// <summary>
/// Handles resume uploads and edits. This class is unique for each client connection.
/// </summary>
internal class ResumeHandler(SessionManager sessionManager, ResumeDisplayer resumeDisplayer) {
	// Injected Dependencies
	private readonly HttpClient httpClient = new();
	private readonly SessionManager sessionManager = sessionManager;
	private readonly ResumeDisplayer resumeDisplayer = resumeDisplayer;

	/// <summary>
	/// Uploads a resume to the database and notifies the preprocessor node.
	/// </summary>
	/// <param name="resume">The resume to upload.</param>
	/// <returns>True if successful.</returns>
	public bool UploadResume(Resume resume) {
		if (!sessionManager.IsAuthenticated()) return false; // Fail if a resume is somehow uploaded before authentication.

		try {
			// Attempt to store resume in DB.
			HttpResponseMessage response = httpClient.PostAsJsonAsync("http://127.0.0.1:8000/insertEntry", new {
				collection_name = "Resumes",
				entry = new {
					filename = resume.Filename,
					userId = resume.UserID,
					data = resume.FileBytes64,
					uploadDate = resume.UploadDate,
					isActive = true,
					locationConfig = resume.Config.Locations,
					expectedSalaryConfig = resume.Config.ExpectedSalaryRanges,
					jobTypeConfig = resume.Config.EmploymentType,
					industryConfig = resume.Config.IndustryPreferences,
					experienceLevelConfig = resume.Config.ExperienceLevels,
					remoteConfig = resume.Config.RemoteStatus,
					companySizeConfig = resume.Config.CompanySizes,
					tags = resume.Config.Tags
				}
			}).Result;

			// If request failed at HTTP level, return false.
			if (!response.IsSuccessStatusCode) return false;

			// Get the DB ID of the resume that was just uploaded.
			HttpResponseMessage response2 = httpClient.PostAsJsonAsync("http://127.0.0.1:8000/fetch", new {
				collection_name = "Resumes",
				filter = new { // Hopefully this should filter for the exact uploaded resume, since we don't have the ID yet...
					userId = resume.UserID,
					data = resume.FileBytes64
				},
				projection = new { _id = 1 }
			}).Result;

			// If second request failed at HTTP level, return false.
			if (!response2.IsSuccessStatusCode) return false;

			// Convert the second response content into a JSON object.
			using JsonDocument response2JSON = JsonDocument.Parse(response2.Content.ReadAsStringAsync().Result);

			// Extract the resume's database ID.
			string resumeID = response2JSON.RootElement.GetProperty("result")[0].GetProperty("_id").GetString();

			// Add new resume to this session's resume list, including the fetched DB ID.
			resumeDisplayer.Resumes.Add(resume with { ResumeID = resumeID });

			// TODO: Notify preprocessor of new resume, tell it to fetch from DB and preprocess.
				// resumeID (string) variable should be sent to preprocessor so it can locate the resume in the DB.

			return true; // Upload successful.
		} catch {
			// Handle network errors.
			return false;
		}
	}
	
	public bool EditResume(Resume resume) {
		// TODO: Update the given resume on the DB, return true if successfull.
		// TODO: Notify preprocessor (or processor?? whatever component uses configuration like expected salary) to re-evaluate resume, similar to the call in UploadResume.
		return false;
	}
}