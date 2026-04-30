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
	/// Returns the resume with the given DB ID, if it exists.
	/// </summary>
	/// <param name="resumeID">The ID of the desired resume (hexadecimal string).</param>
	/// <returns></returns>
	public Resume? GetResumeByID(string resumeID) => resumes.FirstOrDefault(r => r.ResumeID == resumeID);

	/// <summary>
	/// Adds the given resume to the user's resume list and updates applicable UI.
	/// </summary>
	/// <param name="resume">The resume to add.</param>
	public void AddResume(Resume resume) {
		if (resume.ResumeID == null) return; // TODO: Return feedback if add fails.
		resumes.Add(resume);
		ResumeListUpdated?.Invoke();
	}

	/// <summary>
	/// Removes the first resume matching the given DB ID.
	/// </summary>
	/// <param name="resumeID">The DB ID of the resume to remove.</param>
	public void RemoveResume(string resumeID) {
		Resume? targetResume = GetResumeByID(resumeID);
		if (targetResume == null) return; // TODO: Perhaps return feedback if remove fails?
		resumes.Remove(targetResume);
		ResumeListUpdated?.Invoke();
	}

	/// <summary>
	/// Invoked when the resume list is added to, updated, or removed from.
	/// </summary>
	public event Action ResumeListUpdated;
}