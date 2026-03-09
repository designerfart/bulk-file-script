import json
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from pathlib import Path

APP_TITLE = "Bulk File Renamer @virgil"
MANIFEST_NAME = "file_descriptions.json"

#this tool was made by @virgil
#enjoy

class BulkFileTool:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title(APP_TITLE)
        self.root.geometry("1320x780")
        self.root.minsize(1080, 680)

        self.files: list[Path] = []
        self.folder: Path | None = None
        self.descriptions: dict[str, str] = {}

        self.prefix_var = tk.StringVar()
        self.suffix_var = tk.StringVar()
        self.same_desc_var = tk.StringVar()
        self.filter_var = tk.StringVar()
        self.status_var = tk.StringVar(value="Choose a folder or add files to begin.")
        self.keep_extension_var = tk.BooleanVar(value=True)
        self.reset_descriptions_var = tk.BooleanVar(value=True)

        self.sequence_base_var = tk.StringVar(value="1")
        self.sequence_step_var = tk.StringVar(value="1")
        self.sequence_padding_var = tk.StringVar(value="0")

        self._build_ui()

    def _build_ui(self):
        top = ttk.Frame(self.root, padding=10)
        top.pack(fill="x")

        ttk.Button(top, text="Open Folder", command=self.open_folder).pack(side="left", padx=(0, 8))
        ttk.Button(top, text="Add Files", command=self.add_files).pack(side="left", padx=(0, 8))
        ttk.Button(top, text="Clear List", command=self.clear_files).pack(side="left", padx=(0, 8))
        ttk.Button(top, text="Load Descriptions", command=self.load_manifest).pack(side="left", padx=(0, 8))
        ttk.Button(top, text="Save Descriptions", command=self.save_manifest).pack(side="left", padx=(0, 8))
        ttk.Button(top, text="Reset Selected Properties", command=self.reset_selected_properties).pack(side="left", padx=(0, 8))
        ttk.Button(top, text="Reset All Properties", command=self.reset_all_properties).pack(side="left")

        filter_frame = ttk.Frame(self.root, padding=(10, 0, 10, 10))
        filter_frame.pack(fill="x")
        ttk.Label(filter_frame, text="Filter files:").pack(side="left")
        filter_entry = ttk.Entry(filter_frame, textvariable=self.filter_var)
        filter_entry.pack(side="left", fill="x", expand=True, padx=(8, 8))
        filter_entry.bind("<KeyRelease>", lambda _e: self.refresh_table())

        rename_frame = ttk.LabelFrame(self.root, text="Add Tag / Prefix / Suffix", padding=10)
        rename_frame.pack(fill="x", padx=10, pady=(0, 10))

        ttk.Label(rename_frame, text="Prefix:").grid(row=0, column=0, sticky="w")
        ttk.Entry(rename_frame, textvariable=self.prefix_var, width=24).grid(row=0, column=1, sticky="w", padx=(6, 16))

        ttk.Label(rename_frame, text="Suffix:").grid(row=0, column=2, sticky="w")
        ttk.Entry(rename_frame, textvariable=self.suffix_var, width=24).grid(row=0, column=3, sticky="w", padx=(6, 16))

        ttk.Checkbutton(rename_frame, text="Keep file extension", variable=self.keep_extension_var).grid(row=0, column=4, sticky="w")

        ttk.Button(rename_frame, text="Preview Selected", command=self.preview_selected).grid(row=1, column=0, pady=(10, 0), sticky="w")
        ttk.Button(rename_frame, text="Rename Selected", command=self.rename_selected).grid(row=1, column=1, pady=(10, 0), sticky="w")
        ttk.Button(rename_frame, text="Rename All", command=self.rename_all).grid(row=1, column=2, pady=(10, 0), sticky="w")

        full_rename_frame = ttk.LabelFrame(self.root, text="Replace Entire File Name", padding=10)
        full_rename_frame.pack(fill="x", padx=10, pady=(0, 10))

        ttk.Label(full_rename_frame, text="Start number:").grid(row=0, column=0, sticky="w")
        ttk.Entry(full_rename_frame, textvariable=self.sequence_base_var, width=10).grid(row=0, column=1, sticky="w", padx=(6, 16))

        ttk.Label(full_rename_frame, text="Step:").grid(row=0, column=2, sticky="w")
        ttk.Entry(full_rename_frame, textvariable=self.sequence_step_var, width=10).grid(row=0, column=3, sticky="w", padx=(6, 16))

        ttk.Label(full_rename_frame, text="Zero padding:").grid(row=0, column=4, sticky="w")
        ttk.Entry(full_rename_frame, textvariable=self.sequence_padding_var, width=10).grid(row=0, column=5, sticky="w", padx=(6, 16))

        ttk.Button(full_rename_frame, text="Preview Selected Sequence", command=self.preview_selected_sequence).grid(row=1, column=0, pady=(10, 0), sticky="w")
        ttk.Button(full_rename_frame, text="Rename Selected to Sequence", command=self.rename_selected_sequence).grid(row=1, column=1, pady=(10, 0), sticky="w")
        ttk.Button(full_rename_frame, text="Rename All to Sequence", command=self.rename_all_sequence).grid(row=1, column=2, pady=(10, 0), sticky="w")

        desc_frame = ttk.LabelFrame(self.root, text="Descriptions", padding=10)
        desc_frame.pack(fill="x", padx=10, pady=(0, 10))

        ttk.Label(desc_frame, text="Apply same description to selected:").grid(row=0, column=0, sticky="w")
        ttk.Entry(desc_frame, textvariable=self.same_desc_var, width=70).grid(row=0, column=1, sticky="we", padx=(8, 8))
        ttk.Button(desc_frame, text="Apply to Selected", command=self.apply_same_description).grid(row=0, column=2, sticky="e")
        ttk.Button(desc_frame, text="Apply to All", command=self.apply_same_description_all).grid(row=0, column=3, sticky="e", padx=(8, 0))
        desc_frame.columnconfigure(1, weight=1)

        reset_frame = ttk.LabelFrame(self.root, text="Bulk Property Reset", padding=10)
        reset_frame.pack(fill="x", padx=10, pady=(0, 10))
        ttk.Checkbutton(
            reset_frame,
            text="Clear saved descriptions when resetting properties",
            variable=self.reset_descriptions_var,
        ).pack(anchor="w")
        ttk.Label(
            reset_frame,
            text="This clears the descriptions stored in the JSON manifest for the selected files."
        ).pack(anchor="w", pady=(4, 0))

        table_frame = ttk.Frame(self.root, padding=(10, 0, 10, 10))
        table_frame.pack(fill="both", expand=True)

        columns = ("name", "preview", "description", "path")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", selectmode="extended")
        self.tree.heading("name", text="Current Name")
        self.tree.heading("preview", text="Preview")
        self.tree.heading("description", text="Description")
        self.tree.heading("path", text="Full Path")

        self.tree.column("name", width=230, anchor="w")
        self.tree.column("preview", width=240, anchor="w")
        self.tree.column("description", width=280, anchor="w")
        self.tree.column("path", width=480, anchor="w")

        yscroll = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        xscroll = ttk.Scrollbar(table_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=yscroll.set, xscrollcommand=xscroll.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        yscroll.grid(row=0, column=1, sticky="ns")
        xscroll.grid(row=1, column=0, sticky="ew")
        table_frame.rowconfigure(0, weight=1)
        table_frame.columnconfigure(0, weight=1)

        self.tree.bind("<Double-1>", self.edit_description_cell)

        bottom = ttk.Frame(self.root, padding=(10, 0, 10, 10))
        bottom.pack(fill="x")
        ttk.Label(bottom, textvariable=self.status_var).pack(side="left")

    def sanitize_name(self, name: str) -> str:
        invalid = '<>:"/\\|?*'
        cleaned = "".join("_" if c in invalid else c for c in name)
        return cleaned.strip()

    def build_tagged_name(self, path: Path) -> str:
        prefix = self.prefix_var.get().strip()
        suffix = self.suffix_var.get().strip()

        if self.keep_extension_var.get():
            new_name = f"{prefix}{path.stem}{suffix}{path.suffix}"
        else:
            new_name = f"{prefix}{path.name}{suffix}"

        return self.sanitize_name(new_name)

    def get_sequence_settings(self) -> tuple[int, int, int]:
        try:
            start = int(self.sequence_base_var.get().strip())
            step = int(self.sequence_step_var.get().strip())
            padding = int(self.sequence_padding_var.get().strip())
        except ValueError:
            raise ValueError("Start number, step, and zero padding must all be whole numbers.")

        if step == 0:
            raise ValueError("Step cannot be 0.")
        if padding < 0:
            raise ValueError("Zero padding cannot be negative.")

        return start, step, padding

    def build_sequence_name(self, path: Path, number: int, padding: int) -> str:
        name_core = str(number).zfill(padding) if padding > 0 else str(number)
        if self.keep_extension_var.get():
            new_name = f"{name_core}{path.suffix}"
        else:
            new_name = name_core
        return self.sanitize_name(new_name)

    def open_folder(self):
        folder = filedialog.askdirectory(title="Choose a folder")
        if not folder:
            return

        self.folder = Path(folder)
        self.files = sorted([p for p in self.folder.iterdir() if p.is_file()])
        self.load_manifest(silent=True)
        self.refresh_table()
        self.status_var.set(f"Loaded {len(self.files)} files from {self.folder}")

    def add_files(self):
        paths = filedialog.askopenfilenames(title="Choose files")
        if not paths:
            return

        for item in paths:
            p = Path(item)
            if p not in self.files:
                self.files.append(p)

        self.files = sorted(self.files)
        if self.files and len({p.parent for p in self.files}) == 1:
            self.folder = self.files[0].parent
            self.load_manifest(silent=True)
        self.refresh_table()
        self.status_var.set(f"Loaded {len(self.files)} files.")

    def clear_files(self):
        self.files.clear()
        self.folder = None
        self.descriptions.clear()
        self.refresh_table()
        self.status_var.set("Cleared file list.")

    def manifest_path(self) -> Path | None:
        if self.folder is not None:
            return self.folder / MANIFEST_NAME
        return None

    def load_manifest(self, silent: bool = False):
        manifest = self.manifest_path()
        if manifest is None or not manifest.exists():
            if not silent:
                messagebox.showinfo(APP_TITLE, "No description manifest found for the current folder.")
            return

        try:
            with manifest.open("r", encoding="utf-8") as f:
                self.descriptions = json.load(f)
            self.refresh_table()
            if not silent:
                messagebox.showinfo(APP_TITLE, f"Loaded descriptions from:\n{manifest}")
        except Exception as exc:
            messagebox.showerror(APP_TITLE, f"Could not load manifest:\n{exc}")

    def save_manifest(self):
        if not self.files:
            messagebox.showwarning(APP_TITLE, "Load some files first.")
            return

        manifest = self.manifest_path()
        if manifest is None:
            save_path = filedialog.asksaveasfilename(
                title="Save descriptions as JSON",
                defaultextension=".json",
                initialfile=MANIFEST_NAME,
                filetypes=[("JSON Files", "*.json")],
            )
            if not save_path:
                return
            manifest = Path(save_path)

        try:
            with manifest.open("w", encoding="utf-8") as f:
                json.dump(self.descriptions, f, indent=2, ensure_ascii=False)
            self.status_var.set(f"Saved descriptions to {manifest}")
            messagebox.showinfo(APP_TITLE, f"Descriptions saved to:\n{manifest}")
        except Exception as exc:
            messagebox.showerror(APP_TITLE, f"Could not save manifest:\n{exc}")

    def refresh_table(self):
        self.tree.delete(*self.tree.get_children())
        query = self.filter_var.get().strip().lower()

        for path in self.files:
            desc = self.descriptions.get(str(path), "")
            preview = self.build_tagged_name(path)
            haystack = f"{path.name} {desc} {path}".lower()
            if query and query not in haystack:
                continue
            self.tree.insert("", "end", iid=str(path), values=(path.name, preview, desc, str(path)))

    def selected_paths(self) -> list[Path]:
        return [Path(iid) for iid in self.tree.selection()]

    def preview_selected(self):
        items = self.selected_paths()
        if not items:
            messagebox.showwarning(APP_TITLE, "Select one or more files first.")
            return

        preview_lines = [f"{p.name}  ->  {self.build_tagged_name(p)}" for p in items]
        messagebox.showinfo(APP_TITLE, "Preview:\n\n" + "\n".join(preview_lines[:60]) + ("\n..." if len(preview_lines) > 60 else ""))

    def preview_selected_sequence(self):
        items = self.selected_paths()
        if not items:
            messagebox.showwarning(APP_TITLE, "Select one or more files first.")
            return

        try:
            start, step, padding = self.get_sequence_settings()
        except ValueError as exc:
            messagebox.showerror(APP_TITLE, str(exc))
            return

        ordered = sorted(items)
        lines = []
        current = start
        for path in ordered:
            lines.append(f"{path.name}  ->  {self.build_sequence_name(path, current, padding)}")
            current += step

        messagebox.showinfo(APP_TITLE, "Sequence Preview:\n\n" + "\n".join(lines[:60]) + ("\n..." if len(lines) > 60 else ""))

    def rename_paths(self, paths: list[Path], name_builder):
        if not paths:
            messagebox.showwarning(APP_TITLE, "No files selected.")
            return

        current_paths = list(self.files)
        current_set = set(current_paths)
        path_set = set(paths)

        planned: dict[Path, Path] = {}
        errors: list[str] = []
        reserved_targets: set[Path] = set()

        for old_path in current_paths:
            if old_path not in path_set:
                continue
            try:
                new_name = name_builder(old_path)
                new_path = old_path.with_name(new_name)
            except Exception as exc:
                errors.append(f"Could not prepare rename for '{old_path.name}': {exc}")
                continue

            if new_path in reserved_targets:
                errors.append(f"Duplicate target name planned: '{new_path.name}'")
                continue

            if new_path.exists() and new_path not in current_set:
                errors.append(f"Skipped '{old_path.name}' because '{new_path.name}' already exists.")
                continue

            reserved_targets.add(new_path)
            planned[old_path] = new_path

        if not planned:
            messagebox.showerror(APP_TITLE, "No files were renamed.\n\n" + ("\n".join(errors[:25]) if errors else "Nothing to do."))
            return

        temp_to_final: dict[Path, Path] = {}
        new_descriptions = dict(self.descriptions)
        renamed = 0
        skipped = 0

        for old_path, final_path in planned.items():
            if old_path == final_path:
                skipped += 1
                continue

            temp_path = old_path.with_name(f"__bulk_tmp__{abs(hash((str(old_path), str(final_path))))}{old_path.suffix}")
            counter = 0
            while temp_path.exists() or temp_path in temp_to_final:
                counter += 1
                temp_path = old_path.with_name(f"__bulk_tmp__{abs(hash((str(old_path), str(final_path), counter)))}{old_path.suffix}")

            try:
                old_path.rename(temp_path)
                temp_to_final[temp_path] = final_path

                if str(old_path) in new_descriptions:
                    value = new_descriptions.pop(str(old_path))
                    new_descriptions[str(temp_path)] = value
            except Exception as exc:
                errors.append(f"Could not move '{old_path.name}' to a temp name: {exc}")

        for temp_path, final_path in temp_to_final.items():
            try:
                temp_path.rename(final_path)
                renamed += 1
                if str(temp_path) in new_descriptions:
                    value = new_descriptions.pop(str(temp_path))
                    new_descriptions[str(final_path)] = value
            except Exception as exc:
                errors.append(f"Could not rename '{temp_path.name}' to '{final_path.name}': {exc}")

        self.files = sorted([p for p in self.files[0].parent.iterdir() if p.is_file()]) if self.folder else sorted(
            [Path(k) for k in new_descriptions.keys() if Path(k).exists()] +
            [p for p in current_paths if p.exists() and p not in planned]
        )
        self.descriptions = {k: v for k, v in new_descriptions.items() if Path(k).exists()}
        self.refresh_table()
        self.status_var.set(f"Renamed {renamed} files. Skipped {skipped}.")

        if errors:
            messagebox.showwarning(APP_TITLE, "Finished with some issues:\n\n" + "\n".join(errors[:25]))
        else:
            messagebox.showinfo(APP_TITLE, f"Done. Renamed {renamed} files. Skipped {skipped}.")

    def rename_selected(self):
        self.rename_paths(self.selected_paths(), self.build_tagged_name)

    def rename_all(self):
        self.rename_paths(list(self.files), self.build_tagged_name)

    def rename_selected_sequence(self):
        items = sorted(self.selected_paths())
        if not items:
            messagebox.showwarning(APP_TITLE, "Select one or more files first.")
            return

        try:
            start, step, padding = self.get_sequence_settings()
        except ValueError as exc:
            messagebox.showerror(APP_TITLE, str(exc))
            return

        mapping: dict[Path, str] = {}
        current = start
        for path in items:
            mapping[path] = self.build_sequence_name(path, current, padding)
            current += step

        self.rename_paths(items, lambda p: mapping[p])

    def rename_all_sequence(self):
        items = sorted(self.files)
        if not items:
            messagebox.showwarning(APP_TITLE, "Load some files first.")
            return

        try:
            start, step, padding = self.get_sequence_settings()
        except ValueError as exc:
            messagebox.showerror(APP_TITLE, str(exc))
            return

        mapping: dict[Path, str] = {}
        current = start
        for path in items:
            mapping[path] = self.build_sequence_name(path, current, padding)
            current += step

        self.rename_paths(items, lambda p: mapping[p])

    def apply_same_description(self):
        items = self.selected_paths()
        if not items:
            messagebox.showwarning(APP_TITLE, "Select one or more files first.")
            return

        text = self.same_desc_var.get().strip()
        for path in items:
            self.descriptions[str(path)] = text
        self.refresh_table()
        self.status_var.set(f"Updated descriptions for {len(items)} files.")

    def apply_same_description_all(self):
        if not self.files:
            messagebox.showwarning(APP_TITLE, "Load some files first.")
            return

        text = self.same_desc_var.get().strip()
        for path in self.files:
            self.descriptions[str(path)] = text
        self.refresh_table()
        self.status_var.set(f"Updated descriptions for {len(self.files)} files.")

    def reset_descriptions_for_paths(self, paths: list[Path]):
        for path in paths:
            self.descriptions.pop(str(path), None)

    def reset_selected_properties(self):
        items = self.selected_paths()
        if not items:
            messagebox.showwarning(APP_TITLE, "Select one or more files first.")
            return

        if self.reset_descriptions_var.get():
            self.reset_descriptions_for_paths(items)
            self.refresh_table()
            self.status_var.set(f"Reset saved properties for {len(items)} files.")
            messagebox.showinfo(APP_TITLE, f"Cleared saved descriptions for {len(items)} selected files.")
        else:
            messagebox.showinfo(APP_TITLE, "Nothing was reset because description reset is unchecked.")

    def reset_all_properties(self):
        if not self.files:
            messagebox.showwarning(APP_TITLE, "Load some files first.")
            return

        if self.reset_descriptions_var.get():
            self.descriptions.clear()
            self.refresh_table()
            self.status_var.set(f"Reset saved properties for {len(self.files)} files.")
            messagebox.showinfo(APP_TITLE, f"Cleared saved descriptions for all {len(self.files)} files.")
        else:
            messagebox.showinfo(APP_TITLE, "Nothing was reset because description reset is unchecked.")

    def edit_description_cell(self, event):
        region = self.tree.identify("region", event.x, event.y)
        if region != "cell":
            return

        row_id = self.tree.identify_row(event.y)
        column = self.tree.identify_column(event.x)
        if not row_id or column != "#3":
            return

        x, y, width, height = self.tree.bbox(row_id, column)
        current_value = self.tree.set(row_id, "description")

        editor = ttk.Entry(self.tree)
        editor.insert(0, current_value)
        editor.place(x=x, y=y, width=width, height=height)
        editor.focus()
        editor.select_range(0, tk.END)

        def save_edit(_event=None):
            new_value = editor.get().strip()
            self.descriptions[row_id] = new_value
            editor.destroy()
            self.refresh_table()
            self.tree.selection_set(row_id)
            self.status_var.set(f"Updated description for {Path(row_id).name}")

        def cancel_edit(_event=None):
            editor.destroy()

        editor.bind("<Return>", save_edit)
        editor.bind("<Escape>", cancel_edit)
        editor.bind("<FocusOut>", save_edit)


def main():
    root = tk.Tk()
    style = ttk.Style()
    try:
        style.theme_use("vista")
    except Exception:
        pass
    BulkFileTool(root)
    root.mainloop()


if __name__ == "__main__":
    main()
