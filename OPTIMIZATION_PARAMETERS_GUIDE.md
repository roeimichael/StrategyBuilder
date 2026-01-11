# Strategy Optimization Parameters Guide

## Overview

All 12 strategies now have fully defined optimizable parameters with metadata (type, default, min, max, step, description). The API now returns this metadata when querying a strategy, allowing the frontend to dynamically build optimization forms.

## How It Works

1. **Query a strategy**: `GET /strategies/{strategy_name}` now returns `optimizable_params`
2. **Each parameter includes**:
   - `name`: Parameter name (e.g., "period")
   - `type`: "int" or "float"
   - `default`: Default value
   - `min`: Minimum recommended value
   - `max`: Maximum recommended value
   - `step`: Recommended step size for ranges
   - `description`: Human-readable explanation

3. **Frontend can dynamically**:
   - Build input fields based on parameter types
   - Suggest reasonable ranges using min/max/step
   - Validate user input
   - Generate optimization ranges automatically

---

## Complete Strategy Parameter Reference

### 1. **Bollinger Bands Strategy** (`bollinger_bands_strategy`)

Trades based on Bollinger Band breakouts and mean reversion.

**Optimizable Parameters:**
| Parameter | Type | Default | Min | Max | Step | Description |
|-----------|------|---------|-----|-----|------|-------------|
| `period` | int | 20 | 10 | 50 | 5 | Moving average period for Bollinger Bands |
| `devfactor` | float | 2.0 | 1.0 | 3.0 | 0.5 | Standard deviation multiplier |

**Example Optimization:**
```json
{
  "strategy": "bollinger_bands_strategy",
  "optimization_params": {
    "period": [15, 20, 25, 30],
    "devfactor": [1.5, 2.0, 2.5]
  }
}
```

---

### 2. **Williams %R Strategy** (`williams_r_strategy`)

Momentum oscillator identifying overbought/oversold conditions.

**Optimizable Parameters:**
| Parameter | Type | Default | Min | Max | Step | Description |
|-----------|------|---------|-----|-----|------|-------------|
| `period` | int | 14 | 5 | 30 | 2 | Lookback period for Williams %R |
| `oversold` | int | -80 | -95 | -70 | 5 | Oversold threshold (negative value) |
| `overbought` | int | -20 | -35 | -10 | 5 | Overbought threshold (negative value) |

**Example Optimization:**
```json
{
  "strategy": "williams_r_strategy",
  "optimization_params": {
    "period": [10, 14, 20],
    "oversold": [-90, -80, -70],
    "overbought": [-30, -20, -10]
  }
}
```

---

### 3. **RSI + Stochastic Strategy** (`rsi_stochastic_strategy`)

Combines RSI and Stochastic oscillators for confirmation signals.

**Optimizable Parameters:**
| Parameter | Type | Default | Min | Max | Step | Description |
|-----------|------|---------|-----|-----|------|-------------|
| `rsi_period` | int | 14 | 7 | 28 | 7 | RSI calculation period |
| `rsi_oversold` | int | 30 | 20 | 40 | 5 | RSI oversold level |
| `rsi_overbought` | int | 70 | 60 | 80 | 5 | RSI overbought level |
| `stoch_period` | int | 14 | 7 | 21 | 7 | Stochastic oscillator period |
| `stoch_oversold` | int | 20 | 10 | 30 | 5 | Stochastic oversold level |
| `stoch_overbought` | int | 80 | 70 | 90 | 5 | Stochastic overbought level |

**Example Optimization:**
```json
{
  "strategy": "rsi_stochastic_strategy",
  "optimization_params": {
    "rsi_period": [7, 14, 21],
    "rsi_oversold": [25, 30, 35],
    "rsi_overbought": [65, 70, 75]
  }
}
```

---

### 4. **Money Flow Index (MFI) Strategy** (`mfi_strategy`)

Volume-weighted momentum indicator.

**Optimizable Parameters:**
| Parameter | Type | Default | Min | Max | Step | Description |
|-----------|------|---------|-----|-----|------|-------------|
| `period` | int | 14 | 7 | 28 | 7 | Money Flow Index period |
| `oversold` | int | 20 | 10 | 30 | 5 | MFI oversold level |
| `overbought` | int | 80 | 70 | 90 | 5 | MFI overbought level |

**Example Optimization:**
```json
{
  "strategy": "mfi_strategy",
  "optimization_params": {
    "period": [7, 14, 21],
    "oversold": [15, 20, 25],
    "overbought": [75, 80, 85]
  }
}
```

---

### 5. **Keltner Channel Strategy** (`keltner_channel_strategy`)

Volatility-based channel breakout system.

**Optimizable Parameters:**
| Parameter | Type | Default | Min | Max | Step | Description |
|-----------|------|---------|-----|-----|------|-------------|
| `ema_period` | int | 20 | 10 | 40 | 5 | EMA period for centerline |
| `atr_period` | int | 10 | 5 | 20 | 5 | ATR period for channel width |
| `atr_multiplier` | float | 2.0 | 1.0 | 3.0 | 0.5 | ATR multiplier for band distance |

**Example Optimization:**
```json
{
  "strategy": "keltner_channel_strategy",
  "optimization_params": {
    "ema_period": [15, 20, 25],
    "atr_period": [10, 14, 20],
    "atr_multiplier": [1.5, 2.0, 2.5]
  }
}
```

---

### 6. **CCI + ATR Strategy** (`cci_atr_strategy`)

Combines Commodity Channel Index with ATR for volatility confirmation.

**Optimizable Parameters:**
| Parameter | Type | Default | Min | Max | Step | Description |
|-----------|------|---------|-----|-----|------|-------------|
| `cci_period` | int | 20 | 10 | 30 | 5 | CCI calculation period |
| `cci_entry` | int | -100 | -150 | -50 | 25 | CCI entry threshold |
| `cci_exit` | int | 100 | 50 | 150 | 25 | CCI exit threshold |
| `atr_period` | int | 14 | 7 | 21 | 7 | ATR period for volatility |

**Example Optimization:**
```json
{
  "strategy": "cci_atr_strategy",
  "optimization_params": {
    "cci_period": [15, 20, 25],
    "cci_entry": [-125, -100, -75],
    "cci_exit": [75, 100, 125]
  }
}
```

---

### 7. **Momentum Multi Strategy** (`momentum_multi_strategy`)

Multi-indicator momentum system using ROC, RSI, and OBV.

**Optimizable Parameters:**
| Parameter | Type | Default | Min | Max | Step | Description |
|-----------|------|---------|-----|-----|------|-------------|
| `roc_period` | int | 12 | 6 | 20 | 2 | Rate of Change period |
| `roc_threshold` | float | 2.0 | 0.5 | 5.0 | 0.5 | ROC threshold for entry signal |
| `rsi_period` | int | 14 | 7 | 21 | 7 | RSI period |
| `rsi_min` | int | 40 | 30 | 50 | 5 | Minimum RSI for entry |
| `rsi_max` | int | 60 | 50 | 70 | 5 | Maximum RSI for entry |
| `rsi_exit` | int | 70 | 60 | 80 | 5 | RSI exit threshold |

**Example Optimization:**
```json
{
  "strategy": "momentum_multi_strategy",
  "optimization_params": {
    "roc_period": [10, 12, 14],
    "roc_threshold": [1.5, 2.0, 2.5],
    "rsi_period": [10, 14, 18]
  }
}
```

---

### 8. **ADX Strategy** (`adx_strategy`)

Adaptive strategy using ADX for trend strength, with MA and Bollinger Band signals.

**Optimizable Parameters:**
| Parameter | Type | Default | Min | Max | Step | Description |
|-----------|------|---------|-----|-----|------|-------------|
| `ma_short_period` | int | 20 | 10 | 30 | 5 | Short moving average period |
| `ma_long_period` | int | 50 | 30 | 100 | 10 | Long moving average period |
| `boll_period` | int | 14 | 10 | 20 | 5 | Bollinger Bands period |
| `adx_threshold` | int | 25 | 20 | 30 | 5 | ADX threshold for trend strength |

**Example Optimization:**
```json
{
  "strategy": "adx_strategy",
  "optimization_params": {
    "ma_short_period": [15, 20, 25],
    "ma_long_period": [40, 50, 60],
    "adx_threshold": [20, 25, 30]
  }
}
```

---

### 9. **TEMA + MACD Strategy** (`tema_macd_strategy`)

Combines Triple Exponential Moving Average with MACD for trend confirmation.

**Optimizable Parameters:**
| Parameter | Type | Default | Min | Max | Step | Description |
|-----------|------|---------|-----|-----|------|-------------|
| `macd1` | int | 12 | 8 | 16 | 2 | MACD fast period |
| `macd2` | int | 26 | 20 | 30 | 2 | MACD slow period |
| `macdsig` | int | 9 | 5 | 13 | 2 | MACD signal period |
| `tema_period` | int | 12 | 8 | 20 | 4 | TEMA period |

**Example Optimization:**
```json
{
  "strategy": "tema_macd_strategy",
  "optimization_params": {
    "macd1": [10, 12, 14],
    "macd2": [24, 26, 28],
    "macdsig": [7, 9, 11]
  }
}
```

---

### 10. **TEMA Crossover Strategy** (`tema_crossover_strategy`)

Dual TEMA crossover with volume confirmation.

**Optimizable Parameters:**
| Parameter | Type | Default | Min | Max | Step | Description |
|-----------|------|---------|-----|-----|------|-------------|
| `tema_short_period` | int | 20 | 10 | 30 | 5 | Short TEMA period |
| `tema_long_period` | int | 60 | 40 | 80 | 10 | Long TEMA period |
| `volume_period` | int | 14 | 7 | 21 | 7 | Volume SMA period |

**Example Optimization:**
```json
{
  "strategy": "tema_crossover_strategy",
  "optimization_params": {
    "tema_short_period": [15, 20, 25],
    "tema_long_period": [50, 60, 70],
    "volume_period": [10, 14, 20]
  }
}
```

---

### 11. **Alligator Strategy** (`alligator_strategy`)

Bill Williams' Alligator indicator with EMA filter.

**Optimizable Parameters:**
| Parameter | Type | Default | Min | Max | Step | Description |
|-----------|------|---------|-----|-----|------|-------------|
| `lips_period` | int | 5 | 3 | 8 | 1 | Alligator lips (fastest MA) period |
| `teeth_period` | int | 8 | 5 | 13 | 2 | Alligator teeth (medium MA) period |
| `jaws_period` | int | 13 | 8 | 21 | 3 | Alligator jaws (slowest MA) period |
| `ema_period` | int | 200 | 150 | 250 | 25 | Long-term EMA filter period |

**Example Optimization:**
```json
{
  "strategy": "alligator_strategy",
  "optimization_params": {
    "lips_period": [4, 5, 6],
    "teeth_period": [7, 8, 10],
    "jaws_period": [11, 13, 16]
  }
}
```

---

### 12. **MACD + CMF + ATR Strategy** (`cmf_atr_macd_strategy`)

Advanced strategy combining MACD, Chaikin Money Flow, and ATR-based stops.

**Optimizable Parameters:**
| Parameter | Type | Default | Min | Max | Step | Description |
|-----------|------|---------|-----|-----|------|-------------|
| `macd1` | int | 12 | 8 | 16 | 2 | MACD fast period |
| `macd2` | int | 26 | 20 | 30 | 2 | MACD slow period |
| `macdsig` | int | 9 | 5 | 13 | 2 | MACD signal period |
| `atrperiod` | int | 14 | 7 | 21 | 7 | ATR period |
| `atrdist` | float | 2.0 | 1.0 | 3.0 | 0.5 | ATR distance multiplier for stops |

**Example Optimization:**
```json
{
  "strategy": "cmf_atr_macd_strategy",
  "optimization_params": {
    "macd1": [10, 12, 14],
    "macd2": [24, 26, 28],
    "atrperiod": [10, 14, 18],
    "atrdist": [1.5, 2.0, 2.5]
  }
}
```

---

## API Usage

### 1. Get Strategy Info with Optimizable Parameters

```bash
GET /strategies/bollinger_bands_strategy
```

**Response:**
```json
{
  "module": "bollinger_bands_strategy",
  "class_name": "Bollinger_three",
  "description": "",
  "parameters": {
    "period": 20,
    "devfactor": 2
  },
  "optimizable_params": [
    {
      "name": "period",
      "type": "int",
      "default": 20,
      "min": 10,
      "max": 50,
      "step": 5,
      "description": "Moving average period for Bollinger Bands"
    },
    {
      "name": "devfactor",
      "type": "float",
      "default": 2.0,
      "min": 1.0,
      "max": 3.0,
      "step": 0.5,
      "description": "Standard deviation multiplier"
    }
  ]
}
```

### 2. Run Optimization

```bash
POST /optimize
```

**Request Body:**
```json
{
  "ticker": "BTC-USD",
  "strategy": "bollinger_bands_strategy",
  "start_date": "2024-01-01",
  "end_date": "2024-12-31",
  "interval": "1d",
  "cash": 10000.0,
  "optimization_params": {
    "period": [15, 20, 25, 30],
    "devfactor": [1.5, 2.0, 2.5]
  }
}
```

---

## Frontend Integration

The frontend can now:

1. **Query strategy info** to get `optimizable_params`
2. **Dynamically generate input fields** for each parameter with appropriate types
3. **Provide smart suggestions** using min/max/step values
4. **Validate user input** against min/max ranges
5. **Generate optimization ranges** automatically (e.g., "10-30:5" → [10, 15, 20, 25, 30])

### Example Frontend Flow

```javascript
// 1. Fetch strategy info
const response = await fetch('/strategies/bollinger_bands_strategy');
const strategyInfo = await response.json();

// 2. Build form inputs dynamically
strategyInfo.optimizable_params.forEach(param => {
  if (param.type === 'int') {
    // Create integer input with step validation
  } else if (param.type === 'float') {
    // Create float input with decimal validation
  }

  // Set placeholder: "e.g., 10-30:5 or 10, 20, 30"
  // Use param.min, param.max, param.step for validation
});

// 3. Parse user input and submit optimization
const optimizationParams = parseUserInput(formData);
await fetch('/optimize', {
  method: 'POST',
  body: JSON.stringify({
    ...formData,
    optimization_params: optimizationParams
  })
});
```

---

## Summary

✅ **All 12 strategies** now have defined optimizable parameters
✅ **Metadata-driven system** allows dynamic frontend generation
✅ **Reasonable defaults** and ranges for each parameter
✅ **Type-safe** with int/float distinction
✅ **API returns** complete parameter info for any strategy

This makes the optimization feature truly **generalized** and **extensible** – adding new strategies or parameters only requires updating the configuration file!
