app: vscode
-

settings():
    user.context_sensitive_dictation = false

key <phrase>:
    insert('key("')
    insert(phrase)
    insert('")')

key <user.letter>:
    insert('key("')
    insert(letter)
    insert('")')

sleep <number>:
    insert('sleep(')
    insert(number)
    insert('s)')

nap <number>:
    insert('sleep(')
    insert(number)
    insert('ms)')

croc <phrase>: insert("^{phrase}$: ")