namespace JobRush;
/// <summary>
/// Caches and displays the current user's resumes. This class is unique for each client connection.
/// </summary>
internal class ResumeDisplayer {
	/// <summary>
	/// The currently authenticated user's resumes.
	/// </summary>
	private readonly List<Resume> resumes = [];

	/// <summary>
	/// Gets an array containing the current user's resumes.
	/// </summary>
	/// <returns>An array copy of the user's resume list.</returns>
	public Resume[] GetResumes() => resumes.ToArray();

	/// <summary>
	/// Adds the given resume to the user's resume list and updates applicable UI.
	/// </summary>
	/// <param name="resume">The resume to add.</param>
	public void AddResume(Resume resume) {
		resumes.Add(resume);
		ResumeListUpdated?.Invoke();
	}

	/// <summary>
	/// Invoked when the resume list is added to, updated, or removed from.
	/// </summary>
	public event Action ResumeListUpdated;
}