from season_view.interface import read_data


# def test_construct_season_view_read_data() -> None:
#     season_view_read_data = read_data.SeasonViewReadData(
#         players=read_data.SeasonViewReadPlayers({
#             "Mickey Mouse": read_data.SeasonViewReadPlayer(
#                 name="Mickey Mouse",
#                 gender=read_data.SeasonViewPlayerGender.MALE,
#                 event_handicap_indices=read_data.SeasonViewEventHandicapIndices({
#                     "Baylands": 14.1,
#                     "Corica": 13.5,
#                 }),
#             ),
#             "Minnie Mouse": read_data.SeasonViewReadPlayer(
#                 name="Minnie Mouse",
#                 gender=read_data.SeasonViewPlayerGender.FEMALE,
#                 event_handicap_indices=read_data.SeasonViewEventHandicapIndices({
#                     "Baylands": 6.3,
#                     "Corica": 7.6,
#                 })
#             )
#         })
#     )

def test_season_view_event_handicap_indices_get_player_not_found_raises_error() -> None:
    indices = read_data.SeasonViewEventHandicapIndices(
        {"Snoopy": 12.0, "Charlie": 14.4}
    )

    indices["Snoopy"]
    indices["foobar"]