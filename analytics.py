from dataclasses import dataclass
import math
from sqlmodel import and_, or_, Session, select

from models import Match

MAX_GOAL_THRESHOLD = 8

@dataclass
class HomeAwayID:
    home_team_id: int
    away_team_id: int

@dataclass
class Analytics:
    session: Session
    competition_id: int
    season_id: int 

    def league_goal_averages(self) -> tuple[float, float]:
        """
        Find and return the home and away goal averages for a particular season in the 
        given competition.
        
        Returns:
            tuple[float, float]: The current competition season total:
                - Home goal averages
                - Away goal averages
        """
        filter = select(Match).where(
            and_(
                Match.competition_id == self.competition_id, 
                Match.season_id == self.season_id,
            )
        )
        competition_matches = self.session.exec(filter).all()
        total_matches = len(competition_matches)
        
        if not total_matches:
            return 0.0, 0.0
        
        h_goals = sum(m.home_goals for m in competition_matches)
        a_goals = sum(m.away_goals for m in competition_matches)
        
        h_goal_avg = h_goals / total_matches
        a_goal_avg = a_goals / total_matches
        
        return h_goal_avg, a_goal_avg

    def team_strengths(self, team_id: int) -> tuple[float, float, float, float]:
        """
        Find and return the attacking and defensive strengths for the given team at 
        both home and away.
        
        Args:
            team_id (int): The id for the team to evaluate.

        Returns:
            tuple[float, float, float, float]: The team's
                - Home attack strength
                - Home defense strength
                - Away attack strength
                - Away defense strength  
            
                For the current competition season.
        """
        league_h_goal_avg, league_a_goal_avg = self.league_goal_averages()

        h_match_filter = select(Match).where(
            and_(
                Match.competition_id == self.competition_id,
                Match.season_id == self.season_id,
                Match.home_team_id == team_id
            )
        )
        a_match_filter = select(Match).where(
            and_(
                Match.competition_id == self.competition_id,
                Match.season_id == self.season_id,
                Match.away_team_id == team_id
            )
        )
        
        h_matches = self.session.exec(h_match_filter).all()
        a_matches = self.session.exec(a_match_filter).all()
        
        total_h_matches = len(h_matches)
        total_a_matches = len(a_matches)

        if not total_h_matches and not total_a_matches:
            return 0.0, 0.0, 0.0, 0.0

        h_goals = sum(m.home_goals for m in h_matches)
        a_goals = sum(m.away_goals for m in a_matches)
        
        h_goals_conceeded = sum(m.away_goals for m in h_matches)
        a_goals_conceeded = sum(m.home_goals for m in a_matches)
        
        avg_h_goals = h_goals / total_h_matches
        avg_a_goals = a_goals / total_a_matches
        
        avg_h_goals_conceeded = h_goals_conceeded / total_h_matches
        avg_a_goals_conceeded = a_goals_conceeded / total_a_matches
        
        h_atk = avg_h_goals / league_h_goal_avg
        h_def = avg_h_goals_conceeded / league_a_goal_avg
        
        a_atk = avg_a_goals / league_a_goal_avg
        a_def = avg_a_goals_conceeded / league_h_goal_avg

        return h_atk, h_def, a_atk, a_def

    def expected_goals(self, team_ids: HomeAwayID) -> tuple[float, float]:
        """
        Find and return the expected goal values for the given matchup.

        Args:
            team_ids (HomeAwayID): The ids for the home and away teams to evaluate.

        Returns:
            tuple[float, float]: The matchup's:
                - Home expected goals
                - Away expected goals
        """
        h_home_atk, h_home_def, _, _ = self.team_strengths(team_ids.home_team_id)
        _, _, a_away_atk, a_away_def = self.team_strengths(team_ids.away_team_id)
        
        league_h_goal_avg, league_a_goal_avg = self.league_goal_averages()
        
        home_xg = (h_home_atk * a_away_def) * league_h_goal_avg
        away_xg = (a_away_atk * h_home_def) * league_a_goal_avg
        
        return home_xg, away_xg

    @staticmethod
    def generate_poisson_values(xg: float) -> list[float]:
        """
        Generate and return a list of possion values from `0` goals to the model's 
        `MAX_GOAL_THRESHOLD` limit based on the given expected goals value.

        Args:
            xg (float): The expected goals of the team being evaluated.

        Returns:
            list[float]: The list of probabilities of scoring `0` to 
                `MAX_GOAL_THRESHOLD` goals.
        """
        pv = []
        
        for i in range(MAX_GOAL_THRESHOLD + 1):
            pv.append(((xg ** i) * (math.exp(-xg))) / math.factorial(i))
        
        return pv

    def poisson_prediction(self, team_ids: HomeAwayID) -> tuple[float, float, float]:
        """
        Find and return the probabilities of a win, draw, and loss.
        
        Args:
            team_ids (HomeAwayID): The ids for the teams in the current matchup.
            
        Returns:
            tuple[float, float, float]: The probabilities for a:
                - Home team win
                - Draw
                - Away team win
        """         
        h_xg, a_xg = self.expected_goals(team_ids)
        
        h_poisson_values = self.generate_poisson_values(h_xg)
        a_poisson_values = self.generate_poisson_values(a_xg)
        
        score_matrix = []
        
        for home_pvs in h_poisson_values:
            pv_row = []
            for away_pvs in a_poisson_values:
                cell = home_pvs * away_pvs
                pv_row.append(cell)
            score_matrix.append(pv_row)
        
        home_win_p, away_win_p, draw_p = 0.0, 0.0, 0.0
        
        for row in range(len(score_matrix)):
            for col in range (len(score_matrix[row])):
                if row == col: # draw
                    draw_p += score_matrix[row][col]
                elif row > col: # win
                    home_win_p += score_matrix[row][col]
                else: # loss
                    away_win_p += score_matrix[row][col]
        
        total_sum = home_win_p + away_win_p + draw_p
        
        home_win_p /= total_sum
        draw_p /= total_sum
        away_win_p /= total_sum
                    
        return home_win_p, draw_p, away_win_p
    
  
    def outcome_percentages(self, team_id: int) -> tuple[float, float, float]:
        """
        Find and return the win, loss, and draw rates for a particular team.
        
        Args:
            team_id (int): The id of team to evaluate.
            
        Returns:
            tuple[float, float, float]: The rates for a team:
                - Win
                - Loss
                - Draw
        """
        wins, losses, draws, total_matches = self.team_outcomes(team_id)
        
        if not total_matches:
            return 0.0, 0.0, 0.0
                    
        wins /= total_matches
        draws /= total_matches
        losses /= total_matches
        
        return wins, draws, losses

    def ppg(self, team_id: int) -> float:
        """
        Find and return the points per game (PPG) ratio of the given team.

        Args:
            team_id (int): The id of the team to evaluate.

        Returns:
            float: The team's PPG.
        """
        wins, _, draws, total_matches = self.team_outcomes(team_id)
        total_points = (wins * 3) + draws
        
        return total_points / total_matches

    def btts_rate(self) -> float:
        """
        Find and return the rate of both teams scoring a goal (BTTS) across all 
        competition season matches. 

        Returns:
            float: The competition season BTTS rate.
        """
        filter = select(Match).where(
            and_(
                Match.competition_id == self.competition_id,
                Match.season_id == self.season_id,
            )
        )
        matches = self.session.exec(filter).all()
        total_matches = len(matches)
        
        if not total_matches:
            return 0.0
        
        bts = 0
        
        for match in matches:
            if match.home_goals > 0 and match.away_goals > 0:
                bts += 1
                
        return bts / total_matches
      
    def over_rate(self) -> float:
        """
        Find and return the rate of over 2.5 goals being scored across all competition 
        season matches. 

        Returns:
            float: The rate of over 2.5 goals being scored.
        """
        filter = select(Match).where(
            and_(
                Match.competition_id == self.competition_id,
                Match.season_id == self.season_id
            )
        )
        matches = self.session.exec(filter).all()
        total_matches = len(matches)
        
        if not total_matches:
            return 0.0
        
        over_count = 0
        
        for match in matches:
            if match.home_goals + match.away_goals >= 3:
                over_count += 1
        
        return over_count / total_matches
        
    def league_table_stats(
        self, 
        team_id: int
    ) -> tuple[int, int, int, int, int, int, int, int]:
        """
        Calculate the given team's wins, losses, draws, points, and goal difference
        for the league table.

        Args:
            team_id (int): The id of the team to evaluate.

        Returns:
            tuple[int, int, int, int, int, int, int, int]: The following table stats:
                - Wins
                - Losses
                - Draws
                - Matches played
                - Goals for
                - Goals against
                - Goal difference
                - League points

                For the current competition season.
        """
        wins, losses, draws, total_matches = self.team_outcomes(team_id)
        
        filter = select(Match).where(
            and_(
                Match.competition_id == self.competition_id,
                Match.season_id == self.season_id,
                or_(
                    Match.home_team_id == team_id,
                    Match.away_team_id == team_id,
                ),
            )
        )
        team_matches = self.session.exec(filter).all()
        
        gf, ga = 0, 0
        for match in team_matches:
            if match.home_team_id == team_id:
                gf += match.home_goals
                ga += match.away_goals
            elif match.away_team_id == team_id:
                gf += match.away_goals
                ga += match.home_goals
        
        gd = gf - ga
        points = (wins * 3) + draws
        
        return wins, losses, draws, total_matches, gf, ga, gd, points
    
    def scoreline_chance(self, team_ids: HomeAwayID) -> tuple[int, int]:
        """
        Find and return the most likely scoreline to occur in the given matchup.

        Args:
            team_ids (HomeAwayID): The team ids in the matchup.

        Returns:
            tuple[int, int]: The most likely scoreline of the format `(0, 0)`, where 
                index `0` is the home team and index `1` is the away team.
        """
        h_xg, a_xg = self.expected_goals(team_ids)
        
        h_poisson_values = self.generate_poisson_values(h_xg)
        a_poisson_values = self.generate_poisson_values(a_xg)
        
        score_matrix = []
        
        for home_pvs in h_poisson_values:
            pv_row = []
            for away_pvs in a_poisson_values:
                cell = home_pvs * away_pvs
                pv_row.append(cell)
            score_matrix.append(pv_row)
        
        m = 0
        scoreline = (0, 0) # home - away
        for row in range(len(score_matrix)):
            for col in range(len(score_matrix[row])):
                temp = max(m, score_matrix[row][col])
                if temp > m:
                    m = temp
                    scoreline = (row, col)
                
        return scoreline
        
    def team_outcomes(self, team_id: int) -> tuple[int, int, int, int]:
        """
        Find and return the number of wins, draws, and total matches played by the
        given team in the current competition and season.

        Args:
            team_id (int): The id for the team to evaluate.

        Returns:
            tuple[int, int, int, int]: The following team stats:
                - Wins
                - Losses
                - Draws
                - Total competition season matches played
        """
        filter = select(Match).where(
            and_(
                Match.competition_id == self.competition_id,
                Match.season_id == self.season_id,
                or_(
                    Match.home_team_id == team_id,
                    Match.away_team_id == team_id,
                ),
            )
        )
        team_matches = self.session.exec(filter).all()
        total_matches = len(team_matches)
        wins, draws, losses = 0, 0, 0
        
        if not total_matches:
            return 0, 0, 0, 0
        
        for match in team_matches:
            if match.home_team_id == team_id:
                if match.home_goals > match.away_goals:
                    wins += 1
                elif match.home_goals < match.away_goals:
                    losses += 1
                else:
                    draws += 1
            elif match.away_team_id == team_id:
                if match.away_goals > match.home_goals:
                    wins += 1
                elif match.away_goals < match.home_goals:
                    losses += 1
                else:
                    draws += 1
                    
        return wins, losses, draws, total_matches
