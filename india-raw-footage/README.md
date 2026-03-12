# India Raw Footage

This folder is the India raw-camera ad workshop.

It exists to help us build ads that feel like:
- real phone footage
- real Indian rooms and settings
- believable student moments
- repeatable scenes and characters when needed

## What this folder is trying to solve

Normal prompt generation can create good moments, but it often loses consistency.

This folder is our attempt to make the process more controlled by locking:
- who the character is
- what room they are in
- what kind of ad format we are making
- what the final video needs to feel like

In simple terms:

`character + setting + format + campaign brief = ad plan`

## How to think about this folder

### `characters/`
Who is in the ad.

### `settings/`
Where the ad happens.

### `formats/`
What type of ad it is.

Examples:
- confession
- reaction
- friend conversation

### `campaigns/`
The actual ad idea we are building.

### `scripts/`
The tools that turn the idea into prompts and production files.

## Why this matters

This folder is useful when we want ads that feel:
- more real
- more repeatable
- more intentional

It is especially useful for India ads where:
- raw footage matters
- room realism matters
- voice and emotion matter
- we may want to reuse the same character or scene style

## India-wide rules in this system

These rules are stored in `india_defaults.json`.

They currently include:
- duration options: `20`, `30`, `40`, `50`, `60`
- export shapes: `9:16`, `4:5`, `16:9`
- one locked India outro
- no changing the outro timing or audio
- dialogue quality is treated as a top-level requirement

## Current example

Current test campaign:
- `campaigns/kota_boy_confession_night_01/`

What it is:
- a kid-to-camera confession
- set in a Kota hostel room at night
- meant to feel like raw handheld student footage

## What gets created

When the campaign is built, this folder generates:
- a manifest for the ad
- shot-by-shot prompt files
- the production plan needed for generation and later editing

## If you are non-technical

The most useful places to open are:
- `characters/`
- `settings/`
- `formats/`
- `campaigns/`

That will tell you:
- who the ad is about
- where it happens
- what style it is
- what the final story is supposed to be
