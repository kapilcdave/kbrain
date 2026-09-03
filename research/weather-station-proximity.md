---
title: Weather Station Proximity and the Tarmac Effect
type: research
status: completed
started: 2026
updated: 2026-09-03
tags: [weather, microclimate, weather-stations, airports, falsification]
source_repositories:
  - "private:weather"
---

# Weather Station Proximity and the Tarmac Effect

## Thesis

Weather contracts settle on one exact observation station, often at an airport.
That sensor can experience a different thermal regime from the surrounding
city. Asphalt, runways, parking areas, marine-layer boundaries, wind direction,
and aircraft activity could create a station-local temperature basis that a
regional forecast or market distribution misses.

The actionable version of the thesis was:

> If the settlement station becomes unusually hot relative to fixed nearby
> stations, its daily maximum may finish in a higher bucket than a regional
> forecast implies.

This was never one experiment. It produced several increasingly specific tests
with different outcomes.

## Why Proximity Matters

A market resolves from the named station, not from a city-wide average. Nearby
stations can therefore be predictors but cannot replace the settlement sensor.
A physically local mechanism also requires the actual sensor location. An
airport reference point or runway midpoint is not a valid substitute when the
hypothesis depends on what lies immediately upwind of the instrument.

## Station-Hot Test

The strongest discovery rule came from Los Angeles International Airport. It
required a strong morning temperature ramp and a settlement-station maximum at
least one degree Fahrenheit above the mean of three fixed neighboring stations.
The trade expressed the view that the nearest lower temperature bucket had
become less likely.

Discovery looked compelling:

- 23 simulated entries;
- 19 wins and 4 losses;
- positive results after a one-cent adverse-fill buffer and fee stress.

The rule was then frozen and applied to non-overlapping dates. An initial report
was underpowered because an archive-loader defect hid many valid triggers. After
repair, the primary out-of-time result was:

- 14 entries;
- 7 wins and 7 losses;
- negative after the registered one-cent execution stress;
- negative in both chronological halves;
- five of six frozen promotion gates failed.

**Verdict:** the exact station-hot trading rule was falsified. Its planned
forward extension was not promoted.

## SFO Microclimate Tests

San Francisco supplied a related coastal mechanism: marine-layer depth,
stratus movement through the San Bruno Gap, pressure gradients, and KSFO's
temperature relative to nearby airport stations.

Two concrete specifications failed their later evaluation periods:

- A frozen early-morning marine-versus-dry rule was approximately flat overall
  and lost heavily in its final chronological segment.
- A KSFO-minus-neighbor rule was positive in discovery but reversed sharply in
  the evaluation segment.

**Verdict:** the tested SFO expressions were selection or regime effects, not a
stable edge.

## Wind-Aligned Thermal Footprint

A preregistered model attempted to represent paved-airport heating more
directly. It combined runway orientation, trailing solar input, wind speed, and
wind direction into a coarse thermal-footprint proxy.

The test included an important negative control: wind direction was shuffled
within station, month, and local hour. The real feature produced only a tiny
Brier-score change, and the shuffled feature reproduced nearly all of it.
Classification accuracy and temperature error did not improve.

**Verdict:** the coarse runway-aligned proxy was killed before opening its
holdout. It did not isolate a directional tarmac effect.

## Aircraft and Upwind-Boundary Branches

Two more physical versions were designed but could not be evaluated:

- A satellite-and-neighbor test for a thermal or cloud boundary approaching
  the sensor from upwind.
- An aircraft/taxiway-plume test under sunny, light-wind conditions, with
  downwind and time-shuffled controls.

The available archive lacked the required satellite files, verified sensor
coordinates, and usable aircraft partitions. Using generic airport coordinates
would have invalidated the near-sensor premise, so no substitute model was fit.

**Verdict:** these mechanisms are unresolved, not positive and not falsified.
There is no market or trading result for either branch.

## Separate Finding: Station-Level Bias

Settlement series did show statistically persistent differences in market
calibration across time. That finding does not establish tarmac heating as the
cause. Attempts to turn the estimated station bias into a trade were
non-monotone and fragile to a small adverse fill.

## Final Assessment

- **Falsified:** the exact Los Angeles station-hot rule.
- **Rejected:** the tested San Francisco microclimate and neighbor rules.
- **Killed by control:** the coarse runway-aligned thermal proxy.
- **Unresolved physically:** sensor-centered land-cover heating, approaching
  local boundaries, and aircraft exhaust effects measured with the correct
  coordinates and causal data.
- **Established but distinct:** station-level calibration differences existed,
  but their physical cause was unidentified and their tested trading expression
  was uneconomic.

The broad lesson is methodological: the closer a hypothesis gets to a physical
sensor, the less defensible a geographic proxy becomes. A tarmac-effect test
needs the actual sensor, the actual upwind surface, causal weather observations,
and an untouched evaluation window.
