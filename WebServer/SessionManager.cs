using System.Text.Json;

namespace JobRush;
/// <summary>
/// Handles user authentication. This class is unique for each client connection.
/// </summary>
internal class SessionManager(ResumeDisplayer resumeDisplayer) {
	// Injected Dependencies
	private readonly HttpClient httpClient = new();
	private readonly ResumeDisplayer resumeDisplayer = resumeDisplayer;

	private bool authenticated = false;

	/// <summary>
	/// The database ID of the currently authenticated user (hex string). Null if not authenticated.
	/// </summary>
	private string? userID;
	/// <summary>
	/// The username of the currently authenticated user. Null if not authenticated.
	/// </summary>
	private string? username;

	/// <summary>
	/// Checks whether the current session is authenticated.
	/// </summary>
	/// <returns>True if session is authenticated.</returns>
	public bool IsAuthenticated() => authenticated;
	/// <summary>
	/// Gets the current session's user's database ID.
	/// </summary>
	/// <returns>The database ID of the currently authenticated user, or null if not authenticated.</returns>
	public string? GetUserID() => userID;

	/// <summary>
	/// Unauthenticates the current session. Should be followed by a redirect.
	/// </summary>
	public void Logout() => authenticated = false;

	/// <summary>
	/// Performs a DB API call to authenticate the provided credentials.
	/// </summary>
	/// <param name="username">The username to authenticate.</param>
	/// <param name="password">The password to authenticate.</param>
	/// <returns>True if authentication succeeds (or already authenticated).</returns>
	public bool AttemptLogin(string username, string password) {
		if (authenticated) return true;
		
		try {
			// Ask DB if username/password combo is valid.
			HttpResponseMessage response = httpClient.PostAsJsonAsync("http://127.0.0.1:8000/login", new {
				username,
				password
			}).Result;

			// If request failed at HTTP level, return false.
			if (!response.IsSuccessStatusCode) return false;

			// Convert the response content into a JSON object.
			using JsonDocument responseJSON = JsonDocument.Parse(response.Content.ReadAsStringAsync().Result);

			// Get the success property if possible.
			if (responseJSON.RootElement.TryGetProperty("result", out JsonElement successElement)) {
				// If DB confirmed credentials are valid...
				if (successElement.GetBoolean()) {
					// Query DB for userID.
					HttpResponseMessage response2 = httpClient.PostAsJsonAsync("http://127.0.0.1:8000/fetch", new {
						collection_name = "Users",
						filter = new { username },
						projection = new { _id = 1 }
					}).Result;

					// If second request failed at HTTP level, return false.
					if (!response2.IsSuccessStatusCode) return false;

					// Convert the second response content into a JSON object.
					using JsonDocument response2JSON = JsonDocument.Parse(response2.Content.ReadAsStringAsync().Result);

					// Extract and record the user's database ID.
					userID = response2JSON.RootElement.GetProperty("result")[0].GetProperty("_id").GetString();

					// Retrieve the user's existing resumes from the DB, if any.
					HttpResponseMessage response3 = httpClient.PostAsJsonAsync("http://127.0.0.1:8000/fetch", new {
						collection_name = "Resumes",
						filter = new { userId = userID },
						projection = new { // 0 skips value in query result.
							userId = 0,
							data = 0,
							isActive = 0,
							extractedKeywords = 0,
							atsScore = 0
						}
					}).Result;

					// If third request failed at HTTP level, return false.
					if (!response3.IsSuccessStatusCode) return false;

					// Convert the third response content into a JSON object.
					using JsonDocument response3JSON = JsonDocument.Parse(response3.Content.ReadAsStringAsync().Result);

					// Extract the resume elements from the response JSON.
					List<JsonElement> returnedResumes = new(response3JSON.RootElement.GetProperty("result").EnumerateArray());

					// Convert each resume element into an object and store them in ResumeDisplayer.
					foreach (JsonElement element in returnedResumes) {
						string GetSubelementString(string subelementName) => element.GetProperty(subelementName).GetString();
						string[] GetSubelementArray(string subelementName) => element.GetProperty(subelementName).EnumerateArray().Select(x => x.GetString()).ToArray();
						resumeDisplayer.AddResume(new Resume(
							UserID: userID,
							ResumeID: GetSubelementString("_id"),
							Filename: GetSubelementString("filename"),
							FileBytes64: null, // Raw file is not needed for display.
							UploadDate: GetSubelementString("uploadDate"),
							new ResumeConfig(
								IndustryPreferences: GetSubelementArray("industryConfig"),
								ExperienceLevels: GetSubelementArray("experienceLevelConfig"),
								EmploymentType: GetSubelementArray("jobTypeConfig"),
								ExpectedSalaryRanges: GetSubelementArray("expectedSalaryConfig"),
								Locations: GetSubelementArray("locationConfig"),
								RemoteStatus: GetSubelementArray("remoteConfig"),
								CompanySizes: GetSubelementArray("companySizeConfig"),
								Tags: GetSubelementArray("tags")
							)
						));
					}

					this.username = username; // Record current user's username.
					authenticated = true;
					return true; // Indicate successful login.
				}
			}

			// Return false by default to prevent login if DB response fails.
			return false;
		} catch {
			// Handle network errors.
			return false;
		}
	}

	/// <summary>
	/// Performs a DB API call to add a new user with the provided credentials. Automatically authenticates if successfull.
	/// </summary>
	/// <param name="email">The new user's email.</param>
	/// <param name="username">The new user's username.</param>
	/// <param name="password">The new user's password.</param>
	/// <returns>True if a new user was added successfully.</returns>
	public bool AttemptSignup(string email, string username, string password) {
		// Validation rules:
		if (string.IsNullOrWhiteSpace(email) || string.IsNullOrWhiteSpace(username) || string.IsNullOrWhiteSpace(password)) return false;

		try {
			// Send signup request to DB API.
			HttpResponseMessage response = httpClient.PostAsJsonAsync("http://127.0.0.1:8000/insertEntry", new {
				collection_name = "Users",
				entry = new {
					username,
					passwordHash = password,
					email
				}
			}).Result;

			// If request failed at HTTP level, return false.
			if (!response.IsSuccessStatusCode) return false;

			// Convert the response content into a JSON object.
			using JsonDocument responseJSON = JsonDocument.Parse(response.Content.ReadAsStringAsync().Result);

			// Get the success property if possible.
			
			if (responseJSON.RootElement.TryGetProperty("result", out JsonElement resultElement)){
					// If result is a string → it is inserted_id → SUCCESS
					if (resultElement.ValueKind == JsonValueKind.String)
					{
						authenticated = true;
						return true;
					}
			}

			// Return false by default.
			return false;
		} catch {
			// Handle network errors.
			return false;
		}
	}

	// Temporary test functions. Simulates a single account with username "admin", password "passwd", and an arbitrary email.
	private bool FakeAPICallLogin(string username, string password) => username == "admin" && password == "passwd";
	private bool FakeAPICallSignup(string email, string username, string password) => username != "admin";
}