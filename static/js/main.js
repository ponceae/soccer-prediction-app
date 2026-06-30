document.addEventListener('DOMContentLoaded', () => {

  const toggleMenuBtn = document.getElementById('toggleMenuBtn');
  const sidebar = document.getElementById('sidebar');
  const countryListContainer = document.getElementById('countryList');

  toggleMenuBtn.addEventListener('click', () => {
    sidebar.classList.toggle('open');
  });

  async function loadMenuData() {
    try {
      const response = await fetch('http://127.0.0.1:8000/league_menu');
      const data = await response.json();

      renderMenu(data);
    } catch (error) {
      console.error('Failed to load menu data', error);
      countryListContainer.innerHTML = 
        '<li style="padding: 20px; color: #E74C3C;">Unable to load menu data.</li>'
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
      countryHeader.innerHTML = `🏴󠁧󠁢󠁥󠁮󠁧󠁿 ${country} <span class="arrow">▼</span>`;

      const leagueList = document.createElement('ul');
      leagueList.className = 'league-list';

      leagues.forEach(leagueName => {
        const leagueItem = document.createElement('li');

        leagueItem.innerHTML = `<span class="league-item-text">${leagueName}</span>`;
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

  async function renderLeagueTable(leagueName) {
    tableContainer.innerHTML = '<p>Loading league standings...</p>';

    try {
      const response = await fetch('/teams/{team_id}/{competition_id}/{season_id}/league_table_data');
      const data = await response.json();
    }
  }

  loadMenuData();
});
