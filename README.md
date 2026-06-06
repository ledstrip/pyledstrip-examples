# pyledstrip-examples

A collection of Python implementation examples and lighting effects built using the `pyledstrip` client library. These scripts demonstrate how to stream color data over UDP to WS2812/WS2812b LED strips.

## Table of Contents
- [Overview of Examples](#overview-of-examples)
- [Common Arguments](#common-arguments)
- [Usage Examples](#usage-examples)
- [Experimental Features](#experimental-features)
- [License](#license)

---

## Overview of Examples

| Script | Description |
| :--- | :--- |
| **`boomerangs.py`** | Spawns multiple light pulses that travel down the strip, bounce off the boundaries, and cross paths. |
| **`disco.py`** | A flashing stroboscopic party light animation using random color palettes. |
| **`fireworks.py`** | Simulates a realistic fireworks show: rocket launch, fuse burning, particle explosion, gravity acceleration, and decay. |
| **`mod.py`** | Uses modular arithmetic to project shifting patterns of color blocks across the strip. |
| **`noise.py`** | Renders smooth, Perlin-like 1D noise transitions for fluid organic color shifts. |
| **`off.py`** | A simple utility to turn off all LEDs on the strip. |
| **`rainbow.py`** | A slowly rolling, custom-calibrated rainbow. Uses specific RGB points to counteract unequal LED dye intensities. |
| **`sines.py`** | Superimposes multiple sine waves with different frequencies and phase-shifts to create shifting wave gradients. |
| **`smooth.py`** | Smoothly interpolates and fades transitions between random colors. |
| **`snake.py`** | A classic snake segment that crawls along the LED strip, reflecting or wrapping around boundaries. |
| **`static_pattern.py`** | Fills the strip with a static, non-moving color pattern. |
| **`walker.py`** | A random walk particle that leaves behind a fading trail of light. |

---

## Common Arguments

All scripts use `pyledstrip`'s command line argument parser. The most common parameters include:

- `--host HOST`: (Required) IP address or hostname of the LED strip controller (e.g., an ESP8266 or piledstrip-server).
- `--port PORT`: UDP port of the controller (default is `7777`).
- `--leds LED_COUNT`: Total number of LEDs on the strip (default: `300`).
- `--power_limit POWER_LIMIT`: Power limit factor between `0.0` and `1.0` to restrict current draw (default: `0.2`).
- `--brightness BRIGHTNESS`: Overall brightness multiplier (0.0 to 1.0).

---

## Usage Examples

Run a script by providing the target host and LED count:

```bash
# Run the calibrated rainbow animation
python3 rainbow.py --host 192.168.1.50 --leds 450

# Run the fireworks simulation
python3 fireworks.py --host 192.168.1.50 --leds 300

# Turn all LEDs off
python3 off.py --host 192.168.1.50 --leds 300
```

---

## Experimental Features

The `experiments/` directory contains more advanced or specialized scripts:

### 1. Lamprecht (`experiments/lamprecht/`)
- Contains custom installation-specific scripts: `LamprechtEins.py` and `LamprechtZwo.py` which define complex layered behaviors.

### 2. Physics (`experiments/physics/`)
- **`gradient.py`**: Visualizes physics gradients on the strip.
- **`show_heightmap.py`** & **`plot_heightmap.py`**: Utilities to read and inspect/display 2D heightmap JSONs.

### 3. Sound-reactive (`experiments/sound/`)
- **`vu_meter.py`**: A sound-reactive volume unit (VU) meter showing audio amplitude.
- **`amplitude.py`**: Monitors microphone/audio input amplitude.
- **`record.py`**: Records audio signals to help calibrate sound-reactive parameters.

*Note: Sound-reactive scripts require audio input libraries such as `pyaudio` or `sounddevice`.*

---

## License

This project is open-source. See the `LICENSE` file for details (MPL-2.0).
