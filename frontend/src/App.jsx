import { useCallback, useState, useEffect } from 'react';
import { Navigate, Routes, Route, useNavigate, useLocation } from 'react-router-dom';

import './App.css';
import Sidebar from './components/Sidebar';
import LeagueLayout from './components/LeagueLayout';
import LeagueTable from './components/LeagueTable';
import TeamProfile from './components/TeamProfile';
import LeagueSummary from './components/LeagueSummary';
import Matchups from './components/Matchups';

export default function App() {
  const [menuData, setMenuData] = useState(null);
  const [leagueTable, setLeagueTable]= useState(null);
  const [error, setError] = useState(null);
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);

  const navigate = useNavigate();
  const location = useLocation();

  const isLeagueRoute = location.pathname.startsWith('/league/');
  const parts = location.pathname.split('/');
  const compId = isLeagueRoute ? parts[2]: null;
  const seasonId = isLeagueRoute ? parts[3]: null;

  const currentLeague = isLeagueRoute ? location.state : null;

  useEffect(() => {
    async function loadMenuData() {
      try {
        const response = await fetch('http://localhost:8000/menu_data');
        if (!response.ok) throw new Error('Failed to fetch menu data.');
        const data = await response.json();
        setMenuData(data);
      } catch (err) {
        console.error(err);
        setError(`Error, unable to load menu data: ${err.message}`);
      }
    }
    loadMenuData();
  }, []);

  useEffect(() => {
    if (isLeagueRoute && compId && seasonId) {
      async function fetchTable() {
        try {
          const url = (
            `http://localhost:8000/leagues/${compId}/${seasonId}/league_table`
          );
          const response = await fetch(url);
          if (!response.ok) throw new Error('Failed to fetch league table.');
          const data = await response.json();
          setLeagueTable(data);
        } catch (err) {
          console.error(err);
          setError(`Error, unable to load league standings: ${err.message}`);
        }
      }
      fetchTable();
    } 
  }, [compId, seasonId, isLeagueRoute]);

  function handleLeagueClick(compId, seasonId, leagueName, country, seasons) {
    setIsSidebarOpen(false);
    navigate(`/league/${compId}/${seasonId}/summary`, {
      state: { name: leagueName, country: country, seasons: seasons }
    });
  }

  const handleCloseSidebar = useCallback(() => {
    setIsSidebarOpen(false);
  }, []);

  return (
    <div className="app-container">
      <button 
        className={`menu-btn ${isSidebarOpen ? 'white-icon' : ''}`}
        onMouseDown={(e) => e.stopPropagation()}
        onClick={(e) => {
          e.stopPropagation();
          setIsSidebarOpen(!isSidebarOpen)}
        }
      >
        ☰
      </button>

      <Sidebar 
        menuData={menuData} 
        isOpen={isSidebarOpen}
        onLeagueClick={handleLeagueClick}
        closeSidebar={handleCloseSidebar}
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
              currentLeague && <LeagueLayout currentLeague={currentLeague}/>
            }>
              <Route index element={<Navigate to="table" replace/>}/>
              <Route path="summary" element={<LeagueSummary/>}/>
              <Route 
                path="table" 
                element={
                  leagueTable && (
                    <LeagueTable 
                      tableData={leagueTable} 
                      currentLeague={currentLeague}
                    />
                  )
                }
              />
              <Route path="matchups" element={<Matchups/>}/>
            </Route>
            <Route path="/team/:compId/:seasonId/:teamId" element={<TeamProfile/>}/>
          </Routes>
        
        </div>
      </main>
    </div>
  );
}
