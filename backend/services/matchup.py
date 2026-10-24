from datetime import date
from sqlalchemy.orm import selectinload
from sqlmodel import and_, col, or_, select

from backend.api.models import Match
from backend.services.base import BaseService, HomeAwayID
from backend.services.prediction import PredictionEngine
from backend.services.team import TeamService

class MatchupService(BaseService):
    
    def get_match_by_id(self, match_id: int):
        statement = (
            select(Match)
            .where(
                Match.id == match_id,
                Match.competition_id == self.competition_id,
                Match.season_id == self.season_id,
            )
            .options(
                selectinload(Match.home_team), # type: ignore
                selectinload(Match.away_team), # type: ignore
            )
        )
        
        return self.session.exec(statement).first()
    
    def get_h2h_matches(
        self, home_team_id: int, away_team_id: int, before_date: date, limit: int = 5
    ):
        statement = (
            select(Match).where(
                or_(
                    and_(
                        Match.home_team_id == home_team_id, 
                        Match.away_team_id == away_team_id
                    ),
                    and_(
                        Match.home_team_id == away_team_id, 
                        Match.away_team_id == home_team_id
                    ),
                ),
                Match.date < before_date,
            )
            .options(
                selectinload(Match.home_team), # type: ignore
                selectinload(Match.away_team), # type: ignore
            )
            .order_by(col(Match.date).desc())
            .limit(limit)
        )
        
        return list(self.session.exec(statement).all())
    
    def get_recent_form(self, team_id: int, before_date: date, limit: int = 5):
        statement = (
            select(Match).where(
                or_(Match.home_team_id == team_id, Match.away_team_id == team_id),
                Match.date < before_date
            )
            .options(
                selectinload(Match.home_team), # type: ignore
                selectinload(Match.away_team), # type: ignore
            )
            .order_by(col(Match.date).desc())
            .limit(limit)
        )
        
        return list(self.session.exec(statement).all())
    
    def generate_matchup_profile(self, match_id: int):
        match = self.get_match_by_id(match_id)
        
        if not match:
            return None 
        
        teams = HomeAwayID(
            home_team_id=match.home_team_id, away_team_id=match.away_team_id
        )
        
        prediction_engine = PredictionEngine(
            self.session, self.competition_id, self.season_id
        )
        predictions = prediction_engine.generate_matchup_prediction(
            teams, matchweek=match.matchweek
        )
        
        h2h = self.get_h2h_matches(
            match.home_team_id, match.away_team_id, before_date=match.date
        )
        home_form = self.get_recent_form(match.home_team_id, before_date=match.date)
        away_form = self.get_recent_form(match.away_team_id, before_date=match.date)

        team_service = TeamService(self.session, self.competition_id, self.season_id)
        hh_atk, hh_def, ha_atk, ha_def = team_service.team_strengths(
            match.home_team_id, up_to_mw=match.matchweek
        )
        ah_atk, ah_def, aa_atk, aa_def = team_service.team_strengths(
            match.away_team_id, up_to_mw=match.matchweek
        )
        
        return {
            'match': match,
            'predictions': predictions,
            'h2h_matches': h2h,
            'home_recent_form': home_form,
            'away_recent_form': away_form,
            'home_strengths': {
                'home_attack': hh_atk, 
                'home_defense': hh_def,
                'away_attack': ha_atk,
                'away_defense': ha_def,
            },
            'away_strengths': {
                'home_attack': ah_atk,
                'home_defense': ah_def,
                'away_attack': aa_atk,
                'away_defense': aa_def,
            },
        }
