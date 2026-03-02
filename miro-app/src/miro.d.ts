// Minimal ambient type declarations for the Miro Web SDK v2.
// Covers only the subset of the API used by this panel.
// Full types: https://developers.miro.com/docs/websdk-reference

declare namespace MiroSdk {
  interface CardItem {
    type: "card";
    id: string;
    title: string;
    description: string;
    x: number;
    y: number;
  }

  interface CreateCardOptions {
    title: string;
    description?: string;
    x?: number;
    y?: number;
    width?: number;
  }

  type SelectableItem = CardItem | { type: string; id: string };

  interface DropEvent {
    x: number;
    y: number;
    target: HTMLElement;
  }

  interface BoardUi {
    on(event: "drop", handler: (event: DropEvent) => void | Promise<void>): void;
    on(event: "icon:click" | "selection:update" | string, handler: () => void): void;
    openPanel(options: { url: string }): Promise<void>;
    closePanel(): Promise<void>;
  }

  interface CreateStickyNoteOptions {
    content: string;
    x?: number;
    y?: number;
    width?: number;
  }

  interface Board {
    getSelection(): Promise<SelectableItem[]>;
    get(filter: { type: "card" }): Promise<CardItem[]>;
    createCard(options: CreateCardOptions): Promise<CardItem>;
    createStickyNote(options: CreateStickyNoteOptions): Promise<{ id: string }>;
    ui: BoardUi;
  }

  interface Sdk {
    board: Board;
  }
}

declare const miro: MiroSdk.Sdk;
