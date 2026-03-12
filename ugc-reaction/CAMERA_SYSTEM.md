# Reaction Camera System

This note captures the missing logic for raw reaction videos.

The core rule:

`the camera is the phone`

If the phone moves, the frame moves.

## What to control explicitly

For every reaction prompt, specify:

1. `camera role`
- front-facing selfie camera
- first-person phone camera
- propped phone camera

2. `start state`
- face-down on table
- propped against books
- in hand at arm's length
- lying on bed

3. `pickup behavior`
- grabbed suddenly
- lifted slowly
- flipped from face-down
- dragged from under blanket

4. `framing`
- chest-up
- tight face close-up
- phone moved closer during reaction
- slightly imperfect crop

5. `face position`
- center
- right third
- left third
- low in frame

6. `movement style`
- tiny hand sway
- abrupt lurch on pickup
- slow drift while reading
- hard tilt while sitting up

7. `reframe logic`
- closer because phone moves closer
- wider because arm extends
- no cinematic invisible zoom

## Prompt pattern

Use a camera block before the emotional action:

```text
CAMERA LOGIC
- THE CAMERA IS THE PHONE.
- Front-facing selfie recording.
- Starts propped against books at desk level.
- When picked up, the frame rises, tilts, and settles with the hand.
- Face begins on the right third of frame.
- As the student reacts, the phone comes physically closer for a tighter face shot.
- Real handheld shake, small autofocus corrections, no cinematic stabilization.
```

## Why this matters

Without this, models often:
- keep the framing too static
- fake the phone interaction
- zoom without physical motion
- center the face too cleanly
- lose the raw feeling
