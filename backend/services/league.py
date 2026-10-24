from sqlmodel import and_, col, or_, select
from sqlalchemy.orm import selectinload 

from backend.api.models import Match, Team, TeamCompetition
from backend.services.base import BaseService

class LeagueService(BaseService):
    
    def btts_rate(self) -> float:
        """ 
        Calculate the rate of both teams scoring in the current competition season.
        
        Returns:
            float: The rate that both teams will score in the competition season.
        """
        max_matchweek_games = self.max_regular_season_matchweek()

        statement = select(Match).where(
            and_(
                Match.competition_id == self.competition_id,
                Match.season_id == self.season_id,
                Match.matchweek <= max_matchweek_games
            )
        )
        matches = self.session.exec(statement).all()
        total_matches = len(matches)
        
        if not total_matches:
            return 0.0
        
        btts_count = 0
        
        for match in matches:
            if match.ft_home_goals > 0 and match.ft_away_goals > 0:
                btts_count += 1
                
        return btts_count / total_matches
    
    def over_rate(self) -> float:
        """ 
        Calculate the rate of over 2.5 goals in the current competition season.
        
        Returns:
            float: The rate that over 2.5 goals will be scored in the competition 
                season.
        """
        max_matchweek_games = self.max_regular_season_matchweek()

        statement = select(Match).where(
            and_(
                Match.competition_id == self.competition_id,
                Match.season_id == self.season_id,
                Match.matchweek <= max_matchweek_games,
            )
        )
        matches = self.session.exec(statement).all()
        total_matches = len(matches)
        
        if not total_matches:
            return 0.0
        
        over_count = 0
        
        for match in matches:
            if match.ft_home_goals + match.ft_away_goals >= 3:
                over_count += 1
        
        return over_count / total_matches
    
    def league_summary(self) -> dict[str, float | dict[str, float]]:
        """ 
        Returns:
            dict[str, float | dict[str, float]]: A dictionary containing the 
                following league stats:
                    - Home league goal average
                    - Away league goal average
                    - Both teams to score rate
                    - Over 2.5 goals scored rate
        """
        h_league_goal_avg, a_league_goal_avg = self.league_goal_averages()
        
        return {
            'goal_averages': {
                'home_league_goal_avg': h_league_goal_avg,
                'away_league_goal_avg': a_league_goal_avg,
            },
            'btts_rate': self.btts_rate(),
            'over_rate': self.over_rate(),
        }
    
    def league_table_stats(
        self, team_id: int
    ) -> tuple[int, int, int, int, int, int, int, int]:
        """ 
        Returns:
            tuple[int, int, int, int, int, int, int, int]: The following league table
                stats:
                    - Wins
                    - Losses
                    - Draws
                    - Matches played
                    - Goals for
                    - Goals against
                    - Goal difference
                    - Points
        """
        max_matchweek_games = self.max_regular_season_matchweek()
                
        statement = select(Match).where(
            and_(
                Match.competition_id == self.competition_id,
                Match.season_id == self.season_id,
                Match.matchweek <= max_matchweek_games,
                or_(
                    Match.home_team_id == team_id,
                    Match.away_team_id == team_id,
                ),
            ),
        )
        team_matches = self.session.exec(statement).all()
        
        wins, losses, draws, gf, ga = 0, 0, 0, 0, 0
        
        for match in team_matches:
            if match.home_team_id == team_id:
                gf += match.ft_home_goals
                ga += match.ft_away_goals
                if match.ft_home_goals > match.ft_away_goals:
                    wins += 1
                elif match.ft_home_goals < match.ft_away_goals:
                    losses += 1
                else:
                    draws += 1
                
            elif match.away_team_id == team_id:
                gf += match.ft_away_goals
                ga += match.ft_home_goals
                if match.ft_away_goals > match.ft_home_goals:
                    wins += 1
                elif match.ft_away_goals < match.ft_home_goals:
                    losses += 1
                else:
                    draws += 1
            
        total_matches = wins + losses + draws
        gd = gf - ga
        points = (wins * 3) + draws
        
        return wins, losses, draws, total_matches, gf, ga, gd, points
    
    def generate_league_table(self):
        league_teams = self.session.exec(
            select(Team)
            .join(TeamCompetition)
            .where(
                TeamCompetition.competition_id == self.competition_id,
                TeamCompetition.season_id == self.season_id,
            )
        ).all()
            
        table = []
                
        for team in league_teams:
            if team.id is None:
                continue
            (
                wins, 
                losses, 
                draws, 
                total_matches, 
                gf, 
                ga, 
                gd, 
                points,
            ) = self.league_table_stats(team.id)
            
            table.append({
                'team_id': team.id,
                'team_name': team.name,
                'matches_played': total_matches,
                'points': points,
                'wins': wins,
                'losses': losses,
                'draws': draws,
                'gf': gf,
                'ga': ga,
                'gd': gd,
            })
        
        return sorted(
            table, key=lambda x: (x['points'], x['gd'], x['gf']), reverse=True
        )
    
    def get_regular_season_matchups(self):
        max_matchweek_games = self.max_regular_season_matchweek()
                
        statement = (
            select(Match)
            .where(
                Match.competition_id == self.competition_id,
                Match.season_id == self.season_id,
                Match.matchweek <= max_matchweek_games
            )
            .options(
                selectinload(Match.home_team), # type: ignore
                selectinload(Match.away_team), # type: ignore
            )
            .order_by(col(Match.date).desc())
        )
        
        return self.session.exec(statement).all()
    
    def get_knockout_matches(self):
        max_matchweek_games = self.max_regular_season_matchweek()
                
        statement = (
            select(Match)
            .where(
                Match.competition_id == self.competition_id,
                Match.season_id == self.season_id,
                Match.matchweek > max_matchweek_games,
            )
            .options(
                selectinload(Match.home_team), # type: ignore
                selectinload(Match.away_team), # type: ignore
            )
        )

        return self.session.exec(statement).all()
