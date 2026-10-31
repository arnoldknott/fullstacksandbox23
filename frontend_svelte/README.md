# create-svelte

Everything you need to build a Svelte project, powered by [`create-svelte`](https://github.com/sveltejs/kit/tree/master/packages/create-svelte).

## Creating a project

If you're seeing this, you've probably already done this step. Congrats!

```bash
# create a new project in the current directory
npm create svelte@latest

# create a new project in my-app
npm create svelte@latest my-app
```

## Developing

Once you've created a project and installed dependencies with `npm install` (or `pnpm install` or `yarn` or `bun`), start a development server:

```bash
bun dev

# or start the server and open the app in a new browser tab
bun dev -- --open
```

## Building

To create a production version of your app:

```bash
bun build
```

You can preview the production build with `bun preview`.

> To deploy your app, you may need to install an [adapter](https://kit.svelte.dev/docs/adapters) for your target environment.

## Presentation image zoom

The Country Overshoot slide uses
[`ZoomableImage.svelte`](<./src/routes/(layout)/presentation/teachingengagement/cbs-2026-11/ZoomableImage.svelte>).
Pass the image address through its required `url` prop. The component fits the
image into the available slide space and provides Leaflet scroll-wheel zoom,
drag-to-pan, and vertically stacked FlyonUI + / − / reset controls in the top-left.
The reset button restores the full image
and its original pan position. Its rounded frame, shadow, and footer clearance
are built in; no map tiles or additional dependencies are needed.

The welcome slide measures its centered heading using Svelte dimension bindings
and passes `excludeWidth` and `excludeHeight` to `NameCloud`. Random name placements
avoid that centered area with 16 pixels of clearance, recalculating when the
container, name, or heading changes size.
