use tauri_plugin_shell::ShellExt;

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
  tauri::Builder::default()
    .plugin(tauri_plugin_shell::init())
    .setup(|app| {
      // Start Django sidecar — Vue's loading screen polls the API and shows
      // content only once Django responds, so no Rust-side polling is needed.
      let (mut rx, _child) = app.shell().sidecar("feed_calc_api").unwrap().spawn().unwrap();

      tauri::async_runtime::spawn(async move {
        while let Some(event) = rx.recv().await {
          match event {
            tauri_plugin_shell::process::CommandEvent::Stdout(line) =>
              println!("[backend stdout] {}", String::from_utf8_lossy(&line)),
            tauri_plugin_shell::process::CommandEvent::Stderr(line) =>
              eprintln!("[backend stderr] {}", String::from_utf8_lossy(&line)),
            _ => {}
          }
        }
      });


      Ok(())
    })
    .run(tauri::generate_context!())
    .expect("error while running tauri application");
}
