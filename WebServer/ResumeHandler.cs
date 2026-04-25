namespace JobRush;
/// <summary>
/// Handles resume uploads and edits. This class is unique for each client connection.
/// </summary>
internal class ResumeHandler(SessionManager sessionManager) {
	// Injected Dependencies
	private readonly HttpClient httpClient = new();
	private readonly SessionManager sessionManager = sessionManager;

	/// <summary>
	/// The currently authenticated user's resumes.
	/// </summary>
	public List<Resume> Resumes { get; } = [];

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
			if (!response.IsSuccessStatusCode) {
				return false;
			} else {
				Resumes.Add(resume); // Add new resume to this session's resume list.
				// TODO: Notify preprocessor of new resume, tell it to fetch from DB and preprocess.
				return true; // Upload successful.
			}
		} catch {
			// Handle network errors.
			return false;
		}
	}
}