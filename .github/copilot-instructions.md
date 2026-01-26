# AI Coding Agent Instructions for Media Gallery Vue

## Project Overview

This is a **Vue 3 + TypeScript + Vite** media gallery application using **Tailwind CSS v4** with a custom design system featuring orange/violet gradients and glassmorphism aesthetics.

## Tech Stack & Key Dependencies

- **Vue 3.5** with Composition API (`<script setup>` only)
- **TypeScript 5.9** with strict type checking (`vue-tsc`)
- **Vite 7** as build tool with `vite-plugin-checker` for live type checking
- **Tailwind CSS v4** via `@tailwindcss/vite` plugin (new API)
- **Vue Router 4** for navigation with typed route guards
- **Vue I18n 11** for internationalization (i18n)
- **Axios 1.13** for HTTP requests (via custom `HttpClient` class)
- **FontAwesome 7** for icons (via `@fortawesome/vue-fontawesome`)
- **VueUse Core 14** for composition utilities (e.g., `useInfiniteScroll`, `useScroll`)
- **Uppy 5** for file uploads with Tus protocol support
- **date-fns 4** for date manipulation
- **medium-zoom 1** for image zoom functionality
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

- Routes defined in [src/router/index.ts](../src/router/index.ts) using a `routes` object:
  ```typescript
  export const routes = {
    home: { path: "/", name: "home" },
    login: { path: "/login", name: "login" },
  };
  ```
- Always import and use `routes` object for type-safe navigation
- RouterLink example: `<RouterLink :to="routes.home.path">`
- Route guards implement authentication:
  - `requiresAuth: true` - requires user to be logged in
  - `guestOnly: true` - only accessible when not authenticated (e.g., login page)
- User stored in `localStorage` as `user` key (parsed as JSON)
- Redirect to login with `?redirect=` query param to preserve intended destination

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
- Examples: `import Header from "@/components/header/Header.vue"`, `import { routes } from "@/router"`

## API & Data Handling

### HTTP Client Architecture

- Custom `HttpClient` class in [src/api/http-client.ts](../src/api/http-client.ts) extends Axios
- Base URL from `import.meta.env.VITE_API_BASE_URL`
- Protected methods: `get<TResponse>()`, `post<TResponse, TRequest>()`
- Repositories extend `HttpClient` for domain-specific API calls
- Example repositories: `seaweedRepository`, `userRepository`

### API Patterns

**Repository Pattern:**

```typescript
class SeaweedRepository extends HttpClient {
  async getAllFiles(params?: GetAllFilesParams): Promise<GetAllFilesDto> {
    const response = await this.get<ApiResponse>(this.resource, { params });
    return new GetAllFilesDto(response);
  }
}
export default new SeaweedRepository();
```

**DTO Classes:**

- Transform API responses into typed domain objects
- Located in `src/api/dto/`
- Example: `GetAllFilesDto` transforms API response with date formatting

### Composables Pattern

**useFilesInfiniteScroll:**

- Manages infinite scroll pagination for media files
- Returns: `{ shouldLoadMore, onLoadMore, datas }`
- Groups files by date (descending order) using `date-fns`
- Updates `limit` and `lastFileName` for cursor-based pagination

**useAuth:**

- Authentication state management
- Returns: `{ user, isAuthenticated, login }`
- Stores user in `localStorage` as JSON
- Redirects to home after successful login

**useLocale:**

- i18n wrapper composable
- Returns: `{ locale, setLocale, t }`
- Uses typed i18n instance for type-safe translations

**useUppyModal:**

- Global state for Uppy dashboard modal
- Returns: `{ open, toggleModal }`
- Shared across components using Vue's reactivity

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

### Generic Components

Support TypeScript generics in `<script setup>`:

```vue
<script setup lang="ts" generic="TData">
interface Props {
  data?: Array<TData>;
}
</script>
```

## Reusable Component Library

### Button Components

**ButtonPrimary.vue:**

- Orange gradient button for primary actions
- Auto-translates label via `t("common.upload")`
- Inherits all native button attributes via `useAttrs()`
- CSS classes: `btn btn-primary`

**ButtonSecondary.vue:**

- Violet gradient button for secondary actions
- Props: `{ disabled?: boolean }`
- Default slot shows `t("common.submit")`
- CSS classes: `btn btn-secondary`

### Input Component

**Input.vue:**

- Reusable input field with label
- Props: `{ label?: string, modelValue: string | boolean | undefined, disabled?: boolean }`
- Emits: `update:modelValue` with InputEvent
- Inherits all native input attributes
- CSS classes: `input`, label has `text-gradient`

### Spinner Component

**Spinner.vue:**

- Loading spinner with size variants
- Props: `{ size?: "sm" | "md" | "lg" }`
- Default size: `"md"`
- Uses CSS Modules for styling

### Layout Components

**Header.vue:**

- Fixed header with gradient logo and upload button
- Height: `var(--header-height)` (3.75rem)
- Conditionally shows upload button when authenticated
- Uses CSS Modules for positioning

**Footer.vue:**

- Footer with gradient branding
- Uses FontAwesome heart icon
- CSS Modules for styling

## Internationalization (i18n)

### I18nManager Singleton

- Singleton pattern in [src/services/i18n/index.ts](../src/services/i18n/index.ts)
- Supported locales: `"vi-vn"` (default), `"en"` (fallback)
- Type-safe with `TypedI18n` and `MessageSchema` inferred from JSON files
- Auto-detects browser locale on init
- Locale files: `src/locales/en.json`, `src/locales/vi-vn.json`

### Usage Pattern

```typescript
import { useLocale } from "@/composables/useLocale";
const { t, locale, setLocale } = useLocale();
// In template: {{ t("common.upload") }}
```

## File Upload System

### Uppy Integration

- Uppy v5 with Dashboard and Tus protocol support
- Service factory: `createTusUppyService()` in [src/services/uppy/tus.ts](../src/services/uppy/tus.ts)
- Modal component: [UppyDashboardModal.vue](../src/components/uppy/UppyDashboardModal.vue)
- Global modal state via `useUppyModal` composable
- Tus endpoint from `import.meta.env.VITE_SEAWEEDFS_TUS_ENDPOINT`
- CSS imports required: `@uppy/core/css/style.min.css`, `@uppy/dashboard/css/style.min.css`

### Uppy Lifecycle

- Service destroyed in `onUnmounted()` hook to prevent memory leaks
- Dashboard modal controlled by global `open` state

### Uppy Configuration

- Auto-proceed: `false` (manual upload)
- Max files: 30
- Allowed types: `image/*`, `video/*`
- Chunk size: 50 MB
- Retry delays: `[0, 1000, 3000, 5000, 10000, 30000]`
- Fingerprint storage for resumable uploads
- Concurrent upload limit: 3
- Auto-generates UUID filenames via `onBeforeFileAdded` hook

## Date Services

### DateFnsService Class

- Service wrapper in [src/services/date-fns/index.ts](../src/services/date-fns/index.ts)
- Wraps `date-fns` library with consistent formatting
- Properties:
  - `date: Date` - parsed Date object
  - `formattedDate: string` - formatted as "dd-MM-yyyy"
- Used by DTOs to transform API date strings

## Media Handling

### Utility Functions

**MIME Type Helpers** in [src/utils/mime.ts](../src/utils/mime.ts):

- `isImage(mime: string): boolean` - checks if MIME type starts with `"image/"`
- `isVideo(mime: string): boolean` - checks if MIME type starts with `"video/"`
- Null-safe with type guards

### Medium Zoom Integration

- Image zoom library for gallery view
- Initialized in `onMounted()` with `.zoomable` selector
- Configuration: `{ margin: 24, background: "rgba(0, 0, 0, 0.8)", scrollOffset: 40 }`
- Re-attach after data changes: `zoom?.attach(".zoomable")` in `watch` callback

## Infinite Scroll Pattern

### InfiniteScroll Component

- Generic component in [src/components/infinite-scroll/InfiniteScroll.vue](../src/components/infinite-scroll/InfiniteScroll.vue)
- Uses `useInfiniteScroll` from `@vueuse/core`
- Props: `{ data?: Array<TData>, shouldLoadMore: boolean }`
- Emits: `loadMore` event with scroll state
- Auto-shows spinner when loading
- Distance: `100` (pixels from bottom)

### Usage Pattern

```vue
<InfiniteScroll :should-load-more="shouldLoadMore" @load-more="onLoadMore">
  <li v-for="item in items" :key="item.id">{{ item }}</li>
</InfiniteScroll>
```

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
- Required variables:
  - `VITE_API_BASE_URL` - API base URL for HttpClient
  - `VITE_SEAWEEDFS_TUS_ENDPOINT` - Tus upload endpoint for Uppy

### Development Tools

- **Vue DevTools**: Required for debugging (see README for browser extensions)
- **Vite DevTools**: Included via `vite-plugin-vue-devtools`
- **VS Code**: Requires Vue Official (Volar) extension, disable Vetur

## When Adding New Features

1. **New routes**: Add to `routes` object in [router/index.ts](../src/router/index.ts)
2. **New components**: Place in `src/components/{feature}/Component.vue` + `styles.module.css`
3. **New colors/tokens**: Add to `@theme` block in [main.css](../src/assets/main.css)
4. **New utilities**: Add to `@layer components` or `@layer utilities` sections
5. **New API endpoints**: Create repository class extending `HttpClient` in `src/api/repositories/`
6. **New translations**: Add keys to both `src/locales/en.json` and `src/locales/vi-vn.json`
7. **Type definitions**: Place in `src/types/` (not yet created)

## Production Build Notes

- Build command runs type-check in parallel with build: `run-p type-check "build-only {@}"`
- Output directory: `dist/`
- Preview built app: `yarn preview`
