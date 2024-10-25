mode: user.game
-
^man game {user.manual_games}$: 
    user.set_manual_game(manual_games)
    app.notify("Active manual game has been set to {manual_games}")

^man game current$: user.get_manual_game()