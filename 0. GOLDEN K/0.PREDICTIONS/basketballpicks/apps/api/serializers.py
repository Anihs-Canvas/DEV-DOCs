"""DRF serializers for /api/v1 [bball-01 §1: api = DRF v1 read surface].

Plain `serializers.Serializer` subclasses with EXPLICIT field lists (never
`__all__`) so the API contract is pinned by tests, not model drift — and so
this module imports cleanly without a hard dependency on the props/edge model
classes (they are read off the ORM instances at serialize time). PAPER-ONLY,
read-only: nothing here writes.
"""

from rest_framework import serializers


class PredictionSerializer(serializers.Serializer):
    """One team-market CORE prediction row (predictions.Prediction)."""

    game_id = serializers.IntegerField(read_only=True)
    fixture = serializers.SerializerMethodField()
    league = serializers.CharField(source="game.season.league.code", read_only=True)
    tipoff_utc = serializers.DateTimeField(source="game.tipoff_utc", read_only=True)
    model_version = serializers.CharField(source="model_version.name", read_only=True)
    market = serializers.CharField(read_only=True)
    prob_vector = serializers.JSONField(read_only=True)

    def get_fixture(self, obj) -> str:
        g = obj.game
        return f"{g.away_team.abbreviation} @ {g.home_team.abbreviation}"


class PropPredictionSerializer(serializers.Serializer):
    """One player-prop projection (predictions.PropPrediction). `calibration_gate`
    is the honest flag: False = noise market, devig/display only, never our edge."""

    game_id = serializers.IntegerField(read_only=True)
    player = serializers.CharField(source="player.canonical_name", read_only=True)
    market_key = serializers.CharField(read_only=True)
    proj_minutes = serializers.DecimalField(max_digits=6, decimal_places=2, read_only=True)
    mean = serializers.DecimalField(max_digits=7, decimal_places=3, read_only=True)
    dist = serializers.CharField(read_only=True)
    calibration_gate = serializers.BooleanField(read_only=True)
    model_version = serializers.CharField(source="model_version.name", read_only=True)


class PropLineSerializer(serializers.Serializer):
    """One book's two-sided quote (props.PropLine). DFS legs carry
    over/under_price=None and a payout_mult instead."""

    book = serializers.CharField(source="bookmaker.name", read_only=True)
    is_dfs = serializers.BooleanField(source="bookmaker.is_dfs", read_only=True)
    market_key = serializers.CharField(source="market.key", read_only=True)
    player = serializers.CharField(source="player.canonical_name", read_only=True)
    line = serializers.DecimalField(max_digits=6, decimal_places=2, read_only=True)
    over_price = serializers.DecimalField(
        max_digits=8, decimal_places=3, read_only=True, allow_null=True
    )
    under_price = serializers.DecimalField(
        max_digits=8, decimal_places=3, read_only=True, allow_null=True
    )
    payout_mult = serializers.DecimalField(
        max_digits=6, decimal_places=3, read_only=True, allow_null=True
    )
    is_closing = serializers.BooleanField(read_only=True)
    captured_at = serializers.DateTimeField(read_only=True)


class PropConsensusSerializer(serializers.Serializer):
    """The devigged sharp/consensus fair benchmark (props.PropConsensus)."""

    market_key = serializers.CharField(source="market.key", read_only=True)
    player = serializers.CharField(source="player.canonical_name", read_only=True)
    line = serializers.DecimalField(max_digits=6, decimal_places=2, read_only=True)
    fair_prob_over = serializers.DecimalField(max_digits=6, decimal_places=5, read_only=True)
    anchor = serializers.CharField(read_only=True)
    is_closing = serializers.BooleanField(read_only=True)
    captured_at = serializers.DateTimeField(read_only=True)


class EdgePickSerializer(serializers.Serializer):
    """One published +EV pick (edge.EdgePick). DEVIG-CENTRIC: the benchmark is
    the sharp-fair prob, model_prob is a secondary (often null) input."""

    id = serializers.IntegerField(read_only=True)
    cell = serializers.CharField(read_only=True)
    venue = serializers.CharField(read_only=True)
    league = serializers.SerializerMethodField()
    fixture = serializers.SerializerMethodField()
    player = serializers.SerializerMethodField()
    book = serializers.SerializerMethodField()
    market_key = serializers.CharField(read_only=True)
    side = serializers.CharField(read_only=True)
    line = serializers.DecimalField(max_digits=6, decimal_places=2, read_only=True, allow_null=True)
    sharp_fair_prob = serializers.DecimalField(max_digits=6, decimal_places=5, read_only=True)
    book_implied_devig = serializers.DecimalField(
        max_digits=6, decimal_places=5, read_only=True, allow_null=True
    )
    model_prob = serializers.DecimalField(
        max_digits=6, decimal_places=5, read_only=True, allow_null=True
    )
    edge = serializers.DecimalField(max_digits=7, decimal_places=5, read_only=True)
    ev = serializers.DecimalField(max_digits=7, decimal_places=5, read_only=True)
    min_acceptable_price = serializers.DecimalField(
        max_digits=6, decimal_places=3, read_only=True, allow_null=True
    )
    status = serializers.CharField(read_only=True)
    published_at = serializers.DateTimeField(read_only=True)
    expires_at = serializers.DateTimeField(read_only=True)

    def _game(self, obj):
        if obj.prop_line_id:
            return obj.prop_line.game
        if obj.odds_snapshot_id:
            return obj.odds_snapshot.game
        return None

    def get_league(self, obj):
        g = self._game(obj)
        return g.season.league.code if g else None

    def get_fixture(self, obj):
        g = self._game(obj)
        return f"{g.away_team.abbreviation} @ {g.home_team.abbreviation}" if g else None

    def get_player(self, obj):
        return obj.prop_line.player.canonical_name if obj.prop_line_id else None

    def get_book(self, obj):
        if obj.prop_line_id:
            return obj.prop_line.bookmaker.name
        if obj.odds_snapshot_id:
            return obj.odds_snapshot.bookmaker.name
        return None
