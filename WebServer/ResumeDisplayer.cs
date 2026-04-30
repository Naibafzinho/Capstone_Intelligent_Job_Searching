namespace JobRush;
/// <summary>
/// Caches and displays the current user's resumes. This class is unique for each client connection.
/// </summary>
internal class ResumeDisplayer {
	/// <summary>
	/// The currently authenticated user's resumes.
	/// </summary>
	public List<Resume> Resumes { get; } = [];
}