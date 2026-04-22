namespace JobRush;
/// <summary>
/// Handles resume uploads. This class is unique for each client connection.
/// </summary>
internal class ResumeUploader {
	public bool Upload(MemoryStream resumeBytes) {
		resumeBytes.Position = 0; // Ensures referenced stream is read from the beginning.
		// TODO: Attempt to store resume in DB, return false on fail.
		// TODO: Notify preprocessor of new resume.
		// TODO: Add documentation.
		throw new NotImplementedException();
	}
}