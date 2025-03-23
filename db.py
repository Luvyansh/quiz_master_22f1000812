from graphviz import Digraph

# Create a Graphviz Digraph
db_diagram = Digraph("ERD", filename="quiz_master_db", format="png")

# Define nodes (tables)
db_diagram.node("User", "User\nid (PK)\nemail (Unique, Not Null)\npassword (Not Null)\nname (Not Null)\nqualifications (Not Null)\ndob (Not Null)")
db_diagram.node("Role", "Role\nid (PK)\nname (Not Null)")
db_diagram.node("UserRoles", "UserRoles\nid (PK)\nuser_id (FK -> User.id)\nrole_id (FK -> Role.id)")

db_diagram.node("Subject", "Subject\nid (PK)\nname (Unique, Not Null)\ndescription (Nullable)")
db_diagram.node("Chapter", "Chapter\nid (PK)\nname (Unique, Not Null)\ndescription (Nullable)\nsubject_id (FK -> Subject.id)")
db_diagram.node("Quiz", "Quiz\nid (PK)\nchapter_id (FK -> Chapter.id, Unique, Not Null)\ndate_of_quiz (Not Null)\ntime_duration (Not Null)\nremarks (Nullable)")

db_diagram.node("Question", "Question\nid (PK)\nquiz_id (FK -> Quiz.id)\nquestion_statement (Not Null)\noption1 (Not Null)\noption2 (Not Null)\noption3 (Not Null)\noption4 (Not Null)\ncorrect_option (Not Null)")

db_diagram.node("Score", "Score\nid (PK)\nquiz_id (FK -> Quiz.id)\nuser_id (FK -> User.id)\ntime_stamp_of_attempt (Not Null)\ntotal_scored (Not Null)")

db_diagram.node("UserAttempt", "UserAttempt\nid (PK)\nattempt_no (Not Null)\nuser_id (FK -> User.id)\nquiz_id (FK -> Quiz.id)\nquestion_id (FK -> Question.id)\nselected_option (Nullable)\nis_correct (Not Null, Default=False)")

# Define relationships (edges)
db_diagram.edge("User", "UserRoles", label="1:N")
db_diagram.edge("Role", "UserRoles", label="1:N")
db_diagram.edge("UserRoles", "User", label="N:1")
db_diagram.edge("UserRoles", "Role", label="N:1")

db_diagram.edge("Subject", "Chapter", label="1:N")
db_diagram.edge("Chapter", "Quiz", label="1:1")
db_diagram.edge("Quiz", "Question", label="1:N")

db_diagram.edge("User", "Score", label="1:N")
db_diagram.edge("Quiz", "Score", label="1:N")
db_diagram.edge("User", "UserAttempt", label="1:N")
db_diagram.edge("Quiz", "UserAttempt", label="1:N")
db_diagram.edge("Question", "UserAttempt", label="1:N")

# Render and save the diagram
db_diagram_path = "/data/quiz_master_db.png"
db_diagram.render(db_diagram_path, format="png", cleanup=True)

db_diagram_path