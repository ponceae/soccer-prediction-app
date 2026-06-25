fetch('/teams')
  .then(response => response.json())
  .then(data => {
    const listContainer = document.getElementById('team-list');

    data.forEach(team => {
      const listItem = document.createElement('li');
      listItem.innerText = `${team.name}`;
      listContainer.appendChild(listItem);
    });
  })
.catch(error => console.error('Error fetching data: ', error));

fetch('/matches')
  .then(response => response.json())
  .then(data => {
    const listContainer = document.getElementById('match-list');
    listContainer.innerHTML = '';

    data.forEach(match => {
      const rawDate = new Date(match.date)
      const fDate = rawDate.toLocaleDateString('en-US', {
        weekday: 'short', year: 'numeric', month: 'short', day: 'numeric',
      });
      
      const matchHTML = `
        <li>
          <h4>${fDate}</h4>
          <p>${match.home_team.name} vs ${match.away_team.name}</p>
        </li>
      `
      listContainer.insertAdjacentHTML('beforeend', matchHTML);
    });
  })
.catch(error => console.error('Error fetching data: ', error))
