# NOKNOW

## ABOUT

This is the backend client for NoKnow; a realtime live chatting web application.

Allows users to access api functions such as creating new chatrooms, engaging chatrooms, searching for chatrooms, searching for users, etc.

## Tech stack

Typescript, React, HTML, CSS, Tanstack query, Zod

## Environment variables

- `VITE_BACKEND_HOST`
- `VITE_BACKEND_PORT`

- `VITE_ACCOUNT_SUSPENDED_ERROR_CODE`
- `VITE_NOT_ADMIN_ERROR_CODE`

- `VITE_DEBUG`

## Installation

- Fork repository.

- Clone repository to your local machine.

- Set the necessary environment variables.

- Install all necessary dependencies by running:

```bash
  npm ci
```

- Build application by running:

```bash
  npm build
```

- Run server:

```bash
  npm run dev
```

## Project ordering

- Folders are heirarchical and nested in a consistent pattern across the project

- Components are stored within their own exclusive folders with a matching name. e.g "Button.tsx" inside "/button".
  Any css styling file name matches the target component's name, and is stored within the same folder.
  e.g ["Button.tsx", "Button.css"] inside "/button".

- In some cases, multiple _related_ components may be stored within a folder with:
  (1) the name main focus component's name matching the folder name. e.g ["Form.tsx", "Button.tsx", "Popup.tsx",...] inside "/form"
  (2) all components within the folder serving similar purpose. e.g ["LoginForm.tsx", "CreateForm.tsx",...] inside "/forms"

- Page/Window components are stored within their respective folders with "PageComponent.tsx" and "/pageComponent" folder
  having matching names, Except in rare cases where such splitting would be unnecessary as pages serve similar purposes
  with differences only being in hooks used within.

### Project Structure

The frontend code is structured as follows:

- `frontend/src` - Main frontend code.

- `frontend/src/assets` - Static assets.

- `frontend/src/public` - Public assets client.

- `frontend/src/components` - Components of the frontend.
- `frontend/src/components/adminPageComponents` - Components for admin panel pages.
- `frontend/src/components/forms` - Form components.
- `frontend/src/components/general` - Generic components usable across all pages.
- `frontend/src/components/pageComponents` - Components for distinct pages.
- `frontend/src/components/pageComponents/chatComponents` - Components for chat related pages.
- `frontend/src/components/pageComponents/userComponents` - Components for user related pages.

- `frontend/src/constants` - Constant unchanging values

- `frontend/src/contexts` - Context providers

- `frontend/src/hooks` - Custom hooks

- `frontend/src/layout` - Top level page layout components

- `frontend/src/pages` - Compound components for pages

- `frontend/src/schemas` - Zod object schemas for data validation

- `frontend/src/styles` - CSS style files
- `frontend/src/styles/forms` - CSS style files for distinct types of forms

- `frontend/src/types` - Typescript types

- `frontend/src/utilities` - Callable functions
