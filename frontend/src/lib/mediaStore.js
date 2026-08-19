const store = { camera: null, screen: null };

export function setStreams(camera, screen) {
  store.camera = camera;
  store.screen = screen;
}

export function getStreams() {
  return store;
}

export function stopStreams() {
  [store.camera, store.screen].forEach((s) => {
    if (s) s.getTracks().forEach((t) => t.stop());
  });
  store.camera = null;
  store.screen = null;
}
