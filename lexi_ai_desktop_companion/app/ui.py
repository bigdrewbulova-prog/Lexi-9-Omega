from __future__ import annotations

import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk
import json

from .security import OpenVASManager

from .controller import LexiController
from .models import GeneratedBundle


class LexiApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()

        self.title("Lexi.AI Desktop Companion — The Beginning Of Life — The Geometry Of The Now")
        self.geometry("1180x780")
        self.minsize(980, 640)

        self.controller = LexiController()
        self.security_manager = OpenVASManager(self.controller.memory)
        self.active_bundle: GeneratedBundle | None = None
        self.auto_job: str | None = None

        self.project_name_var = tk.StringVar(value="core")
        self.auto_enabled_var = tk.BooleanVar(value=False)
        self.auto_interval_var = tk.StringVar(value="180")
        self.status_var = tk.StringVar(value="Lexi local template engine ready.")
        self.workspace_root_var = tk.StringVar(value=self.controller.app_paths()["workspaces_dir"])

        self._configure_style()
        self._build_layout()
        self._refresh_status_panel()

    def _configure_style(self) -> None:
        self.configure(bg="#111316")
        style = ttk.Style(self)
        style.theme_use("clam")

        style.configure("TFrame", background="#e8e5dc")
        style.configure("Root.TFrame", background="#e8e5dc")
        style.configure("Dark.TFrame", background="#111316")
        style.configure("TLabel", background="#e8e5dc", foreground="#1c1c1c", font=("Helvetica", 11))
        style.configure("Header.TLabel", font=("Helvetica", 17, "bold"))
        style.configure("Subheader.TLabel", font=("Helvetica", 10, "bold"))
        style.configure("TButton", padding=8, font=("Helvetica", 10, "bold"))
        style.configure("TNotebook", background="#d8d4ca")
        style.configure("TNotebook.Tab", padding=(14, 8), font=("Helvetica", 10, "bold"))

    def _build_layout(self) -> None:
        root = ttk.Frame(self, style="Root.TFrame", padding=14)
        root.pack(fill=tk.BOTH, expand=True)

        header = ttk.Frame(root)
        header.pack(fill=tk.X)

        title_block = ttk.Frame(header)
        title_block.pack(side=tk.LEFT, fill=tk.X, expand=True)

        ttk.Label(title_block, text="Lexi.AI Desktop Companion", style="Header.TLabel").pack(anchor="w")
        ttk.Label(
            title_block,
            text="The Beginning Of Life — The Geometry Of The Now",
            style="Subheader.TLabel",
        ).pack(anchor="w", pady=(2, 8))

        paths_btn = ttk.Button(header, text="Show Local Paths", command=self._show_paths)
        paths_btn.pack(side=tk.RIGHT, padx=(8, 0))

        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        self._build_lexi_live_tab()
        self._build_disk_tab()
        self._build_architecture_tab()
        self._build_settings_tab()
        self._build_security_tab()

        status = ttk.Label(root, textvariable=self.status_var, anchor="w")
        status.pack(fill=tk.X, pady=(8, 0))

    def _build_lexi_live_tab(self) -> None:
        tab = ttk.Frame(self.notebook, padding=14)
        self.notebook.add(tab, text="Lexi Live")

        ttk.Label(tab, text="Live generated project note:").pack(anchor="w")

        self.live_output = tk.Text(
            tab,
            height=22,
            wrap=tk.WORD,
            bg="#171a1f",
            fg="#f1f4f8",
            insertbackground="#f1f4f8",
            relief=tk.FLAT,
            font=("Menlo", 12),
        )
        self.live_output.pack(fill=tk.BOTH, expand=True, pady=(6, 8))

        row = ttk.Frame(tab)
        row.pack(fill=tk.X)

        ttk.Button(row, text="Generate Project Note", command=self._generate_project_note).pack(side=tk.LEFT)
        ttk.Button(row, text="Generate Auto Draft Now", command=self._generate_auto_draft_once).pack(side=tk.LEFT, padx=8)
        ttk.Button(row, text="Clear Live Output", command=lambda: self._replace_text(self.live_output, "")).pack(
            side=tk.LEFT
        )

    def _build_disk_tab(self) -> None:
        tab = ttk.Frame(self.notebook, padding=14)
        self.notebook.add(tab, text="Disk Command Center")

        ttk.Label(tab, text="Workspace root:").pack(anchor="w")
        root_row = ttk.Frame(tab)
        root_row.pack(fill=tk.X, pady=(4, 10))

        ttk.Entry(root_row, textvariable=self.workspace_root_var).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(root_row, text="Choose Folder", command=self._choose_workspace_root).pack(side=tk.LEFT, padx=8)
        ttk.Button(root_row, text="Apply Root", command=self._apply_workspace_root).pack(side=tk.LEFT)

        ttk.Label(tab, text="Workspace preview:").pack(anchor="w")

        self.workspace_preview = tk.Text(
            tab,
            height=20,
            wrap=tk.NONE,
            bg="#171a1f",
            fg="#f1f4f8",
            insertbackground="#f1f4f8",
            relief=tk.FLAT,
            font=("Menlo", 12),
        )
        self.workspace_preview.pack(fill=tk.BOTH, expand=True, pady=(6, 8))

        row = ttk.Frame(tab)
        row.pack(fill=tk.X)

        ttk.Button(row, text="Preview Workspace Files", command=self._preview_workspace).pack(side=tk.LEFT)
        ttk.Button(row, text="Create Workspace", command=self._create_workspace).pack(side=tk.LEFT, padx=8)

        warning = (
            "Safety: Lexi creates folders/files only after confirmation. "
            "No delete, no shell execution, no silent overwrite."
        )
        ttk.Label(tab, text=warning).pack(anchor="w", pady=(10, 0))

    def _build_architecture_tab(self) -> None:
        tab = ttk.Frame(self.notebook, padding=14)
        self.notebook.add(tab, text="Architecture Lab")

        form = ttk.Frame(tab)
        form.pack(fill=tk.X)

        ttk.Label(form, text="Project name:").pack(side=tk.LEFT)
        ttk.Entry(form, textvariable=self.project_name_var, width=48).pack(side=tk.LEFT, padx=8, fill=tk.X, expand=True)

        ttk.Button(form, text="Save Note", command=self._save_note).pack(side=tk.RIGHT)
        ttk.Button(form, text="Generate Brief", command=self._generate_brief).pack(side=tk.RIGHT, padx=8)
        ttk.Button(form, text="Create Workspace", command=self._create_workspace).pack(side=tk.RIGHT)

        ttk.Label(tab, text="Project notes / design signal:").pack(anchor="w", pady=(12, 4))

        self.notes_input = tk.Text(
            tab,
            height=13,
            wrap=tk.WORD,
            bg="#15171b",
            fg="#f6f6f3",
            insertbackground="#f6f6f3",
            relief=tk.FLAT,
            font=("Menlo", 12),
        )
        self.notes_input.pack(fill=tk.BOTH, expand=True)
        self.notes_input.insert(
            "1.0",
            "design Lexi.AI Desktop dashboard\n"
            "Core principle: safe control, clean geometry, owner-approved file actions.\n"
            "First build: local template-based generator only.\n",
        )

        ttk.Label(tab, text="Generated brief:").pack(anchor="w", pady=(12, 4))

        self.brief_output = tk.Text(
            tab,
            height=14,
            wrap=tk.WORD,
            bg="#15171b",
            fg="#f6f6f3",
            insertbackground="#f6f6f3",
            relief=tk.FLAT,
            font=("Menlo", 12),
        )
        self.brief_output.pack(fill=tk.BOTH, expand=True)

    def _build_settings_tab(self) -> None:
        tab = ttk.Frame(self.notebook, padding=14)
        self.notebook.add(tab, text="Settings / Android Bridge")

        ttk.Label(tab, text="Autonomous draft mode").pack(anchor="w")

        auto_row = ttk.Frame(tab)
        auto_row.pack(fill=tk.X, pady=(8, 8))

        ttk.Checkbutton(
            auto_row,
            text="Enable automatic design-signal drafts",
            variable=self.auto_enabled_var,
            command=self._toggle_auto_mode,
        ).pack(side=tk.LEFT)

        ttk.Label(auto_row, text="Interval seconds:").pack(side=tk.LEFT, padx=(18, 6))
        ttk.Entry(auto_row, textvariable=self.auto_interval_var, width=8).pack(side=tk.LEFT)

        info = (
            "Auto mode generates draft notes/signals and saves them to Lexi memory. "
            "It does not create workspace files, delete files, overwrite files, or run commands."
        )
        ttk.Label(tab, text=info, wraplength=900).pack(anchor="w", pady=(4, 14))

        ttk.Label(tab, text="Project status:").pack(anchor="w")

        self.status_panel = tk.Text(
            tab,
            height=22,
            wrap=tk.WORD,
            bg="#171a1f",
            fg="#f1f4f8",
            insertbackground="#f1f4f8",
            relief=tk.FLAT,
            font=("Menlo", 12),
        )
        self.status_panel.pack(fill=tk.BOTH, expand=True, pady=(6, 8))

        row = ttk.Frame(tab)
        row.pack(fill=tk.X)

        ttk.Button(row, text="Refresh Status", command=self._refresh_status_panel).pack(side=tk.LEFT)
        ttk.Button(row, text="Show Local Paths", command=self._show_paths).pack(side=tk.LEFT, padx=8)

        ttk.Label(
            tab,
            text="Android Bridge placeholder: this build intentionally does not run ADB or shell commands.",
            wraplength=900,
        ).pack(anchor="w", pady=(12, 0))

    def _build_security_tab(self) -> None:
        tab = ttk.Frame(self.notebook, padding=14)
        self.notebook.add(tab, text="Security")

        ttk.Label(tab, text="OpenVAS Scan (Docker) — owner approval required").pack(anchor="w")

        form = ttk.Frame(tab)
        form.pack(fill=tk.X, pady=(6, 6))

        ttk.Label(form, text="Target (IP/host):").pack(side=tk.LEFT)
        self.scan_target_var = tk.StringVar(value="127.0.0.1")
        ttk.Entry(form, textvariable=self.scan_target_var, width=36).pack(side=tk.LEFT, padx=8)

        ttk.Label(form, text="Template:").pack(side=tk.LEFT, padx=(8, 0))
        self.scan_template_var = tk.StringVar(value="Full and fast")
        ttk.Entry(form, textvariable=self.scan_template_var, width=24).pack(side=tk.LEFT, padx=8)

        row = ttk.Frame(tab)
        row.pack(fill=tk.X, pady=(8, 0))

        ttk.Button(row, text="Preview Scan", command=self._preview_scan).pack(side=tk.LEFT)
        ttk.Button(row, text="Request Scan", command=self._request_scan).pack(side=tk.LEFT, padx=8)

        self.security_output = tk.Text(
            tab,
            height=12,
            wrap=tk.WORD,
            bg="#15171b",
            fg="#f6f6f3",
            insertbackground="#f6f6f3",
            relief=tk.FLAT,
            font=("Menlo", 11),
        )
        self.security_output.pack(fill=tk.BOTH, expand=True, pady=(8, 0))

    def _project_name(self) -> str:
        return self.project_name_var.get().strip()

    def _notes_text(self) -> str:
        return self.notes_input.get("1.0", tk.END).strip()

    def _replace_text(self, widget: tk.Text, text: str) -> None:
        widget.delete("1.0", tk.END)
        widget.insert("1.0", text)

    def _append_text(self, widget: tk.Text, text: str) -> None:
        widget.insert(tk.END, text + "\n")
        widget.see(tk.END)

    def _set_status(self, text: str) -> None:
        self.status_var.set(text)
        self._refresh_status_panel()

    def _save_note(self) -> None:
        try:
            message = self.controller.save_note(self._project_name(), self._notes_text())
            self._set_status(message)
        except Exception as exc:
            messagebox.showerror("Save Note Failed", str(exc))

    def _generate_project_note(self) -> None:
        try:
            note = self.controller.generate_project_note(self._project_name(), self._notes_text())
            self._replace_text(self.live_output, note)
            self._set_status("Generated and saved project note.")
        except Exception as exc:
            messagebox.showerror("Generate Note Failed", str(exc))

    def _generate_brief(self) -> None:
        try:
            bundle = self.controller.generate_bundle(self._project_name(), self._notes_text())
            self.active_bundle = bundle
            output = f"{bundle.brief}\n\n\n---\n\n{bundle.signal}"
            self._replace_text(self.brief_output, output)
            self._replace_text(self.live_output, bundle.note)
            self._set_status("Generated note, design signal, brief, and task list.")
        except Exception as exc:
            messagebox.showerror("Generate Brief Failed", str(exc))

    def _preview_workspace(self) -> None:
        try:
            files = self.controller.preview_workspace(self._project_name())
            self._replace_text(self.workspace_preview, "\n".join(files))
            self._set_status("Workspace preview generated.")
        except Exception as exc:
            messagebox.showerror("Preview Failed", str(exc))

    def _create_workspace(self) -> None:
        try:
            if self.active_bundle is None:
                self.active_bundle = self.controller.generate_bundle(self._project_name(), self._notes_text())
                self._replace_text(self.brief_output, self.active_bundle.brief)

            files = self.controller.preview_workspace(self._project_name())
            preview = "\n".join(files)
            approved = messagebox.askyesno(
                "Owner Approval Required",
                "Lexi will create a safe workspace with these files:\n\n"
                f"{preview}\n\n"
                "Existing files will not be overwritten; versioned files will be created instead.\n\n"
                "Create workspace now?",
            )

            if not approved:
                self._set_status("Workspace creation cancelled by owner.")
                return

            result = self.controller.create_workspace(self.active_bundle)
            self._replace_text(
                self.workspace_preview,
                f"{result.message}\n\nWritten files:\n" + "\n".join(result.written_files),
            )
            self._set_status(result.message)
            messagebox.showinfo("Workspace Created", result.message)
        except Exception as exc:
            messagebox.showerror("Create Workspace Failed", str(exc))

    def _choose_workspace_root(self) -> None:
        chosen = filedialog.askdirectory(title="Choose Lexi workspace root")
        if chosen:
            self.workspace_root_var.set(chosen)

    def _apply_workspace_root(self) -> None:
        try:
            from .workspace_manager import WorkspaceManager

            root = Path(self.workspace_root_var.get()).expanduser()
            root.mkdir(parents=True, exist_ok=True)
            self.controller.workspace_manager = WorkspaceManager(root)
            self.controller.memory.workspaces_dir = root
            self._set_status(f"Workspace root set to {root}")
        except Exception as exc:
            messagebox.showerror("Workspace Root Failed", str(exc))

    def _generate_auto_draft_once(self) -> None:
        try:
            draft = self.controller.generate_auto_draft(self._project_name(), self._notes_text())
            self._replace_text(self.live_output, draft)
            self._set_status("Auto draft generated and saved to local memory.")
        except Exception as exc:
            messagebox.showerror("Auto Draft Failed", str(exc))

    def _toggle_auto_mode(self) -> None:
        if self.auto_enabled_var.get():
            self._set_status("Autonomous draft mode enabled.")
            self._schedule_auto_tick()
        else:
            if self.auto_job is not None:
                self.after_cancel(self.auto_job)
                self.auto_job = None
            self._set_status("Autonomous draft mode disabled.")

    def _schedule_auto_tick(self) -> None:
        if not self.auto_enabled_var.get():
            return

        try:
            seconds = max(30, int(self.auto_interval_var.get()))
        except ValueError:
            seconds = 180
            self.auto_interval_var.set(str(seconds))

        self.auto_job = self.after(seconds * 1000, self._auto_tick)

    def _auto_tick(self) -> None:
        if not self.auto_enabled_var.get():
            return

        try:
            draft = self.controller.generate_auto_draft(self._project_name(), self._notes_text())
            self._replace_text(self.live_output, draft)
            self._set_status("Autonomous draft generated. No workspace files changed.")
        except Exception as exc:
            self._set_status(f"Auto draft skipped: {exc}")

        self._schedule_auto_tick()

    def _show_paths(self) -> None:
        paths = self.controller.app_paths()
        message = "\n".join(f"{key}: {value}" for key, value in paths.items())
        messagebox.showinfo("Lexi Local Paths", message)

    def _refresh_status_panel(self) -> None:
        if not hasattr(self, "status_panel"):
            return

        try:
            summary = self.controller.project_summary(self._project_name())
            paths = self.controller.app_paths()
            text = (
                "# Lexi Status\n\n"
                f"Project: {summary['project_name']}\n"
                f"Slug: {summary['slug']}\n"
                f"Notes: {summary['notes']}\n"
                f"Signals: {summary['signals']}\n"
                f"Briefs: {summary['briefs']}\n"
                f"Drafts: {summary['drafts']}\n"
                f"Workspaces: {summary['workspaces']}\n"
                f"Updated: {summary['updated_at']}\n\n"
                "# Local Paths\n\n"
                + "\n".join(f"{key}: {value}" for key, value in paths.items())
                + "\n\n# Current Status\n\n"
                + self.status_var.get()
            )
            self._replace_text(self.status_panel, text)
        except Exception:
            pass

    def _preview_scan(self) -> None:
        try:
            target = self.scan_target_var.get().strip()
            template = self.scan_template_var.get().strip()
            plan = self.security_manager.preview_scan(self._project_name(), target, template)
            self._replace_text(self.security_output, json.dumps(plan, indent=2))
            self._set_status("Scan preview generated. No actions taken.")
        except Exception as exc:
            messagebox.showerror("Preview Failed", str(exc))

    def _request_scan(self) -> None:
        try:
            target = self.scan_target_var.get().strip()
            template = self.scan_template_var.get().strip()
            plan = self.security_manager.prepare_scan(self._project_name(), target, template)
            approved = messagebox.askyesno(
                "Owner Approval Required",
                "Lexi will request a scan with the following plan:\n\n"
                f"{json.dumps(plan, indent=2)}\n\n"
                "Do you approve requesting the scan (the scan will not run automatically)?",
            )

            if not approved:
                self.controller.memory.log_event("scan_request_cancelled", {"project": self._project_name(), "target": target})
                self._set_status("Scan request cancelled by owner.")
                return

            result = self.security_manager.request_scan(self._project_name(), target, template, owner_approved=True)
            self._replace_text(self.security_output, json.dumps(result, indent=2))
            self.controller.memory.log_event("scan_requested_owner_approved", {"project": self._project_name(), "scan": result.get("scan_id")})
            self._set_status("Scan requested (simulated start logged). Check exports after scan finishes.")
        except Exception as exc:
            messagebox.showerror("Scan Request Failed", str(exc))


def run_app() -> None:
    app = LexiApp()
    app.mainloop()
