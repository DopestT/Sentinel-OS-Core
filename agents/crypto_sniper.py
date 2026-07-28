"""
Crypto Sniper Agent

Month-1 mission: watch LUNC, build multi-signal market context, score strategies,
and paper-trade only. No real execution lives in this agent.
"""
import asyncio
import math
import random
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Dict, List, Optional


@dataclass
class MarketSnapshot:
    symbol: str
    price: float
    volume_24h: float
    btc_trend: str
    rsi: float
    ma_fast: float
    ma_slow: float
    bb_lower: float
    bb_middle: float
    bb_upper: float
    atr: float
    solana_alpha_signal: str
    volatility_score: float
    sentiment_score: float
    whale_risk_score: float
    timestamp: str


@dataclass
class StrategyScore:
    name: str
    score: float
    signal: str
    reason: str


class CryptoSniperAgent:
    def __init__(self, symbol: str = "LUNC"):
        self.symbol = symbol
        self.price_history: List[float] = []
        self.paper_trades: List[Dict] = []
        self.strategy_history: Dict[str, List[float]] = {
            "momentum_breakout": [],
            "dip_buy": [],
            "volume_spike": [],
            "btc_follow": [],
            "solana_alpha": [],
            "no_trade": [],
        }

    async def fetch_market_snapshot(self) -> MarketSnapshot:
        """
        Fetch or simulate market data.
        Replace the mock section with live exchange APIs once deployment is stable.
        """
        await asyncio.sleep(0.25)

        last_price = self.price_history[-1] if self.price_history else 0.00010
        drift = random.uniform(-0.000003, 0.000003)
        price = max(last_price + drift, 0.000001)
        self.price_history.append(price)
        self.price_history = self.price_history[-200:]

        ma_fast = self._moving_average(9)
        ma_slow = self._moving_average(21)
        rsi = self._estimate_rsi()
        volatility = self._estimate_volatility()
        bb_lower, bb_middle, bb_upper = self._bollinger_bands()
        atr = self._estimate_atr()
        solana_alpha_signal = self._solana_alpha_signal(
            price=price,
            rsi=rsi,
            bb_lower=bb_lower,
            bb_upper=bb_upper,
        )

        return MarketSnapshot(
            symbol=self.symbol,
            price=price,
            volume_24h=random.uniform(2_000_000, 25_000_000),
            btc_trend=random.choice(["up", "sideways", "down"]),
            rsi=rsi,
            ma_fast=ma_fast,
            ma_slow=ma_slow,
            bb_lower=bb_lower,
            bb_middle=bb_middle,
            bb_upper=bb_upper,
            atr=atr,
            solana_alpha_signal=solana_alpha_signal,
            volatility_score=volatility,
            sentiment_score=random.uniform(35, 75),
            whale_risk_score=random.uniform(10, 85),
            timestamp=datetime.utcnow().isoformat(),
        )

    def score_strategies(self, snapshot: MarketSnapshot) -> List[StrategyScore]:
        scores = []

        momentum_score = 50
        if snapshot.ma_fast > snapshot.ma_slow:
            momentum_score += 15
        if snapshot.rsi > 55:
            momentum_score += 10
        if snapshot.volume_24h > 10_000_000:
            momentum_score += 10
        if snapshot.whale_risk_score > 70:
            momentum_score -= 20
        scores.append(StrategyScore(
            "momentum_breakout",
            self._clamp(momentum_score),
            self._signal(momentum_score),
            "Fast trend, RSI, volume, and whale-risk weighted together.",
        ))

        dip_score = 45
        if snapshot.rsi < 35:
            dip_score += 25
        if snapshot.btc_trend != "down":
            dip_score += 10
        if snapshot.volatility_score > 75:
            dip_score -= 15
        scores.append(StrategyScore(
            "dip_buy",
            self._clamp(dip_score),
            self._signal(dip_score),
            "Looks for oversold LUNC conditions without heavy BTC pressure.",
        ))

        volume_score = 40
        if snapshot.volume_24h > 15_000_000:
            volume_score += 25
        if snapshot.rsi < 72:
            volume_score += 10
        if snapshot.whale_risk_score > 65:
            volume_score -= 15
        scores.append(StrategyScore(
            "volume_spike",
            self._clamp(volume_score),
            self._signal(volume_score),
            "Scores volume expansion while penalizing crowded/whale-risk conditions.",
        ))

        btc_score = 40
        if snapshot.btc_trend == "up":
            btc_score += 25
        elif snapshot.btc_trend == "down":
            btc_score -= 25
        if snapshot.ma_fast > snapshot.ma_slow:
            btc_score += 10
        scores.append(StrategyScore(
            "btc_follow",
            self._clamp(btc_score),
            self._signal(btc_score),
            "Checks whether the configured asset should follow Bitcoin direction.",
        ))

        alpha_scores = {
            "enter_long": 85,
            "hold": 45,
            "exit_long": 15,
            "warmup": 20,
        }
        alpha_score = alpha_scores[snapshot.solana_alpha_signal]
        scores.append(StrategyScore(
            "solana_alpha",
            self._clamp(alpha_score),
            self._signal(alpha_score),
            (
                "RSI/Bollinger mean-reversion signal: "
                f"{snapshot.solana_alpha_signal}; ATR {snapshot.atr:.8f}."
            ),
        ))

        no_trade_score = 30
        if snapshot.whale_risk_score > 70:
            no_trade_score += 25
        if snapshot.volatility_score > 80:
            no_trade_score += 20
        if snapshot.btc_trend == "down" and snapshot.rsi > 60:
            no_trade_score += 15
        scores.append(StrategyScore(
            "no_trade",
            self._clamp(no_trade_score),
            self._signal(no_trade_score),
            "Rewards patience when risk, volatility, or bad market alignment is high.",
        ))

        for item in scores:
            self.strategy_history[item.name].append(item.score)
            self.strategy_history[item.name] = self.strategy_history[item.name][-500:]

        return sorted(scores, key=lambda item: item.score, reverse=True)

    def build_paper_decision(self, snapshot: MarketSnapshot, scores: List[StrategyScore]) -> Dict:
        top = scores[0]
        decision = "watch"

        if top.name == "no_trade" and top.score >= 60:
            decision = "do_nothing"
        elif top.score >= 75:
            decision = "paper_trade"
        elif top.score >= 60:
            decision = "alert_only"

        record = {
            "timestamp": snapshot.timestamp,
            "symbol": snapshot.symbol,
            "price": snapshot.price,
            "decision": decision,
            "top_strategy": asdict(top),
            "all_scores": [asdict(score) for score in scores],
        }

        if decision == "paper_trade":
            self.paper_trades.append(record)
            self.paper_trades = self.paper_trades[-500:]

        return record

    async def execute(self) -> Dict:
        snapshot = await self.fetch_market_snapshot()
        scores = self.score_strategies(snapshot)
        decision = self.build_paper_decision(snapshot, scores)

        return {
            "snapshot": asdict(snapshot),
            "decision": decision,
            "paper_trade_count": len(self.paper_trades),
            "best_strategy_now": scores[0].name,
            "best_strategy_score": scores[0].score,
        }

    def _moving_average(self, window: int) -> float:
        if not self.price_history:
            return 0.0
        sample = self.price_history[-window:]
        return sum(sample) / len(sample)

    def _estimate_rsi(self, window: int = 14) -> float:
        if len(self.price_history) < 2:
            return 50.0

        changes = [self.price_history[i] - self.price_history[i - 1] for i in range(1, len(self.price_history))]
        recent = changes[-window:]
        gains = sum(change for change in recent if change > 0)
        losses = abs(sum(change for change in recent if change < 0))

        if losses == 0:
            return 70.0

        rs = gains / losses
        return 100 - (100 / (1 + rs))

    def _estimate_volatility(self, window: int = 21) -> float:
        sample = self.price_history[-window:]
        if len(sample) < 2:
            return 20.0

        avg = sum(sample) / len(sample)
        variance = sum((price - avg) ** 2 for price in sample) / len(sample)
        normalized = math.sqrt(variance) / avg if avg else 0
        return self._clamp(normalized * 10_000)

    def _bollinger_bands(
        self, window: int = 20, deviations: float = 2.0
    ) -> tuple[float, float, float]:
        """Return lower, middle, and upper bands for the available closes."""
        if not self.price_history:
            return 0.0, 0.0, 0.0

        sample = self.price_history[-window:]
        middle = sum(sample) / len(sample)
        variance = sum((price - middle) ** 2 for price in sample) / len(sample)
        standard_deviation = math.sqrt(variance)
        return (
            middle - deviations * standard_deviation,
            middle,
            middle + deviations * standard_deviation,
        )

    def _estimate_atr(self, window: int = 14) -> float:
        """Estimate ATR from closes until OHLC candles replace simulated data."""
        sample = self.price_history[-(window + 1):]
        if len(sample) < 2:
            return 0.0

        true_ranges = [
            abs(sample[index] - sample[index - 1])
            for index in range(1, len(sample))
        ]
        return sum(true_ranges) / len(true_ranges)

    def _solana_alpha_signal(
        self,
        price: float,
        rsi: float,
        bb_lower: float,
        bb_upper: float,
        minimum_candles: int = 20,
    ) -> str:
        """Apply SolanaAlpha entry and exit conditions to the current snapshot."""
        if len(self.price_history) < minimum_candles:
            return "warmup"
        if rsi < 35 and price < bb_lower:
            return "enter_long"
        if rsi > 70 or price > bb_upper:
            return "exit_long"
        return "hold"

    @staticmethod
    def _clamp(value: float) -> float:
        return round(max(0, min(100, value)), 2)

    @staticmethod
    def _signal(score: float) -> str:
        if score >= 75:
            return "strong"
        if score >= 60:
            return "watch"
        if score >= 40:
            return "weak"
        return "ignore"
