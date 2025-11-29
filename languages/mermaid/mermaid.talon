code.language: mermaid
-
# Enable relevant shared command sets
tag(): user.code_comment_line

# Start new diagrams (uses .talon-list)
new {user.mermaid_diagram_type.list}: "{mermaid_diagram_type}\n"

# Flowchart nodes (uses .talon-list)
node <user.text> {user.mermaid_node_shape.list}:
    text = user.formatted_text(text, "SNAKE_CASE")
    insert("{text}{mermaid_node_shape}")

# Arrows and connections (uses .talon-list)
{user.mermaid_arrow.list}: "{mermaid_arrow} "

# Common sequences for sequence diagrams
participant <user.text>:
    text = user.formatted_text(text, "CAPITALIZE_FIRST_WORD")
    insert("participant {text}\n")

activate <user.text>:
    text = user.formatted_text(text, "CAPITALIZE_FIRST_WORD")
    insert("activate {text}\n")

deactivate <user.text>:
    text = user.formatted_text(text, "CAPITALIZE_FIRST_WORD")
    insert("deactivate {text}\n")

# Subgraphs
sub graph <user.text>:
    text = user.formatted_text(text, "CAPITALIZE_FIRST_WORD")
    insert("subgraph {text}\n")

graph end: "end\n"
