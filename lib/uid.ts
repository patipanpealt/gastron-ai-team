/** crypto.randomUUID only exists on https / localhost; on a phone opening http://192.168.x.x it is missing, so fall back. */
export function uid(): string {
  if (typeof crypto !== "undefined" && typeof crypto.randomUUID === "function") return crypto.randomUUID();
  return "id-" + Date.now().toString(36) + "-" + Math.random().toString(36).slice(2, 10);
}
