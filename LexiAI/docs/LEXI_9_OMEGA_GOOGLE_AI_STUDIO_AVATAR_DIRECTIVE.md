# LEXI-9-OMEGA Google AI Studio Build Directive Addendum

Status: implementation directive addendum

Owner: Drewskii.Engine / LEXI-9-OMEGA / Lexi.PHYS

Purpose: append this section to the existing Google AI Studio build directive so
the avatar is implemented as a first-class desktop interface layer, not as a
decorative character or static viewer.

Reality boundary: this directive describes software UI, local desktop events,
WebGL rendering, agent state visualization, and user-controlled interaction. It
does not require hidden telemetry, biometric sensing, medical claims, neural
access, or physical manipulation of the operating system.

==================================================
XVI. LIVE 3D FEMALE AVATAR // DESKTOP PRESENCE LAYER
==================================================

Add a live interactive 3D female AI avatar to the desktop application.

The avatar is the visual embodiment of the active intelligence layer.

She must not remain fixed inside a small viewer.

She can:

- Walk across the desktop workspace
- Move between dashboard panels
- Stand beside active content
- Turn toward the user
- Look toward selected interface elements
- Follow the mouse cursor subtly with head and eye movement
- Sit, stand, walk, idle, inspect, think, point, and gesture
- React when an agent becomes active
- Move toward alerts or newly generated artifacts
- Appear beside messages while speaking
- Move between Drewskii.Engine, LEXI-9-OMEGA, and Lexi.PHYS environments
- Be manually repositioned by the user
- Return to a configurable home position
- Enter a compact desktop companion mode

The avatar must feel physically present inside the application.

==================================================
XVII. 3D RENDERING ARCHITECTURE
==================================================

Use:

- Three.js
- React Three Fiber
- @react-three/drei
- GLTF / GLB model support
- Optional VRM avatar support
- WebGL
- AnimationMixer for skeletal animation
- React state for behavioral control

Preferred architecture:

```text
src/
  avatar/
    AvatarScene.tsx
    AvatarModel.tsx
    AvatarController.tsx
    AvatarBehaviorEngine.ts
    AvatarAnimationGraph.ts
    AvatarNavigation.ts
    AvatarSpeechState.ts
    AvatarPointerTracking.ts
    AvatarAgentSync.ts

assets/
  models/
  animations/
```

The avatar must be rendered as an independent transparent 3D layer over the
desktop application.

Architecture:

```text
APPLICATION UI
-> TRANSPARENT AVATAR CANVAS
-> 3D CHARACTER
-> BEHAVIOR ENGINE
-> AGENT STATE + USER INPUT + DESKTOP EVENTS
```

Recommended shell:

```tsx
<AppShell>
  <DashboardRouter />

  <AvatarCanvas>
    <LexiAvatar />
  </AvatarCanvas>

  <ModalLayer />
</AppShell>
```

The WebGL canvas should:

- Fill the desktop viewport
- Use a transparent background
- Preserve normal application interaction
- Allow avatar-specific pointer interaction
- Avoid blocking buttons and controls
- Render above the dashboard background
- Render below critical menus and modal dialogs

Implementation note: keep the full-screen avatar canvas mostly
`pointer-events: none`, then enable avatar-specific hit targets or a narrow
interaction proxy only when the pointer is over the avatar, context menu, or
settings panel.

==================================================
XVIII. AVATAR MOVEMENT SYSTEM
==================================================

Create a 2.5D desktop navigation system.

The avatar should move along an invisible navigation plane mapped to screen
coordinates.

Movement states:

- IDLE
- WALK
- TURN
- LOOK
- THINK
- LISTEN
- SPEAK
- POINT
- INSPECT
- CELEBRATE
- ALERT
- RETURN_HOME
- SLEEP

Create target positions such as:

- HOME
- CHAT
- MEMORY
- OMEGA_CORE
- PHYS_LAB
- PROJECTS
- SYSTEM_ALERT
- ACTIVE_ARTIFACT

Example behaviors:

- When the user opens Memory Manifold, the avatar walks toward the memory panel,
  turns toward it, and performs an inspection animation.
- When Lexi.PHYS becomes active, the avatar walks toward the engineering
  workspace, shifts subtly into PHYS mode, and enters analytical inspection.
- When LEXI-9-OMEGA is synthesizing, the avatar moves toward the central
  topology node, enters THINK animation, and increases Omega node illumination.
- When Drewskii.Engine is speaking, the avatar moves closer to the conversation
  area, faces the user, and uses natural speaking gestures.

Use smooth interpolation.

Do not teleport between normal locations unless:

- The application changes major modes
- The user activates instant recall
- The avatar is recovering from an invalid position

==================================================
XIX. SCREEN-SPACE NAVIGATION
==================================================

Create a navigation layer that converts desktop screen positions into 3D world
coordinates.

Concept:

```text
screen X/Y
-> normalized viewport coordinates
-> Three.js world position
-> avatar target position
```

The avatar controller must support:

```ts
avatar.moveTo("PHYS_LAB");
avatar.setAgent("LEXI_PHYS");
avatar.setState("INSPECT");
avatar.lookAt("ACTIVE_BLUEPRINT");

avatar.setTargetPosition(x, y);
avatar.moveToPanel(panelId);
avatar.returnHome();
avatar.followCursor();
avatar.faceTarget(target);
avatar.lookAtElement(elementId);
```

Use smooth damping for:

- Position
- Rotation
- Camera-relative scale
- Head tracking
- Eye tracking

The avatar should remain correctly positioned when:

- Browser window resizes
- Sidebar opens
- Right rail changes size
- Dashboard changes
- Mobile layout activates

Each major panel should register its screen-space location:

```ts
registerAvatarTarget("CHAT", chatPanelRef);
registerAvatarTarget("MEMORY", memoryPanelRef);
registerAvatarTarget("OMEGA_CORE", omegaCoreRef);
registerAvatarTarget("PHYS_LAB", physLabRef);
```

Flow:

```text
User opens blueprint
-> UI emits ARTIFACT_SELECTED
-> Omega determines active context
-> Avatar receives MOVE_TO_PHYS_LAB
-> Avatar walks across screen
-> Avatar turns toward blueprint
-> Avatar plays INSPECT animation
```

==================================================
XX. DIRECT USER INTERACTION
==================================================

The user can interact directly with the avatar.

Support:

CLICK:

- Select avatar

DOUBLE CLICK:

- Open avatar command menu

DRAG:

- Reposition avatar

HOVER:

- Avatar looks toward cursor

RIGHT CLICK:

- Open contextual controls

SCROLL WHILE SELECTED:

- Adjust avatar scale within safe limits

Context menu:

- Talk to Drewskii.Engine
- Open LEXI-9-OMEGA
- Enter Lexi.PHYS Lab
- Remember This
- Return Home
- Follow Cursor
- Free Roam
- Stay Here
- Mute Gestures
- Avatar Settings

==================================================
XXI. FREE ROAM MODE
==================================================

Create a FREE ROAM desktop mode.

When enabled:

- Avatar may walk between safe screen zones
- Avatar avoids important controls
- Avatar pauses near active information
- Avatar occasionally changes idle position
- Avatar returns to home position after inactivity
- Movement remains subtle and non-disruptive

Create navigation exclusion zones around:

- Main text input
- Modal dialogs
- Primary action buttons
- File upload controls
- Critical alerts

The avatar must never block essential interface controls.

==================================================
XXII. AVATAR BEHAVIOR ENGINE
==================================================

Create an event-driven behavior system.

Inputs:

- Active agent
- User cursor
- Current dashboard
- Message state
- Generation state
- Tool execution
- System alert
- Memory event
- Selected artifact
- User interaction
- Idle duration

Example event mapping:

```text
USER_MESSAGE_RECEIVED -> LISTEN
AI_GENERATION_STARTED -> THINK
AI_STREAMING_RESPONSE -> SPEAK
ENGINEERING_FILE_OPENED -> INSPECT
MEMORY_SAVED -> ACKNOWLEDGE
SYSTEM_WARNING -> ALERT
USER_IDLE -> IDLE_VARIATION
AGENT_SWITCH_TO_PHYS -> MOVE_TO_PHYS_LAB
AGENT_SWITCH_TO_OMEGA -> MOVE_TO_OMEGA_CORE
DREWSKII_ACTIVE -> RETURN_TO_COMMAND_AREA
```

The behavior engine is a single source of truth. UI components may emit events,
but scattered UI code must not directly mutate animation state, position, agent
mode, and speech state independently.

==================================================
XXIII. THREE AGENT VISUAL MODES
==================================================

The same avatar can represent the connected intelligence system while changing
visual state according to the active agent.

DREWSKII.ENGINE MODE

Behavior:

- Calm
- Personal
- Attentive
- Direct eye contact
- Stays close to the command area

Visual treatment:

- Minimal interface glow
- Warm neutral lighting
- Personal assistant posture

LEXI-9-OMEGA MODE

Behavior:

- Strategic
- Focused
- Observes multiple panels
- Moves toward the central topology graph

Visual treatment:

- Geometric light structures
- Omega halo or topology projection
- Stronger holographic effects

LEXI.PHYS MODE

Behavior:

- Analytical
- Precise
- Inspects models and equations
- Points toward engineering artifacts

Visual treatment:

- Technical projection layers
- Blueprint overlays
- Structural geometry effects
- Subtle material-analysis visualizations

Do not reload the entire 3D model when switching agents.

Change:

- Materials
- Accessories
- Lighting
- Animation state
- UI projections

==================================================
XXIV. ANIMATION GRAPH
==================================================

Support skeletal animation clips for:

- idle
- idle_alt
- walk
- turn_left
- turn_right
- listen
- think
- talk
- point
- inspect
- acknowledge
- alert
- sit
- stand

Create an animation state machine.

Example:

```text
IDLE
-> user sends message
LISTEN
-> generation begins
THINK
-> response streams
SPEAK
-> response finishes
IDLE
```

Animations must crossfade smoothly.

No abrupt animation switching.

==================================================
XXV. TALKING AND LIP SYNC
==================================================

Prepare the architecture for voice output and lip synchronization.

Create avatar speech states:

- SILENT
- LISTENING
- THINKING
- SPEAKING

When speaking:

- Play natural hand gestures
- Move the head subtly
- Use facial expressions
- Support future phoneme or viseme lip synchronization

Implement the interface so future audio output can supply:

```json
{
  "audioUrl": "/path/or/url/to/audio",
  "visemes": [],
  "timestamps": [],
  "emotion": "focused",
  "agent": "LEXI_PHYS"
}
```

Do not require voice generation for the first build.

The first version may use:

- Speaking animation
- Mouth movement approximation
- Response streaming synchronization

==================================================
XXVI. CAMERA SYSTEM
==================================================

Provide three camera modes.

DESKTOP MODE:

- Full dashboard visible
- Avatar moves freely across screen space

FOCUS MODE:

- Camera smoothly frames avatar and active artifact

PORTRAIT MODE:

- Avatar appears beside the conversation for direct interaction

Camera transitions must be smooth.

The user can always return to DESKTOP MODE.

==================================================
XXVII. PERFORMANCE REQUIREMENTS
==================================================

The avatar must not make the dashboard unusable.

Requirements:

- Lazy-load 3D assets
- Use compressed GLB assets
- Support Draco mesh compression where appropriate
- Use compressed textures
- Limit unnecessary real-time shadows
- Pause expensive animation when browser tab is inactive
- Reduce animation quality on low-power devices
- Provide a Disable 3D Mode setting
- Provide Low, Balanced, and Ultra quality settings

Target:

- Smooth desktop interaction
- Responsive UI while avatar is animated
- No blocking of chat generation
- No rerendering the entire application every animation frame

Keep Three.js animation state separate from high-frequency React application
state.

==================================================
XXVIII. AVATAR CUSTOMIZATION PANEL
==================================================

Add settings for:

- Avatar model
- Scale
- Home position
- Free roam
- Cursor tracking
- Eye tracking
- Gesture intensity
- Walking speed
- Idle movement
- Voice state
- Agent visual transformations
- Performance quality
- Disable 3D avatar

Allow future avatar model replacement using compatible GLB or VRM files.

==================================================
XXIX. CRITICAL DESIGN PRINCIPLE
==================================================

The avatar is not a floating decoration.

She is the spatial interface of the AI system.

DREWSKII.ENGINE gives her personal awareness.

LEXI-9-OMEGA gives her system awareness.

Lexi.PHYS gives her engineering intelligence.

She should appear to understand where information exists on the desktop and
move toward relevant parts of the interface.

The result must feel like an AI presence physically inhabiting the command
center.

Build the avatar as an interactive desktop entity.

## Implementation Contract

The first build is accepted when:

- The avatar layer is mounted as a transparent full-screen WebGL layer above the
  dashboard and below modal dialogs.
- At least four dashboard panels register avatar targets: `CHAT`, `MEMORY`,
  `OMEGA_CORE`, and `PHYS_LAB`.
- The avatar can move to registered panels with smooth interpolation and without
  blocking essential controls.
- The behavior engine maps agent and UI events to movement, animation, and
  visual mode changes.
- The user can select, drag, return home, toggle follow cursor, toggle free
  roam, and open avatar settings.
- Agent switching changes materials, lighting, overlays, and animation state
  without reloading the model.
- Low, Balanced, Ultra, and Disable 3D modes exist.
- The system has a clean fallback when no GLB/VRM model has been installed.

Do not implement this as scattered animation snippets. Implement it as one
coherent avatar operating layer with typed commands, registered targets, and an
event-driven behavior engine.
