use std::process::{Child, Command};
use std::sync::Mutex;
use tauri::{Manager, State};

// ── Backend process state ─────────────────────────────────────────────────────

struct BackendProcess(Mutex<Option<Child>>);

// ── Commands ──────────────────────────────────────────────────────────────────

/// Spawn the FastAPI backend (uvicorn) if not already running.
/// Returns `Ok(true)` when newly started, `Ok(false)` when already running,
/// `Err(msg)` when uvicorn is not on PATH or the spawn fails.
#[tauri::command]
fn launch_backend(backend: State<BackendProcess>) -> Result<bool, String> {
    let mut guard = backend.0.lock().unwrap();
    if guard.is_some() {
        return Ok(false);
    }

    let child = Command::new("uvicorn")
        .args([
            "algorithm_atlas.main:app",
            "--host", "127.0.0.1",
            "--port", "8000",
            "--app-dir", "apps/backend",
        ])
        .spawn()
        .map_err(|e| format!("Could not start backend: {e}"))?;

    *guard = Some(child);
    Ok(true)
}

/// Kill the managed backend process.
#[tauri::command]
fn kill_backend(backend: State<BackendProcess>) {
    if let Ok(mut guard) = backend.0.lock() {
        if let Some(mut child) = guard.take() {
            let _ = child.kill();
            let _ = child.wait();
        }
    }
}

/// Return whether the managed backend process is alive.
#[tauri::command]
fn backend_running(backend: State<BackendProcess>) -> bool {
    if let Ok(mut guard) = backend.0.lock() {
        if let Some(ref mut child) = *guard {
            // try_wait: Ok(None) means still running
            return matches!(child.try_wait(), Ok(None));
        }
    }
    false
}

// ── App entry ─────────────────────────────────────────────────────────────────

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_shell::init())
        .manage(BackendProcess(Mutex::new(None)))
        .invoke_handler(tauri::generate_handler![
            launch_backend,
            kill_backend,
            backend_running,
        ])
        .on_window_event(|window, event| {
            if let tauri::WindowEvent::Destroyed = event {
                // Kill the backend when the last window closes.
                if let Some(s) = window.try_state::<BackendProcess>() {
                    if let Ok(mut guard) = s.0.lock() {
                        if let Some(mut child) = guard.take() {
                            let _ = child.kill();
                            let _ = child.wait();
                        }
                    }
                }
            }
        })
        .run(tauri::generate_context!())
        .expect("error while running Algorithm Atlas desktop app");
}
