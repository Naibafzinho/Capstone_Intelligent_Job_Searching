namespace JobRush;

using System.Net.Http.Json;

// This class is unique for each client connection.
internal class SessionManager {
	private readonly HttpClient httpClient;
	private bool authenticated = false;
	/// <summary>
	/// Used to check whether the current session is authenticated.
	/// </summary>
	/// <returns>True if session is authenticated.</returns>
	public bool IsAuthenticated() => authenticated;
	/// <summary>
	/// Performs a DB API call to authenticate the provided credentials.
	/// </summary>
	/// <param name="username">The username to authenticate.</param>
	/// <param name="password">The password to authenticate.</param>
	/// <returns>True if authentication succeeds (or already authenticated).</returns>
	public async Task<bool> AttemptLogin(string username, string password) {
		if (authenticated) return true;
		//authenticated = FakeAPICallLogin(username, password);
		var response = await httpClient.PostAsJsonAsync("API/LOCATION/HERE", new { username, password });
		authenticated = response.IsSuccessStatusCode;
		return authenticated;
	}
	/// <summary>
	/// Performs a DB API call to add a new user with the provided credentials. Automatically authenticates if successfull.
	/// </summary>
	/// <param name="email">The new user's email.</param>
	/// <param name="username">The new user's username.</param>
	/// <param name="password">The new user's password.</param>
	/// <returns>True if a new user was added successfully.</returns>
	public bool AttemptSignup(string email, string username, string password) {
		bool success = FakeAPICallSignup(email, username, password);
		if (success) authenticated = true;
		return success;
	}

	// Temporary test functions.
	private bool FakeAPICallLogin(string username, string password) => username == "admin" && password == "passwd" ? true : false;
	private bool FakeAPICallSignup(string email, string username, string password) => username != "admin" ? true : false;
}