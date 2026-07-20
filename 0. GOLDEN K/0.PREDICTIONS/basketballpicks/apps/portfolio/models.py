"""portfolio — Bankroll/Bet (singles) + DFSEntry (pick'em parlays) [bball-01 §2].

STUB owned by the portfolio agent. Add here:
  * Bankroll (copy safepicks verbatim — paper only until a gate)
  * Bet      (copy safepicks; retarget pick FK -> edge.EdgePick; add PUSH pnl)
  * DFSEntry (NEW — a 2-6 correlated-leg pick'em entry, fixed payout multiplier,
              capped stake; legs = M2M to edge.EdgePick; power|flex; correlation
              managed at build time; status OPEN|WON|PARTIAL|LOST|VOID)
Import EdgePick from apps.edge.models once it lands.
"""

from django.db import models  # noqa: F401  (import kept so the app is migration-ready)
