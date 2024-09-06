mode: user.game
-

^force {user.geforce_games}$: 
    user.set_geforce_game(geforce_games)
    app.notify("Active GEForce game has been set to {geforce_games}")

^force current$: user.get_geforce_game()