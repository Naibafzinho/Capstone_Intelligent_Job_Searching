namespace JobRush;

/// <summary>
/// Stores a user's resume file with job match configuration.
/// </summary>
/// <param name="UserID">The database ID of this resume's associated user (hex string).</param>
/// <param name="Filename">The name of the resume.</param>
/// <param name="FileBytes">The resume file as binary data.</param>
/// <param name="UploadDate">The date of the resume upload.</param>
/// <param name="Config">The resume's job match configuration data.</param>
internal record Resume(
	string UserID,
	string Filename,
	MemoryStream FileBytes,
	string UploadDate,
	ResumeConfig Config
);

/// <summary>
/// Stores job match configuration data for a resume.
/// </summary>
/// <param name="IndustryPreferences">The resume owner's desired work industry.</param>
/// <param name="ExperienceLevels">The resume owner's desired job experience level. (Entry-level, senior, etc.)</param>
/// <param name="EmploymentType">The resume owner's desired employment type. (Full-time, part-time, etc.)</param>
/// <param name="ExpectedSalaryRanges">The resume owner's desired salary range(s).</param>
/// <param name="Locations">The resume owner's desired work location(s).</param>
/// <param name="RemoteStatus">The resume owner's remote work preference.</param>
/// <param name="CompanySizes">The resume owner's desired company size(s).</param>
/// <param name="Tags">A set of misc. strings for job match indexing and filtering.</param>
internal record ResumeConfig (
	string[] IndustryPreferences,
	string[] ExperienceLevels,
	string[] EmploymentType,
	string[] ExpectedSalaryRanges,
	string[] Locations,
	string[] RemoteStatus,
	string[] CompanySizes,
	string[] Tags
);