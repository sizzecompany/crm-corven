# Design System Document

## 1. Overview & Creative North Star: "The Kinetic Curator"

This design system is engineered to transform the standard CRM experience into a high-end, editorial-grade workspace. Our Creative North Star is **"The Kinetic Curator."** It rejects the static, boxy nature of traditional SaaS in favor of a fluid, high-velocity aesthetic that feels both authoritative and accessible.

We break the "template" look through:
- **Intentional Asymmetry:** Leveraging whitespace to guide the eye, rather than filling every pixel.
- **Micro-Tonal Contrast:** Using neon accents against soft, slate-toned surfaces to create a sense of focused energy.
- **Squircle Geometry:** Softening the "high-tech" edge with organic, heavily rounded corners (rounded-3xl) to maintain a friendly, approachable persona.

---

## 2. Colors & Surface Philosophy

The color palette is a sophisticated interplay between "Hyper-Visibility" (Neon) and "Atmospheric Depth" (Slate/Gray).

### The Primary Palette
- **Primary (`#526600` / `primary_container: #d3ff1a`):** Our signature neon lime. This is a high-energy tool used for primary actions and critical highlights.
- **Surface (`#f9f9f9`):** The canvas. A clean, sophisticated light slate that prevents the "clinical white" fatigue.
- **On-Surface (`#1a1c1c` / `slate-900`):** Pure, high-contrast legibility for all primary editorial content.

### The "No-Line" Rule
**Explicit Instruction:** Designers are prohibited from using 1px solid borders for sectioning. Boundaries must be defined solely through background color shifts or subtle tonal transitions.
*   Instead of a border, place a `surface_container_lowest` (#ffffff) card on top of a `surface_container` (#eeeeee) background.

### The "Glass & Gradient" Rule
To elevate beyond a "flat" SaaS aesthetic:
- **Floating Elements:** Use semi-transparent surface colors with a `backdrop-blur-xl` effect.
- **Signature Textures:** For Hero CTAs and primary buttons, use a subtle linear gradient transitioning from `primary_fixed` (#c8f300) to `primary` (#526600). This provides "soul" and depth that flat hex codes cannot achieve.

---

## 3. Typography: Editorial Authority

We use **Inter** as our typographic workhorse. The system relies on dramatic scale shifts to create a hierarchy that feels like a premium digital magazine.

- **Display (lg/md):** 3.5rem - 2.75rem. Bold, tight letter-spacing. Used for "Big Truth" statements and hero headers.
- **Headline (lg/md/sm):** 2rem - 1.5rem. Used to define major feature sections.
- **Body (lg/md):** 1rem - 0.875rem. Optimized for long-form CRM data entry and reading.
- **Label (md/sm):** 0.75rem. All-caps for metadata, using `on_surface_variant` (#444933) to provide a secondary layer of information without cluttering the visual field.

*Director's Note:* Use `tracking-tight` on all Headlines and Display text to give the font a custom, high-end "locked-in" feel.

---

## 4. Elevation & Depth: Tonal Layering

We convey hierarchy through **Tonal Layering** rather than structural lines or heavy drop shadows.

### The Layering Principle
Depth is achieved by "stacking" the surface-container tiers.
1.  **Level 0 (Base):** `surface` (#f9f9f9)
2.  **Level 1 (Sections):** `surface_container_low` (#f3f3f3)
3.  **Level 2 (Cards/Modals):** `surface_container_lowest` (#ffffff)

### Ambient Shadows
When a floating effect is required (e.g., a modal or dropdown), use **Ambient Shadows**:
- **Blur:** 40px - 60px.
- **Opacity:** 4% - 6%.
- **Tint:** Use a tinted version of `on_surface` (a very dark slate-green) instead of pure black.

### The "Ghost Border" Fallback
If an element lacks contrast against its background, use a **Ghost Border**: A 1px stroke using the `outline_variant` token at **15% opacity**. Never use a 100% opaque border.

---

## 5. Components

### Buttons
- **Primary:** Neon Lime (`primary_container`). Squircle shape (`rounded-3xl`). Text in `on_primary_fixed` (#171e00).
- **Secondary:** Ghost style. No background, `Ghost Border` (15% opacity).
- **Tertiary:** Pure text with a Lucide React icon trailing.

### Cards
Cards must never have borders. They are "white islands" (`surface_container_lowest`) floating on a slate sea. Use `rounded-3xl` for all card corners.

### Input Fields
- **Background:** `surface_container_high` (#e8e8e8).
- **State:** On focus, the background remains, but a 2px `primary` (#526600) ring appears with a soft neon glow.
- **Shape:** `rounded-2xl`.

### Lists & Data Tables
- **Forbid Divider Lines.** Separate list items using `spacing-3` (1rem) of vertical whitespace.
- For active rows, apply a subtle background shift to `surface_container_highest` (#e2e2e2).

### Additional Component: The "Quick Action" Glass-Chip
For CRM context (Lead status, priority), use chips with a `backdrop-blur-md` and 40% opacity of the status color (e.g., 40% opacity neon green for "Active").

---

## 6. Do’s and Don'ts

### Do:
- **Do** use asymmetrical margins (e.g., `ml-16 mr-8`) to create a sense of motion.
- **Do** lean into the "Squircle." If an element is clickable or a container, round it heavily.
- **Do** use Lucide icons with a `stroke-width` of 1.5px to match the weight of Inter's medium strokes.

### Don’t:
- **Don’t** use pure black (#000000) for text. Use Slate-900 (`on_surface`) to keep the "high-end" softness.
- **Don’t** use a standard 4px or 8px border-radius. It looks "Bootstrap" and dated. Stick to the `xl` (3rem) or `lg` (2rem) scale.
- **Don’t** crowd the UI. If you feel like you need a divider line, you actually need more whitespace (`spacing-8`).

---

## 7. Application Rule

Todas as novas criações de frontend devem seguir este padrão de design como referência obrigatória.
