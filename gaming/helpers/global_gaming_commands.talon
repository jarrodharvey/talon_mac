mode: user.game
-
^man game {user.manual_games}$: 
    user.set_manual_game(manual_games)
    app.notify("Active manual game has been set to {manual_games}")

^man game current$: user.get_manual_game()

^quit moonlight$: 
    key("ctrl-alt-shift-q")

^better test$: 
    user.betterinput_simple("return |500ms space |500ms space |500ms space")
