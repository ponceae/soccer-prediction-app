const showTeamsBtn = document.getElementById('show-teams-btn')

showTeamsBtn.addEventListener('click', () => {

  fetch('/teams')
    .then(response => response.json())
    .then(teams => {
      const teamList = document.getElementById('team-list');
      teamList.style.display = 'block';
      teamList.innerHTML = '';

      teams.forEach(team => {
        const teamBtn = document.createElement('button');
        teamBtn.innerText = team.name;

        const compContainer = document.createElement('div');
        compContainer.style.display = 'none';
        compContainer.innerHTML = '';

        teamBtn.addEventListener('click', () => {
          if (compContainer.style.display === 'block') {
            compContainer.style.display = 'none';
            return;
          }

          if (compContainer.innerHTML === '') {
            compContainer.style.display = 'block';
            compContainer.innerHTML = 'Loading competitions...';

            fetch(`/teams/${team.id}/competitions`)
              .then(response => response.json())
              .then(competitions => {
                compContainer.innerHTML = '';

                competitions.forEach(comp => {
                  const compButton = document.createElement('button');
                  compButton.innerText = comp.name;
                  compButton.style.marginLeft ='20px';

                  const statsContainer = document.createElement('div');
                  statsContainer.style.display = 'none';
                  statsContainer.innerHTML = '';

                  compButton.addEventListener('click', () => {
                    if (statsContainer.style.display === 'block') {
                      statsContainer.style.display = 'none';
                      return;
                    }
                    if (statsContainer.innerHTML === '') {
                      statsContainer.style.display = 'block';
                      statsContainer.innerHTML = 'Fetching stats...';

                      fetch(`/teams/${team.id}/${comp.competition_id}/${comp.season_id}/league_table_data`)
                        .then(response => response.json())
                        .then(stats => {
                          statsContainer.innerHTML = `
                            <div style="margin-left: 40px; background: #eee; padding: 10px;">
                              <p>W: ${stats.wins}</p>
                              <p>L: ${stats.losses}</p>
                              <p>D: ${stats.draws}</p>
                              <p>PL: ${stats.matches_played}</p>
                              <p>GF: ${stats.goals_for}</p>
                              <p>GA: ${stats.goals_against}</p>
                              <p>GD: ${stats.goal_difference}</p>
                              <p>PTS: ${stats.points}</p>
                            </div>
                          `;
                        });
                    } else {
                      statsContainer.style.display = 'block';
                    }
                  });

                  compContainer.appendChild(compButton);
                  compContainer.appendChild(statsContainer);
                });
              });
          } else {
            compContainer.style.display = 'block';
          }
        });

        const listItem = document.createElement('li');
        listItem.style.listStyle = 'none';
        listItem.appendChild(teamBtn);
        listItem.appendChild(compContainer);
        teamList.appendChild(listItem);
      });
  });
});
