const DEFAULT_HTTP = "http://localhost:8000";

export const backendHttpUrl =
  import.meta.env.VITE_BACKEND_URL?.replace(/\/$/, "") || DEFAULT_HTTP;

export const backendWsUrl =
  import.meta.env.VITE_BACKEND_WS?.replace(/\/$/, "") ||
  backendHttpUrl.replace(/^http/, "ws") + "/ws/detections";
