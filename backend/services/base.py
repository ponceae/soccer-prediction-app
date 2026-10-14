from dataclasses import dataclass
from sqlmodel import and_, col, func, select, Session

from models import Match, TeamCompetition

@dataclass
class HomeAwayID:
    home_team_id: int 
    away_team_id: int

@dataclass
class BaseService:
    session: Session
    competition_id: int
    season_id: int
    
    def league_goal_averages(self):
        max_matchweek = self.max_regular_season_matchweek()

        statement = select(Match).where(
            and_(
                Match.competition_id == self.competition_id, 
                Match.season_id == self.season_id,
                Match.matchweek <= max_matchweek,
            )
        )
        competition_matches = self.session.exec(statement).all()
        total_matches = len(competition_matches)
        
        if not total_matches:
            return 0.0, 0.0
        
        h_goals = sum(m.ft_home_goals for m in competition_matches)
        a_goals = sum(m.ft_away_goals for m in competition_matches)
        
        h_goal_avg = h_goals / total_matches
        a_goal_avg = a_goals / total_matches
        
        return h_goal_avg, a_goal_avg
    
    def max_regular_season_matchweek(self):
        team_count = self.session.exec(
        select(func.count(col(TeamCompetition.team_id)))
        .where(
            TeamCompetition.competition_id == self.competition_id,
            TeamCompetition.season_id == self.season_id,
            )
        ).one()

        return (team_count - 1) * 2