document.addEventListener('DOMContentLoaded', () => {

  const toggleMenuBtn = document.getElementById('toggleMenuBtn');
  const sidebar = document.getElementById('sidebar');
  const countryListContainer = document.getElementById('countryList');
  const mainHeader = document.getElementById('mainHeader');
  const tableContainer = document.getElementById('tableContainer');
  const homeBtn = document.getElementById('homeBtn')

  let currCompId = null;
  let currSeasonId = null;
  let currLeagueName = '';
  let currCountry = '';
  let globalMenuData = null;

  history.replaceState({ view: 'home' }, '', window.location.pathname);

  window.addEventListener('popstate', (event) => {
    const state = event.state;

    if (!state || state.view === 'home') {
      mainHeader.innerText = `Soccer Prediction Model`;
      tableContainer.innerHTML = '';
      return;
    }

    if (state.view === 'table') {
      currLeagueName = state.leagueName;
      currCountry = state.country;
      currCompId = state.competitionId;
      currSeasonId = state.seasonId;

      if (globalMenuData && globalMenuData[currCountry] && globalMenuData[currCountry][currLeagueName]) {
        const seasons = globalMenuData[currCountry][currLeagueName];
        renderSeasonSelect(seasons, currCompId, currLeagueName, currCountry);
      }

      renderLeagueTable(state.competitionId, state.seasonId, false);
    }
    else if (state.view === 'team') {
      displayTeamInfo(state.teamId, false);
    }
  });

  toggleMenuBtn.addEventListener('click', () => {
    sidebar.classList.toggle('open');
  });

  homeBtn.addEventListener('click', () => {
    sidebar.classList.remove('open');
    mainHeader.innerText = 'Soccer Prediction Model';

    tableContainer.innerHTML = '';
  });

  tableContainer.addEventListener('click', (event) => {
    const clickedRow = event.target.closest('tr');
    if (clickedRow) {
      const teamId = clickedRow.dataset.teamId;
      displayTeamInfo(teamId);
    }
  });

  async function displayTeamInfo(teamId, pushToHistory = true) {
    try {
      const response = await fetch(`/teams/${teamId}`);
      const data = await response.json();

      renderTeamInfo(data);

      if (pushToHistory) {
        history.pushState(
          { 
            view: 'team', 
            teamId: teamId,
            competitionId: currCompId,
            seasonId: currSeasonId,
            leagueName: currLeagueName,
            country: currCountry,
          },
          '',
          `#team-${teamId}`
        );
      }
    } catch (error) {
      console.error('Failed to load team data', error);
      tableContainer.innerHTML = `
        <li style="padding: 20px; color: #E74C3C;">Unable to load team data.</li>
      `;
    }
  }

  async function loadMenuData() {
    try {
      const response = await fetch('http://127.0.0.1:8000/menu_data');
      const data = await response.json();

      globalMenuData = data;
      renderMenu(data);
    } catch (error) {
      console.error('Failed to load menu data', error);
      countryListContainer.innerHTML = `
        <li style="padding: 20px; color: #E74C3C;">Unable to load menu data.</li>
      `;
    }
  }

  function renderTeamInfo(teamData) {
    tableContainer.innerHTML = `
      <div class="team-profile-view">
        <h2>${teamData.name}</h2>
      </div>
    `;
  }

  function renderMenu(menuData) {
    countryListContainer.innerHTML = '';

    for (const [country, competitions] of Object.entries(menuData)) {
      
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

      for (const [leagueName, seasons] of Object.entries(competitions)) {
        const leagueItem = document.createElement('li');

        leagueItem.innerHTML = `
          <span class="league-item-text">${leagueName}</span>
        `;

        leagueItem.addEventListener('click', () => {
          sidebar.classList.remove('open');

          const latestSeason = seasons[0]

          currLeagueName = leagueName;
          currCountry = country;

          renderSeasonSelect(seasons, latestSeason.competition_id, leagueName, country)

          renderLeagueTable(latestSeason.competition_id, latestSeason.season_id)
        });

        leagueList.appendChild(leagueItem)
      }

      countryHeader.addEventListener('click', () => {
        leagueList.classList.toggle('show');
        countryHeader.classList.toggle('active');
      });

      countryItem.appendChild(countryHeader);
      countryItem.appendChild(leagueList);

      countryListContainer.appendChild(countryItem);
    }
  }

  function renderSeasonSelect(seasons, currCompId, leagueName, country) {
    const headerContainer = document.getElementById('mainHeader');

    const optionsHTML = seasons.map(s =>
      `<option value="${s.season_id}">${s.season_year}</option>`
    ).join('');

    headerContainer.innerHTML = `
      <div class="league-header-container">
        <div class="league-title-group">
          <img
            src="/logos/competitions/${currCompId}.svg"
            class="competition-badge"
            alt="${leagueName} logo"
            onerror="this.style.display='none'"
          >
          <div class="league-text">
            <h2>${leagueName}</h2>
            <p class="country-subtitle">${country}</p>
          </div>
        </div>

        <div class="season-select-group">
          <label for="seasonSelect">Season:</label>
          <select id="seasonSelect" class="season-dropdown">
            ${optionsHTML}
          </select>
        </div>
      </div>
    `;

    const selectElem = document.getElementById('seasonSelect');
    selectElem.value = currSeasonId || seasons[0].season_id;
    selectElem.onchange = (e) => {
      const selectedSeasonId = e.target.value;
      renderLeagueTable(competitionId, selectedSeasonId, true)
    }
  }

  async function renderLeagueTable(competitionId, seasonId, pushToHistory = true) {
    currCompId = competitionId;
    currSeasonId = seasonId;
    
    tableContainer.innerHTML = `<p>Loading league standings...</p>`;

    try {
      const response = await fetch(`/leagues/${competitionId}/${seasonId}/league_table`);
      const data = await response.json();

      if (pushToHistory) {
        history.pushState(
          { 
            view: 'table', 
            competitionId, 
            seasonId, 
            leagueName: currLeagueName, 
            country: currCountry 
          },
          '',
          `#league-${competitionId}`
        );
      }

      let tableHTML = `
        <table class="data-table">
          <thead>
            <tr>
              <th>#</th>
              <th></th>
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

      data.forEach((team, index) => {
        let rowClass = '';

        if (index >= 0 && index <= 3) {
          rowClass = 'ucl';
        }

        else if (index == 4) {
          rowClass = 'uel';
        }

        else if (index >= data.length - 3) {
          rowClass = 'relegation';
        }

        tableHTML += `
          <tr class="${rowClass}" data-team-id="${team.team_id}">
            <td>${index + 1}</td>
            <td class="team-cell">
            <img
              src="/logos/teams/${team.team_id}.svg"
              class="team-badge"
              alt="${team.team_name} logo"
            >
            <strong>${team.team_name}</strong>
            </td>
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
