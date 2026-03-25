const skillsList = document.getElementById("skillsList");
const recommendationsList = document.getElementById("recommendationsList");

function addSkill() {
    const input = document.getElementById("skillInput");
    const skill = input.value;

    if (!skill) return;

    const div = document.createElement("div");
    div.className = "skill-item";
    div.textContent = skill;

    skillsList.appendChild(div);
    input.value = "";
}

// Fetch recommendations from backend
async function loadRecommendations() {
    const response = await fetch("http://localhost:5000/recommendations");
    const data = await response.json();

    data.forEach(skill => {
        const div = document.createElement("div");
        div.className = "recommendation-item";
        div.textContent = skill;

        // click to add skill
        div.onclick = () => {
            document.getElementById("skillInput").value = skill;
        };

        recommendationsList.appendChild(div);
    });
}

loadRecommendations();