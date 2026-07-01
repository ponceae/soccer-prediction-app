document.addEventListener('DOMContentLoaded', () => {

  const toggleMenuBtn = document.getElementById('toggleMenuBtn');
  const sidebar = document.getElementById('sidebar');
  const countryListContainer = document.getElementById('countryList');
  const mainHeader = document.getElementById('mainHeader');
  const tableContainer = document.getElementById('tableContainer');
  const homeBtn = document.getElementById('homeBtn')

  toggleMenuBtn.addEventListener('click', () => {
    sidebar.classList.toggle('open');
  });

  homeBtn.addEventListener('click', () => {
    sidebar.classList.remove('open');
    mainHeader.innerText = 'Soccer Prediction Model';

    tableContainer.innerHTML = '';
  });

  async function loadMenuData() {
    try {
      const response = await fetch('http://127.0.0.1:8000/menu_data');
      const data = await response.json();

      renderMenu(data);
    } catch (error) {
      console.error('Failed to load menu data', error);
      countryListContainer.innerHTML = `
        <li style="padding: 20px; color: #E74C3C;">Unable to load menu data.</li>
      `;
    }
  }

  function renderMenu(menuData) {
    countryListContainer.innerHTML = '';
    for (const [country, leagues] of Object.entries(menuData)) {
      
      const countryItem = document.createElement('li');
      countryItem.className = 'country-item';

      const countryHeader = document.createElement('div');
      countryHeader.className = 'country-header';
      // TODO: When more countries are added, create a flag filter.
      countryHeader.innerHTML = `
        🏴󠁧󠁢󠁥󠁮󠁧󠁿 ${country} <span class="arrow">▼</span>
      `;

      const leagueList = document.createElement('ul');
      leagueList.className = 'league-list';

      leagues.forEach(league => {
        const leagueItem = document.createElement('li');

        leagueItem.innerHTML = `
          <span class="league-item-text">${league.name}</span>
        `;
        
        leagueItem.addEventListener('click', () => {
          sidebar.classList.remove('open');
          mainHeader.innerText = league.name;

          renderLeagueTable(league.id, league.season_id)
        });

        leagueList.appendChild(leagueItem);
      });

      countryHeader.addEventListener('click', () => {
        leagueList.classList.toggle('show');
        countryHeader.classList.toggle('active');
      });

      countryItem.appendChild(countryHeader);
      countryItem.appendChild(leagueList);

      countryListContainer.appendChild(countryItem);
    }
  }

  async function renderLeagueTable(competitionId, seasonId) {
    tableContainer.innerHTML = `<p>Loading league standings...</p>`;

    try {
      const response = await fetch(`/leagues/${competitionId}/${seasonId}/league_table`);
      const data = await response.json();

      let tableHTML = `
        <table class="data-table">
          <thead>
            <tr>
              <th>Team</th>
              <th>Pl</th>
              <th>W</th>
              <th>D</th>
              <th>L</th>
              <th>GF</th>
              <th>GA</th>
              <th>GD</th>
              <th>Pts</th>
            </tr>
          </thead>
        <tbody>
      `;

      data.forEach(team => {
        tableHTML += `
          <tr>
            <td><strong>${team.team_name}</strong></td>
            <td>${team.matches_played}</td>
            <td>${team.wins}</td>
            <td>${team.draws}</td>
            <td>${team.losses}</td>
            <td>${team.gf}</td>
            <td>${team.ga}</td>
            <td>${team.gd}</td>
            <td><strong>${team.points}</strong></td>
          </tr>
        `;
      });

      tableHTML += `</tbody></table>`;

      tableContainer.innerHTML = tableHTML;
    } catch (error) {
      console.error('Failed to load table data', error);
      tableContainer.innerHTML = `
        <p style="color:#E74C3C">Error loading league standings.</p>
      `;
    }
  }

  loadMenuData();
});
