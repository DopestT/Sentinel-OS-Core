"""Focused tests for the integrated SolanaAlpha signal."""

from agents.crypto_sniper import CryptoSniperAgent, MarketSnapshot


def _snapshot(signal: str) -> MarketSnapshot:
    return MarketSnapshot(
        symbol="SOL",
        price=95.0,
        volume_24h=20_000_000,
        btc_trend="sideways",
        rsi=30.0,
        ma_fast=96.0,
        ma_slow=100.0,
        bb_lower=96.0,
        bb_middle=100.0,
        bb_upper=104.0,
        atr=2.0,
        solana_alpha_signal=signal,
        volatility_score=30.0,
        sentiment_score=50.0,
        whale_risk_score=30.0,
        timestamp="2026-07-28T00:00:00",
    )


def test_solana_alpha_waits_for_indicator_warmup():
    agent = CryptoSniperAgent(symbol="SOL")
    agent.price_history = [100.0] * 19

    assert agent._solana_alpha_signal(95.0, 30.0, 96.0, 104.0) == "warmup"


def test_solana_alpha_emits_entry_and_exit_signals():
    agent = CryptoSniperAgent(symbol="SOL")
    agent.price_history = [100.0] * 20

    assert agent._solana_alpha_signal(95.0, 30.0, 96.0, 104.0) == "enter_long"
    assert agent._solana_alpha_signal(105.0, 50.0, 96.0, 104.0) == "exit_long"
    assert agent._solana_alpha_signal(100.0, 75.0, 96.0, 104.0) == "exit_long"


def test_solana_alpha_entry_can_drive_paper_trade_decision():
    agent = CryptoSniperAgent(symbol="SOL")
    scores = agent.score_strategies(_snapshot("enter_long"))

    alpha = next(score for score in scores if score.name == "solana_alpha")
    assert alpha.score == 85
    assert alpha.signal == "strong"
    assert agent.build_paper_decision(_snapshot("enter_long"), scores)["decision"] == "paper_trade"


def test_bollinger_bands_and_atr_are_derived_from_price_history():
    agent = CryptoSniperAgent(symbol="SOL")
    agent.price_history = [100.0] * 20

    assert agent._bollinger_bands() == (100.0, 100.0, 100.0)
    assert agent._estimate_atr() == 0.0
