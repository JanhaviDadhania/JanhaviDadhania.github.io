---
title: "how to send a small satellite to the moon and take photos"
date: 2026-04-02
tags: []
summary: "A practical guide to doing one of the hardest things humans have ever attempted — but in miniature."
draft: false
meta:
  on_coffee: true
  is_finished: true
  opinion_strength: 6
  evidence_strength: 8
---

*A practical guide to doing one of the hardest things humans have ever attempted — but in miniature.*

## Why this is actually possible now

Ten years ago, sending anything to the Moon was the exclusive domain of nation-states with billion-dollar budgets. That's changed. CubeSats — standardized small satellites — have become so capable that NASA flew two of them (WALL-E and EVE, officially the MarCO mission) past Mars in 2018. In 2022, Japan's OMOTENASHI attempted a lunar landing from a 6U CubeSat. It didn't fully work, but it almost did. The hardware, the launch options, and the knowledge are all more accessible than ever.

What follows is what it would actually take to build a small satellite, get it to the Moon, put it in orbit, and beam photos back to your laptop.

## Part 1: Mission design — what are you actually trying to do?

Before touching hardware, you need a mission concept. The Moon is ~384,400 km away on average (it varies between 356,500 km at perigee and 406,700 km at apogee — the Moon's orbit is notably eccentric). Getting there is not a straight shot. You're essentially threading a gravitational needle.

For a small satellite mission, the most realistic goal is **lunar flyby** or **lunar orbit** — not landing. Landing is brutally hard and mass-intensive. Orbit is hard enough.

**Key decisions up front:**

- **Form factor**: A 6U CubeSat (10×20×30 cm, ~14 kg max) is the sweet spot. Big enough to carry meaningful propulsion and a camera. Small enough to hitch a ride affordably.
- **Primary objective**: Imaging. You want a camera payload that can photograph the lunar surface from orbit.
- **Mission duration**: 3 to 6 months in lunar orbit is realistic before attitude control propellant runs out.
- **Data return**: You'll need a ground station or access to a deep space network.

## Part 2: The spacecraft — building your CubeSat

A 6U lunar CubeSat has roughly this mass budget:

| Subsystem | Mass |
|---|---|
| Structure | ~1.5 kg |
| Power (solar panels + battery) | ~2 kg |
| Propulsion | ~4 kg (including propellant) |
| Communications | ~1 kg |
| ADCS (attitude control) | ~1 kg |
| Camera payload | ~1 kg |
| On-board computer | ~0.5 kg |
| Margins | ~2.5 kg |
| **Total** | **~14 kg** |

### Propulsion

This is the hardest part. To get from Earth orbit to the Moon, you need to perform a **trans-lunar injection (TLI)** burn — roughly **3.1 km/s of delta-v** if you're launching from low Earth orbit. Then you need **lunar orbit insertion (LOI)** — about **0.9 km/s** to slow down enough for the Moon to capture you. Total: ~4 km/s.

That's an enormous amount of delta-v for a small satellite. The Tsiolkovsky rocket equation makes this painfully clear: to get 4 km/s with a 10 kg dry mass, even with a high-efficiency thruster (Isp ~220s, like a monopropellant hydrazine system), you'd need over 50 kg of propellant. That's way over budget.

**The solution used by real missions: rideshare + high-energy launch.**

NASA's Artemis 1 (2022) carried 10 CubeSats as secondary payloads. The rocket (SLS) provided the TLI burn for free. The CubeSats only needed enough propulsion for small trajectory corrections and LOI. This is the realistic path: your satellite hitches a ride on a rocket already going to the Moon, so you inherit most of the delta-v from the launch vehicle.

For LOI alone (~0.9 km/s), a 6U CubeSat with a solid motor or a small monopropellant thruster can manage this with ~4 to 6 kg of propellant. Tight but doable.

### Power

At lunar distance, solar panels produce about 1,360 W/m² (roughly the same as near Earth — the Sun is far enough that the Moon's distance doesn't matter much relative to Earth's). A 6U CubeSat can deploy ~0.1 m² of solar panels, yielding ~60 to 80W. Combined with a lithium-ion battery pack (~30 Wh), you have enough power to run the spacecraft through lunar eclipses (which can last up to 4 hours when the Moon passes through Earth's shadow).

### Attitude control

You need to know which way you're pointing — always. At the Moon, you can't rely on GPS. You use:

- **Star trackers**: cameras pointed at stars, cross-referenced against a catalog to determine orientation. Accurate to <0.01°.
- **Reaction wheels**: spinning flywheels that transfer angular momentum to rotate the spacecraft.
- **Sun sensors**: cheap, simple backup.

## Part 3: The launch — getting off Earth

You have two realistic options:

**Option A: Rideshare on a commercial rocket.** SpaceX's Transporter missions (Falcon 9) offer CubeSat rides to low Earth orbit for ~$5,500/kg. But LEO is only the start — you still need to get from LEO to the Moon yourself.

**Option B: Rideshare on a lunar-bound mission.** This is the golden ticket. NASA's CLPS (Commercial Lunar Payload Services) program and similar initiatives sometimes offer CubeSat slots on lunar missions. You get TLI for free. The catch: you don't control the timeline and must meet the primary mission's requirements.

For timeline planning: a typical procurement and launch cycle for a secondary payload is **2 to 4 years** from contract to launch. Budget accordingly.

## Part 4: The journey — trans-lunar trajectory

Once separated from the launch vehicle, your satellite is in **trans-lunar injection** — a highly elliptical orbit whose apogee reaches the Moon's distance.

**The numbers:**

- TLI burn: performed at low Earth orbit (~400 km altitude)
- Coast phase: **3 to 5 days** to reach the Moon
- Distance traveled: ~386,000 km along the trajectory arc
- Velocity at TLI: ~10.9 km/s (relative to Earth)
- Velocity when arriving at Moon: slowed to ~0.8 to 1.0 km/s relative to the Moon

During the coast, you're essentially in freefall. The spacecraft needs to:

- Maintain communication with Earth (already 1+ light-second away by day 2)
- Perform small **trajectory correction maneuvers (TCMs)** — tiny burns of just a few m/s to refine the path
- Monitor health, power, and thermal state

The Moon's gravity starts to dominate at the **Hill sphere boundary**, roughly 60,000 km from the Moon.

## Part 5: Lunar orbit insertion — the critical burn

This is the most nail-biting moment. If the LOI burn fails, you fly past the Moon and are lost in heliocentric space. There's no second chance.

**LOI burn parameters (for a 100 km circular polar orbit):**

- Required delta-v: ~0.9 km/s
- Burn duration: depends on thruster thrust level. At 22 N thrust (typical small monopropellant), burning ~4 kg of hydrazine takes about 3 to 4 minutes.
- Timing: must occur at the precise moment of closest approach (periselene)

The burn happens on the far side of the Moon — out of contact with Earth. You programmed the maneuver in advance and your computer executes it autonomously. You find out if it worked ~45 minutes later when the spacecraft re-emerges from behind the Moon.

**Target orbit:** 100 km circular polar orbit is ideal for surface imaging. Polar orbit ensures that as the Moon rotates slowly beneath you (one rotation every 27.3 days), you eventually image the entire surface.

Orbital period at 100 km: ~2 hours. In 27 days you'd complete ~324 orbits and image nearly the full surface.

## Part 6: The camera — your eyes at the Moon

A 100 km altitude and modest camera can yield impressive results. Here's how the math works:

**Ground Sampling Distance (GSD)** — the size of one pixel on the surface:

```
GSD = (altitude × pixel_size) / focal_length
```

With a 1/2.3" CMOS sensor (like a Sony IMX258, 4208×3120 pixels, 1.12 µm pixel size) and a 50 mm focal length:

```
GSD = (100,000 m × 0.00000112 m) / 0.050 m = 2.24 m/pixel
```

That means each pixel covers a 2.24m × 2.24m patch of the Moon. You'd clearly see large boulders, craters down to ~10m diameter, and the terrain in beautiful detail.

**Camera data volume:**

- One image: 4208 × 3120 × 3 bytes = ~39 MB (raw)
- With lossless compression: ~10 to 15 MB
- At 100 orbits per day imaging 10 frames per orbit: ~10 to 15 GB/day uncompressed

You can't transmit all of that. You'll select the best frames and downlink a subset.

**Thermal considerations:** The lunar surface swings between +127°C in sunlight and -173°C in shadow. Your camera's electronics need a thermal enclosure — multi-layer insulation (MLI) blankets and heaters keep it in the −20°C to +50°C operating range.

## Part 7: Transmitting photos back to Earth

At 384,400 km, radio waves take **1.28 seconds** to travel one way. Communication is manageable but the link budget is tight.

**The link budget (how much data you can send):**

Radio signals follow the inverse-square law — power falls off with distance squared. From the Moon:

```
Free space path loss (at 8 GHz, 384,400 km) ≈ 212 dB
```

That's a staggering loss. You compensate with:

- **Transmit power**: 5 to 10 W on the spacecraft
- **High-gain antenna**: a small patch or horn antenna with 15 to 20 dBi gain
- **Ground station dish**: a 5 to 10m dish with a low-noise amplifier

A realistic link might achieve **10 to 100 kbps** downlink data rate. At 100 kbps and 8 hours of contact per day:

```
Daily downlink: 100,000 bits/s × 8 × 3600 s = 2.88 Gbits = 360 MB/day
```

That's ~25 compressed images per day at 15 MB each. Not a firehose, but enough to tell a story.

**Ground station options:**

- Build your own small dish (feasible for a university team)
- Lease time on commercial deep space networks (Atlas Space Operations, Leaf Space)
- Apply for time on NASA's Deep Space Network (DSN) — free for approved missions, but competitive

## Part 8: Operations and what you'll see

Once in orbit and downlinking data, you'll see things like this:

- **Craters**: The Moon has over 5,000 named craters. From 100 km at 2m/pixel resolution, small craters appear as crisp circles with raised rims and central peaks.
- **Mare regions**: The vast dark basaltic plains (ancient lava flows) that make up the Man in the Moon's "face."
- **Highlands**: The bright, heavily cratered ancient crust.
- **Terminator**: The day/night boundary where shadows are long and topography jumps out in stark relief. The most dramatic images always come from near the terminator.
- **Apollo landing sites**: At 2m/pixel you can actually resolve the descent stages and equipment left behind by Apollo missions.

Your operations team (which could be 3 to 5 people) monitors spacecraft health, plans imaging targets, commands the satellite, and processes downlinked images. The satellite autonomously handles safe-mode responses if something goes wrong.

## The real numbers summary

| Parameter | Value |
|---|---|
| Earth–Moon distance (avg) | 384,400 km |
| Transit time | 3 to 5 days |
| TLI delta-v | ~3.1 km/s (provided by launch vehicle) |
| LOI delta-v | ~0.9 km/s (spacecraft provides) |
| Orbital altitude | 100 km |
| Orbital period | ~2 hours |
| Image resolution | ~2 m/pixel |
| Downlink rate | 10 to 100 kbps |
| Mission cost (small team) | $5M to $30M total |
| Timeline | 3 to 7 years from start to data |

## The honest bottom line

This is hard. Missions fail — propulsion anomalies, software bugs, radiation upsets, thermal surprises. Of the ~130 lunar missions launched since 1958, a significant fraction failed. But the ones that work are extraordinary.

The fact that a team of engineers with a few million dollars and a lot of determination can now seriously attempt this — that's one of the most remarkable things about the era we live in. The Moon isn't just for superpowers anymore.

If you're serious: start with a CubeSat in low Earth orbit. Learn the spacecraft bus, the ground station, the operations. Then look at what CAPSTONE, LunIR, and ArgoMoon achieved as 6U CubeSats in lunar space. They are your proof that it's possible.

The Moon is waiting.

---

*Written for dreamers who like real numbers.*
