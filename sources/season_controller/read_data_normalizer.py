from season_common.scorecard import (
    IncompleteScorecard,
    Scorecard,
)
from season_view import (
    SeasonViewReadData,
    SeasonViewReadEvent,
    SeasonViewReadEvents,
)


class SeasonReadDataNormalizer:
    def __init__(self, read_data: SeasonViewReadData, log_normalizations: bool = False) -> None:
        self._read_data = read_data
        self._logs_enabled = log_normalizations

    def normalize(self) -> SeasonViewReadData:
        normalized_events: list[SeasonViewReadEvent] = []
        for event in self._read_data.events.values():
            normalized_events.append(self.normalize_event(event=event))

        events = SeasonViewReadEvents({event.event_name: event for event in normalized_events})
        return SeasonViewReadData(players=self._read_data.players, events=events)

    def normalize_event(self, event: SeasonViewReadEvent) -> SeasonViewReadEvent:
        player_scorecards: dict[str, Scorecard] = {}
        for player in event.player_names:
            player_scorecards[player] = self.normalize_player_scorecard(player=player, event=event)

        return SeasonViewReadEvent(
            event_name=event.event_name,
            player_scorecards=player_scorecards,
        )

    def normalize_player_scorecard(self, player: str, event: SeasonViewReadEvent) -> Scorecard:
        scorecard = event.player_scorecard(player=player)
        if scorecard.is_complete_score():
            if not self._read_data.is_handicap_available(player_name=player, event_name=event.event_name):
                self._log(
                    f"Found a complete scorecard for {player} in event {event.event_name}, but no handicap was "
                    "found. This score will be skipped."
                )
                return IncompleteScorecard()

        return scorecard

    def _log(self, message: str) -> None:
        if self._logs_enabled:
            print(message)
