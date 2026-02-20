# CSE423_Project
Computer Graphics

# 🏎️ 3D Nitro Racing Game (PyOpenGL)

## 📌 Project Overview

This project is a fully interactive **3D racing game** developed using **PyOpenGL (OpenGL + GLUT + GLU)** in Python. The game simulates a dynamic highway racing environment with curved roads, AI-controlled opponent cars, nitro boost mechanics, weather effects, and multiple gameplay modes.

The objective varies by mode — players can compete to finish first, race against time, or explore freely — while managing speed, collisions, and resource-based nitro boosts.

The project demonstrates real-time rendering, game state management, collision detection, procedural object spawning, particle systems, and camera control using core OpenGL primitives.

---

## 🎮 Core Features

### 🚗 Player Mechanics

* Forward/backward movement with strafing
* Dynamic speed scaling
* Road-edge slowdown physics
* Collision detection with opponents
* Crash system with spark particle effects
* Reborn system (coin-based recovery)
* Invincibility window after respawn

---

### ⚡ Nitro Boost System

* Collectable nitro pickups (rotating 3D objects)
* Single-tap boost
* Double-tap boost (higher speed, higher consumption)
* Timed boost duration
* Visual flame boost effect
* Nitro resource management system

---

### 🏁 Multiple Game Modes

| Mode            | Description                                                                          |
| --------------- | ------------------------------------------------------------------------------------ |
| **Competitive** | Race against AI opponents to reach the finish line. Ranking determines coin rewards. |
| **Free Mode**   | Endless driving without finish line constraints.                                     |
| **Timed Mode**  | Race against a countdown timer. Coins can be used to extend time.                    |

---

### 🌦️ Dynamic Weather System

* **Summer** – Clear environment
* **Monsoon** – Rain particle effects
* **Winter** – Snow particle effects & visual adjustments

Weather affects:

* Sky color
* Tree appearance
* Particle rendering

---

### 🌄 Environment & Visual Effects

* Procedurally curved road using sinusoidal functions
* Infinite scrolling environment
* Recycled trees and mountains for performance optimization
* Day/Night toggle
* Headlight beam rendering at night
* Animated finish line with shimmering effect
* 3D pixel-style car models
* Particle-based rain, snow, and sparks

---

### 🎥 Camera System

* **Third-person dynamic camera**
* **First-person driving mode**
* Real-time camera transformation using `gluLookAt()`
* Perspective projection via `gluPerspective()`

---

### 🧠 Technical Implementation

#### Rendering

* Built entirely with OpenGL primitives
* Uses:

  * `glBegin(GL_QUADS)`
  * `glBegin(GL_TRIANGLES)`
  * `glutSolidCube()`
  * `gluCylinder()`
* Blending for transparency effects
* Depth testing for proper 3D rendering

#### Physics & Logic

* Trigonometric road curvature:

  ```
  x = A * sin(y / frequency)
  ```

* Distance tracking system

* Real-time collision detection using radius-based checks

* State machine-based game flow:

  * MENU
  * COUNTDOWN
  * RACING
  * CRASHED_CHOICE
  * TIMED_CHOICE
  * FINISHED

#### Optimization Techniques

* Object recycling (trees, mountains)
* Limited active nitro pickups
* Controlled opponent spawning
* Frame-based timer updates (~60 FPS logic)

---

## 🕹️ Controls

| Key   | Action                       |
| ----- | ---------------------------- |
| ↑     | Accelerate                   |
| ↓     | Brake                        |
| ← →   | Move left/right              |
| Space | Nitro Boost                  |
| V     | Toggle First/Third Person    |
| X     | Toggle Day/Night             |
| C     | Extend Time (Timed Mode)     |
| Enter | Select Menu                  |
| Y/N   | Reborn or Time Extend Choice |

---

## 💰 Coin Economy System

* Earn coins by:

  * Finishing in top positions
* Spend coins on:

  * Reborn after crash
  * Extend time in Timed mode

---

## 🏗️ Concepts Demonstrated

This project demonstrates strong understanding of:

* 3D transformations
* Perspective projection
* Camera matrices
* Real-time input handling
* Game state machines
* Procedural environment generation
* Particle systems
* Resource management mechanics
* Collision detection algorithms

---

## 📦 Technologies Used

* Python
* PyOpenGL
* GLUT
* GLU
* Mathematical modeling (Trigonometry)
* Real-time rendering techniques

---

## 🎯 Learning Outcome

This project was designed to simulate a real-time 3D racing experience using only fundamental OpenGL primitives and mathematical transformations, without using any external game engine. It highlights how low-level graphics APIs can be used to construct a complete interactive game system from scratch.



