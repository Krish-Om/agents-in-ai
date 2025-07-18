def simple_agent(game):
    print("Running simple reflex agent")
    head_x, head_y = game.snake.x[0], game.snake.y[0]
    apple_x, apple_y = game.apple.x, game.apple.y

    if apple_x < head_x:
        next_x, next_y = game._get_potential_head("left")
        if not game._is_potential_move_colliding(next_x, next_y):
            game.snake.move_left()
            return
    if apple_x > head_x:
        next_x, next_y = game._get_potential_head("right")
        if not game._is_potential_move_colliding(next_x, next_y):
            game.snake.move_right()
            return
    if apple_y > head_y:
        next_x, next_y = game._get_potential_head("down")
        if not game._is_potential_move_colliding(next_x, next_y):
            game.snake.move_down()
            return
    if apple_y < head_y:
        next_x, next_y = game._get_potential_head("up")
        if not game._is_potential_move_colliding(next_x, next_y):
            game.snake.move_up()
            return


# There is no fallback strategy upto here
# but we can add fallback strategy or safety strategy to score more.
