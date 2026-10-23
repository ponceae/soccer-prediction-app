from dataclasses import dataclass
from sqlmodel import and_, col, func, select, Session

from backend.api.models import Match, TeamCompetition, Season

@dataclass
class HomeAwayID:
    home_team_id: int 
    away_team_id: int

@dataclass
class BaseService:
    session: Session
    competition_id: int
    season_id: int
    
    def league_goal_averages(self, up_to_mw: int | None = None) -> tuple[float, float]:
        """ 
        Calculate the league goal averages up to the specified matchweek for 
        the specified league. If no matches have been played fallback to a default
        value.
        
        Args:
            up_to_mw (int | None): The max matchweek limit.
            
        Returns:
            tuple[float, float]: The following league stats:
                - Home goal average
                - Away goal average
        """
        max_matchweek = self.max_regular_season_matchweek()

        conditions = [
            Match.competition_id == self.competition_id,
            Match.season_id == self.season_id,
            Match.matchweek <= max_matchweek,
        ]
        
        if up_to_mw is not None:
            conditions.append(Match.matchweek < up_to_mw)

        statement = select(Match).where(and_(*conditions))
        competition_matches = self.session.exec(statement).all()
        total_matches = len(competition_matches)
        
        if not total_matches:
            return 1.15, 1.15
        
        h_goals = sum(m.ft_home_goals for m in competition_matches)
        a_goals = sum(m.ft_away_goals for m in competition_matches)
        
        h_goal_avg = h_goals / total_matches
        a_goal_avg = a_goals / total_matches
        
        return h_goal_avg, a_goal_avg
    
    def max_regular_season_matchweek(self) -> int:
        """ 
        Calculate the maximum number of matchweeks possible in the regular season
        for the specified league.
        
        Returns:
            int: The maximum number of matchweeks
        """
        team_count = self.session.exec(
            select(
                func.count(col(TeamCompetition.team_id))
            )
            .where(
                TeamCompetition.competition_id == self.competition_id,
                TeamCompetition.season_id == self.season_id,
            )
        ).one()

        return (team_count - 1) * 2
    
    def get_previous_season_id(self) -> int | None:
        """ 
        Return the previous season's ID that appears chronologically ordered by
        year if it exists.
        
        Returns:
            (int | None) The previous season's ID, `None` if it does not exist.
        """
        curr_season = self.session.get(Season, self.season_id)
        
        if not curr_season:
            return None
        
        statement = (
            select(Season.id)
            .where(Season.year < curr_season.year)
            .order_by(
                col(Season.year).desc()
            )
            .limit(1)
        )
        
        return self.session.exec(statement).first()
