import { useState, useEffect } from 'react';
import { Routes, Route, useNavigate, useLocation } from 'react-router-dom';
import Sidebar from './components/Sidebar';
import LeagueTable from './components/LeagueTable';
import './App.css';

export default function App() {
  const [menuData, setMenuData] = useState(null);
  const [leagueTable, setLeagueTable]= useState(null);
  const [currentLeague, setCurrentLeague] = useState(null);
  const [currentTeam, setCurrentTeam] = useState(null);
  const [loading, setLoading] = useState(null);
  const [error, setError] = useState(null);
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);

  const navigate = useNavigate();
  const location = useLocation();

  useEffect(() => {
    async function loadMenuData() {
      try {
        const response = await fetch('http://localhost:8000/menu_data');
        if (!response.ok) {
          throw new Error('Failed to fetch');
        }
        const data = await response.json();
        setMenuData(data);
      } catch(err) {
        console.error(err);
        setError('Unable to load menu data.');
      }
    }
    loadMenuData();
  }, []);

  useEffect(() => {
    if (location.pathname.startsWith('/league/')) {
      const parts = location.pathname.split('/');
      const compId = parts[2];
      const seasonId = parts[3];

      if (location.state) {
        setCurrentLeague(location.state);
      }

      async function fetchTable() {
        try {
          const response = await fetch(`http://localhost:8000/leagues/${compId}/${seasonId}/league_table`);
          if (!response.ok) {
            throw new Error('Failed to fetch league table.');
          }
          const data = await response.json();
          setLeagueTable(data);
        } catch(err) {
          console.error(err);
          setError('Unableto load league standings.');
        }
      }
      fetchTable();
    } else {
      setLeagueTable(null);
      setCurrentLeague(null);
    }
  }, [location.pathname, location.state]);

  async function handleLeagueClick(compId, seasonId, leagueName, country) {
    setIsSidebarOpen(false);

    navigate(`/league/${compId}/${seasonId}`, {
      state: { name: leagueName, country: country }
    });
  }

  return (
    <div className="app-container">
      <button 
        className={`menu-btn ${isSidebarOpen ? 'white-icon' : ''}`}
        onClick={() => setIsSidebarOpen(!isSidebarOpen)}
      >
        ☰
      </button>

      <Sidebar 
        menuData={menuData} 
        isOpen={isSidebarOpen}
        onLeagueClick={handleLeagueClick}
      />

      <main className="landing-page">
        <header id="mainHeader">
          <h1>Soccer Prediction Model</h1>
        </header>

        <div id="tableContainer">
          {error && <p className="status-message error">{error}</p>}
        
          <Routes>
            <Route path="/" element={null}/>
            <Route path="/league/:compId/:seasonId" element={
              leagueTable && <LeagueTable tableData={leagueTable} currentLeague={currentLeague}/>
            }/>
          </Routes>
        
        </div>
      </main>
    </div>
  );
}