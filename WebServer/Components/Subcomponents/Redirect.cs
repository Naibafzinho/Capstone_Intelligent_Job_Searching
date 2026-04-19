using Microsoft.AspNetCore.Components;

namespace JobRush.Components.Subcomponents;
/// <summary>
/// Automatically redirects on page load if unauthenticated, or if authenticated and Invert == true.
/// </summary>
public class Redirect : ComponentBase {
	[Inject] private NavigationManager navigationManager { get; set; } = default!;
	[Inject] private SessionManager sessionManager { get; set; } = default!;

	protected bool invert = false;

	protected override void OnInitialized() {
		base.OnInitialized();
		
		// Redirect to home page if not authenticated, or if authenticated and invert == true.
		if (sessionManager.IsAuthenticated() == invert) {
			navigationManager.NavigateTo("/");
		}
	}
}