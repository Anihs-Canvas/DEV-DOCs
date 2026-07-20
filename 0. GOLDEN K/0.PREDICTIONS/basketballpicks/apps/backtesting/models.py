"""apps.backtesting is a SERVICE app — the settle / pnl / forward-CLV engine
(bball-01 §1). It owns no tables of its own (no migrations): settlement writes
to apps.edge's EdgePick rows, and prop_clv is pure read-side + a JobRun audit.
This empty models module keeps it a well-formed Django app.
"""
