# AI Coding Agent Instructions for Media Gallery Vue

## Project Overview

This is a **Vue 3 + TypeScript + Vite** media gallery application using **Tailwind CSS v4** with a custom design system featuring orange/violet gradients and glassmorphism aesthetics.

## Tech Stack & Key Dependencies

- **Vue 3.5** with Composition API (`<script setup>` only)
- **TypeScript 5.9** with strict type checking (`vue-tsc`)
- **Vite 7** as build tool
- **Tailwind CSS v4** via `@tailwindcss/vite` plugin (new API)
- **Vue Router 4** for navigation
- **FontAwesome** for icons (imported via `@fortawesome/vue-fontawesome`)
- **Yarn 1.22.22** enforced via `preinstall` script (use `yarn`, not `npm`)
- **Node 22.x** required (see `engines` in package.json)

## Development Commands

```bash
yarn dev          # Start dev server with HMR
yarn build        # Type-check + build for production
yarn type-check   # Run vue-tsc separately
yarn lint         # Run ESLint with auto-fix
yarn format       # Run Prettier on src/
```

## Architecture & File Organization

### Component Structure

- All components use **`<script setup lang="ts">`** - no Options API
- Components use **CSS Modules** for scoped styles: `import styles from "./styles.module.css"`
- Apply styles via `:class="[styles.className]"` in templates
- See [Header.vue](../src/components/header/Header.vue) and [Footer.vue](../src/components/footer/Footer.vue) for reference patterns

### Routing

- Routes defined in [src/router/index.ts](../src/router/index.ts) using an enum:
  ```typescript
  export enum RoutePaths {
    HOME = "/",
  }
  ```
- Always import and use `RoutePaths` enum for type-safe navigation
- RouterLink example: `<RouterLink :to="RoutePaths.HOME">`

### Styling System (Tailwind v4 + Custom Design Tokens)

#### Design Tokens in [@theme](../src/assets/main.css)

Custom CSS variables defined in `@theme` block (Tailwind v4 syntax):

- **Colors**: `--color-orange`, `--color-violet`, `--color-bg-start/mid/end`, `--color-text-primary/secondary/muted`
- **Spacing**: `--header-height: 3.75rem`
- **Shadows**: `--shadow-glow-orange`, `--shadow-glow-violet` (with `oklch()` color functions)
- **Fonts**: `--font-roboto-mono`, `--font-pixeboy` (custom font loaded via `@font-face`)

#### Tailwind Utilities

Access theme variables with parentheses syntax:

- Heights: `h-(--header-height)`, `pt-(--header-height)`
- Colors: Use semantic class names like `text-orange`, `text-violet-light`, `bg-orange/10`
- Custom utilities: `text-gradient`, `glow-orange`, `glow-violet`, `gradient-bg`

#### Component Classes in @layer components

Reusable design system components in [main.css](../src/assets/main.css) (around line 159):

- Buttons: `.btn`, `.btn-primary`, `.btn-secondary`, `.btn-outline-orange`, `.btn-outline-violet`
- Cards: `.card`, `.card-title`, `.card-value`
- Forms: `.input`, `.progress-bar`, `.toggle`
- Badges: `.badge`, `.badge-orange`, `.badge-violet`, `.badge-gradient`
- Text: `.text-gradient` (orange→violet gradient with `bg-clip-text`)

#### CSS Module Best Practices

- Use for component-specific layout/positioning (e.g., header fixed positioning)
- Reference main.css variables via `@reference "@/assets/main.css"`
- Combine with Tailwind utilities: `:class="[styles.headerContainer, 'flex', 'items-center']"`

### Path Aliases

- `@/*` maps to `./src/*` configured in [vite.config.ts](../vite.config.ts) and [tsconfig.app.json](../tsconfig.app.json)
- **MUST use `@/` path alias for all imports** - Never use relative paths (`../`, `./`)
- Examples: `import Header from "@/components/header/Header.vue"`, `import { RoutePaths } from "@/router"`

## TypeScript & Linting Rules

### Strict ESLint Configuration

Key enforced rules from [eslint.config.ts](../eslint.config.ts):

- **No `any` types**: `@typescript-eslint/no-explicit-any: "error"`
- **Strict equality only**: `eqeqeq: ["error", "always"]` (use `===`/`!==`)
- **Strict boolean expressions**: No truthy/falsy checks on non-booleans
- **Unused vars**: Prefix with `_` to ignore: `const _unused = ...`
- **Component naming**: PascalCase in templates, multi-word not required
- **Vue macros order**: `defineProps` before `defineEmits`
- **Script setup only**: `vue/component-api-style: ["error", ["script-setup"]]`
- **Prop types**: `vue/require-default-prop` and `vue/require-prop-types` enforced
- **Semicolons required**: Always use semicolons in TS/JS

### TypeScript Project Structure

- Composite project: [tsconfig.json](../tsconfig.json) references `tsconfig.app.json` and `tsconfig.node.json`
- Build artifacts in `./node_modules/.tmp/tsconfig.app.tsbuildinfo`
- Use `vue-tsc --build` for type checking (not `tsc`)

## Code Style Conventions

### Component Props

Always define with types and defaults:

```typescript
interface Props {
  title: string;
  count?: number;
}
const props = withDefaults(defineProps<Props>(), {
  count: 0,
});
```

### Console Usage

Only `console.warn` and `console.error` allowed (others are warnings)

### Vue Template Style

- Use PascalCase for components in templates: `<RouterLink>`, `<Header />`
- Self-closing tags for components without children: `<Header />`
- camelCase for custom events

## Special Notes

### Custom Font Loading

- Custom font "pixeboy" loaded via `@font-face` in [main.css](../src/assets/main.css) (line 5)
- Available as utility class: `font-pixeboy`
- Used for gradient headings: `<strong class="text-gradient font-pixeboy">`

### App Mount Point

App mounts to `#root` not `#app` - see [main.ts](../src/main.ts) (line 11)

### Package Manager Lock

Project enforces Yarn via preinstall hook - `npm install` will fail

### Environment Files

- Ignore all `.env*` files except `.env.example`
- Never commit `.env`, `.env.local`, `.env.development`, `.env.production`
- Use `.env.example` as template for required environment variables

### Development Tools

- **Vue DevTools**: Required for debugging (see README for browser extensions)
- **Vite DevTools**: Included via `vite-plugin-vue-devtools`
- **VS Code**: Requires Vue Official (Volar) extension, disable Vetur

## When Adding New Features

1. **New routes**: Add to `RoutePaths` enum in [router/index.ts](../src/router/index.ts)
2. **New components**: Place in `src/components/{feature}/Component.vue` + `styles.module.css`
3. **New colors/tokens**: Add to `@theme` block in [main.css](../src/assets/main.css)
4. **New utilities**: Add to `@layer components` or `@layer utilities` sections
5. **Type definitions**: Place in `src/types/` (not yet created)

## Production Build Notes

- Build command runs type-check in parallel with build: `run-p type-check "build-only {@}"`
- Output directory: `dist/`
- Preview built app: `yarn preview`
