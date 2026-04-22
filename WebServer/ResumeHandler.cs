namespace JobRush;
/// <summary>
/// Handles resume uploads and edits. This class is unique for each client connection.
/// </summary>
internal class ResumeHandler {
	public bool UploadResume(Resume resume) {
		resume.FileBytes.Position = 0; // Ensures byte stream is read from the beginning.
		// TODO: Attempt to store resume in DB, return false on fail.
		// TODO: Notify preprocessor of new resume.
		// TODO: Add documentation.
		throw new NotImplementedException();
	}
}