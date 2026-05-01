namespace JobRush;

/// <summary>
/// Stores a job listing.
/// </summary>
/// <param name="Title">The job title.</param>
/// <param name="CompanyName">The company offering the job.</param>
/// <param name="DatePosted">The date this listing was posted.</param>
/// <param name="OriginalPostingSite">The site this listing was found on.</param>
/// <param name="OriginalPostingLink">The link to the original listing.</param>
/// <param name="Industries">The work industry/industries.</param>
/// <param name="ExperienceLevels">The desired experience level(s).</param>
/// <param name="EmploymentTypes">The employment type.</param>
/// <param name="SalaryRanges">The salary range(s).</param>
/// <param name="Locations">The work location(s).</param>
/// <param name="RemoteStatuses">The remote work options.</param>
/// <param name="CompanySizes">The employing company's size.</param>
/// <param name="Description">The job description.</param>
public record class JobListing(
	string Title,
	string CompanyName,
	string DatePosted,
	string OriginalPostingSite,
	string OriginalPostingLink,
	string[] Industries,
	string[] ExperienceLevels,
	string[] EmploymentTypes,
	string[] SalaryRanges,
	string[] Locations,
	string[] RemoteStatuses,
	string[] CompanySizes,
	string Description
);