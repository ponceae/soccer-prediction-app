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
  loadMenuData();

  // +=========================+
  //       Event Listeners
  // +=========================+

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

      if (globalMenuData?.[currCountry]?.[currLeagueName]) {
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

  countryListContainer.addEventListener('click', (event) => {
    const clickedHeader = event.target.closest('.country-header');
    if (clickedHeader) {
      const leagueList = clickedHeader.nextElementSibling;
      leagueList.classList.toggle('show');
      clickedHeader.classList.toggle('active');
      return;
    }

    const clickedItem = event.target.closest('.league-item');
    if (clickedItem) {
      sidebar.classList.remove('open');

      const { country, leagueName, compId, seasonId } = clickedItem.dataset;
      const seasons = globalMenuData[country][leagueName];
      
      currLeagueName = leagueName;
      currCountry = country;

      renderSeasonSelect(seasons, compId, leagueName, country);
      renderLeagueTable(compId, seasonId);
    }
  });

  // +=========================+
  //     API & Data Fetching
  // +=========================+

  async function loadMenuData() {
    try {
      const data = await fetchJSON('/menu_data')
      globalMenuData = data;
      renderMenu(data);
    } catch (error) {
      console.error('Failed to load menu data', error);
      showError(countryListContainer, 'Unable to load menu data.');
    }
  }

  async function renderLeagueTable(competitionId, seasonId, pushToHistory = true) {
    currCompId = competitionId;
    currSeasonId = seasonId;
    
    showLoading(tableContainer, 'Loading league standings...');

    try {
      const data = await fetchJSON(
        `/leagues/${competitionId}/${seasonId}/league_table`
      );

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
        let rowClass = (index >= 0 && index <= 3) ? 'ucl' 
                    : (index == 4) ? 'uel' 
                    : (index >= data.length- 3) ? 'relegation' 
                    : '';

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
      showError(tableContainer, 'Error loading league standings.')
    }
  }

  async function displayTeamInfo(teamId, pushToHistory = true) {
    showLoading(tableContainer, 'Loading team profile...');

    try {
      const data = await fetchJSON(`/teams/${teamId}`);
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
      showError(tableContainer, 'Unable to load team data.')
    }
  }

  // +=========================+
  //        UI Functions
  // +=========================+

  function renderMenu(menuData) {
    let menuHTML = '';

    for (const [country, competitions] of Object.entries(menuData)) {
      let leaguesHTML = '';

      for (const [leagueName, seasons] of Object.entries(competitions)) {
        const latestSeason = seasons[0];
        leaguesHTML += `
          <li
            class="league-item"
            data-country="${country}"
            data-league-name="${leagueName}"
            data-comp-id="${latestSeason.competition_id}"
            data-season-id="${latestSeason.season_id}"
          >
            <span class="league-item-text">${leagueName}</span>
          </li>
        `;
      }

      menuHTML += `
        <li class="country-item">
          <div class="country-header">
            🏴󠁧󠁢󠁥󠁮󠁧󠁿 ${country} <span class="arrow">▼</span>
          </div>
          <ul class="league-list">
            ${leaguesHTML}
          </ul>
        </li>
      `;
    }
    countryListContainer.innerHTML = menuHTML;
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
      renderLeagueTable(currCompId, selectedSeasonId, true)
    }
  }

  function renderTeamInfo(teamData) {
    tableContainer.innerHTML = `
      <div class="team-profile-dashboard">
        <h2>${teamData.name}</h2>
        <p>blah</p>
      </div>
    `;
  }

  // +=========================+
  //      Helper Functions
  // +=========================+ 

  async function fetchJSON(endpoint) {
    const response = await(fetch(endpoint));
    if (!response.ok) {
      throw new Error(`HTTP Error: ${response.status}`);
    }
    return response.json();
  }

  function showLoading(container, message = 'Loading...') {
    container.innerHTML = `<p class="status-message">${message}</p>`;
  }

  function showError(container, message = 'An error occured.') {
    container.innerHTML = `<p class="status-message error">${message}</p>`;
  }  
});
