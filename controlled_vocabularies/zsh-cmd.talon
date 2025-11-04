app: Terminal
-

shell {user.zsh_cmd}+:
    joined = user.join_spaces(zsh_cmd_list)
    insert(joined)
    key("space")