// headless.ts — silent background entry point
// Loaded automatically by Miro when the board opens.
// Registers the toolbar icon click handler and opens the panel.

miro.board.ui.on("icon:click", async () => {
  await miro.board.ui.openPanel({ url: "/panel" });
});
