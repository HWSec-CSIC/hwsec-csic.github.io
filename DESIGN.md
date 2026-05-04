---
name: Sapphire Precision
colors:
  surface: '#0b1326'
  surface-dim: '#0b1326'
  surface-bright: '#31394d'
  surface-container-lowest: '#060e20'
  surface-container-low: '#131b2e'
  surface-container: '#171f33'
  surface-container-high: '#222a3d'
  surface-container-highest: '#2d3449'
  on-surface: '#dae2fd'
  on-surface-variant: '#c2c7d1'
  inverse-surface: '#dae2fd'
  inverse-on-surface: '#283044'
  outline: '#8c919a'
  outline-variant: '#42474f'
  surface-tint: '#a0c9ff'
  primary: '#a0c9ff'
  on-primary: '#00325a'
  primary-container: '#0f4c81'
  on-primary-container: '#8ebdf9'
  inverse-primary: '#2d6197'
  secondary: '#4edea3'
  on-secondary: '#003824'
  secondary-container: '#00a572'
  on-secondary-container: '#00311f'
  tertiary: '#adc6ff'
  on-tertiary: '#002e6a'
  tertiary-container: '#00479c'
  on-tertiary-container: '#9abaff'
  error: '#ffb4ab'
  on-error: '#690005'
  error-container: '#93000a'
  on-error-container: '#ffdad6'
  primary-fixed: '#d2e4ff'
  primary-fixed-dim: '#a0c9ff'
  on-primary-fixed: '#001c37'
  on-primary-fixed-variant: '#07497d'
  secondary-fixed: '#6ffbbe'
  secondary-fixed-dim: '#4edea3'
  on-secondary-fixed: '#002113'
  on-secondary-fixed-variant: '#005236'
  tertiary-fixed: '#d8e2ff'
  tertiary-fixed-dim: '#adc6ff'
  on-tertiary-fixed: '#001a42'
  on-tertiary-fixed-variant: '#004395'
  background: '#0b1326'
  on-background: '#dae2fd'
  surface-variant: '#2d3449'
typography:
  display-xl:
    fontFamily: Space Grotesk
    fontSize: 48px
    fontWeight: '700'
    lineHeight: '1.1'
  headline-lg:
    fontFamily: Space Grotesk
    fontSize: 32px
    fontWeight: '600'
    lineHeight: '1.2'
  headline-md:
    fontFamily: Space Grotesk
    fontSize: 24px
    fontWeight: '500'
    lineHeight: '1.3'
  body-lg:
    fontFamily: Space Grotesk
    fontSize: 18px
    fontWeight: '400'
    lineHeight: '1.6'
  body-md:
    fontFamily: Space Grotesk
    fontSize: 16px
    fontWeight: '400'
    lineHeight: '1.5'
  label-sm:
    fontFamily: Space Grotesk
    fontSize: 13px
    fontWeight: '600'
    lineHeight: '1.0'
    letterSpacing: 0.05em
  mono-data:
    fontFamily: Space Grotesk
    fontSize: 14px
    fontWeight: '400'
    lineHeight: '1.4'
rounded:
  sm: 0.125rem
  DEFAULT: 0.25rem
  md: 0.375rem
  lg: 0.5rem
  xl: 0.75rem
  full: 9999px
spacing:
  base: 4px
  xs: 0.5rem
  sm: 1rem
  md: 1.5rem
  lg: 2.5rem
  xl: 4rem
  gutter: 24px
  margin: 32px
---

## Brand & Style

The design system moves away from sterile monochrome environments toward a high-fidelity, high-trust aesthetic tailored for hardware security and forensic analysis. The brand personality is authoritative, technical, and luminous. It targets research engineers and security architects who require data density without sacrificing visual clarity.

The chosen style is **Corporate Modern with Luminous Accents**. It utilizes a dark-mode foundation to reduce eye strain during long research sessions, punctuated by vibrant jewel-toned interactive elements. This approach creates a clear hierarchy where data is neutral, but the system's "intelligence" (actions, statuses, and navigation) is expressed through rich color.

## Colors

The palette is anchored by a deep Sapphire Blue, used for primary actions and active navigation states. This is complemented by an Emerald Green that serves as both a secondary brand identifier and a semantic indicator for successful security checks and verified hardware components.

- **Primary (Sapphire):** Used for main CTAs, active sidebar icons, and primary selection states.
- **Secondary (Emerald):** Reserved for "Safe" states, secondary badges, and success-oriented micro-interactions.
- **Surface & Backgrounds:** We utilize a rich Navy-Slate (`#0F172A`) rather than pure black to maintain depth and allow for sophisticated layering.
- **UI Borders:** Key containers use a low-opacity Sapphire stroke to reinforce the brand identity without overwhelming the content.

## Typography

This design system leverages **Space Grotesk** across all touchpoints to maintain its technical, futuristic character. The geometric nature of the font pairs perfectly with hardware schematics and code-heavy interfaces.

- **Headlines:** Use tighter tracking and heavier weights to establish a "hard-tech" look.
- **Body:** Generous line heights are applied to ensure legibility during data-dense analysis.
- **Labels:** Uppercase styling is frequently used for metadata labels and badge text to provide a clear distinction from narrative content.

## Layout & Spacing

The system follows a **12-column fluid grid** designed for large-format laboratory monitors. To accommodate complex hardware diagnostic tools, the layout prioritizes side-by-side comparisons.

- **Sidebar:** A fixed-width navigation rail (72px collapsed, 240px expanded) sits on the left, utilizing Sapphire highlights for active states.
- **Modules:** Content is organized into modular cards separated by 24px gutters.
- **Padding:** Internal card padding is set to `md` (1.5rem) to ensure technical data does not feel cramped, maintaining a clean, professional "breathing room."

## Elevation & Depth

Hierarchy is established through **Tonal Layering** and **Sapphire Accents** rather than traditional heavy shadows.

- **Level 0 (Background):** The darkest slate foundation.
- **Level 1 (Cards/Panels):** A slightly lighter navy with a 1px Sapphire-tinted border (10% opacity).
- **Level 2 (Modals/Popovers):** Higher contrast backgrounds with a subtle blue outer glow (4px blur, 5% opacity) to simulate the illumination of hardware LEDs.
- **Active States:** Interactive elements like buttons and selected inputs utilize a "inner-glow" effect using the primary Sapphire color to indicate focus.

## Shapes

The design system utilizes **Soft** roundedness (`0.25rem` base) to strike a balance between industrial hardware aesthetics and modern software usability.

- **Buttons & Inputs:** Use the standard 4px radius for a precise, "machined" look.
- **Badges:** Maintain the same 4px radius; avoid pill shapes to keep the system feeling more technical and less consumer-oriented.
- **Key UI Borders:** Card containers use the `rounded-lg` (0.5rem) setting to distinguish the primary workspace from smaller utility elements.

## Components

### Buttons
Primary buttons are solid Deep Sapphire (`#0F4C81`) with white text. Secondary buttons use a Sapphire outline with a subtle hover fill. Success-oriented actions (e.g., "Deploy Fix") utilize the Emerald Green.

### Badges & Status Indicators
Badges are used extensively for hardware health. "Pass/Verified" badges use a soft Emerald background with dark Emerald text. "Critical" states use a vibrant Ruby (only where necessary), while "Active/Running" states use a Sapphire pulse animation.

### Navigation Highlights
The navigation sidebar uses a vertical Sapphire bar (4px wide) on the left edge of the active menu item, accompanied by a low-opacity Sapphire background tint.

### Data Inputs
Inputs feature a dark background with a 1px border. On focus, the border transitions to a vibrant Sapphire blue with a subtle outer glow, mimicking a powered-on hardware interface.

### Cards
Cards are the primary container. They feature a 1px border in a muted sapphire-slate tone. For "Highlighted Research," the top border of the card is thickened to 3px and colored in vibrant Emerald.