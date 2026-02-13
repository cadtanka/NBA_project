# python3 src/manual_player_mapping.py


from src.data.analytics_queries import get_unmapped_tracking_players, insert_player_mapping

def main():
    players = get_unmapped_tracking_players()

    if not players:
        print("All players mapped!")
        return
    
    for p in players:
        print("\nTracking player:")
        print(p)

        nba_id = input("Enter NBA player_id:")
        name = input("Enter player name:")

        insert_player_mapping(
            tracking_id=p["id"],
            nba_id=int(nba_id),
            name=name,
        )

        print("Saved!")

if __name__ == "__main__":
    main()