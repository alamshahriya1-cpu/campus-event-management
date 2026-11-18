"use strict";
const feedback = document.getElementById("feedback");
function showError(message) {
  feedback.textContent = message;
  feedback.hidden = false;
}
async function api(url, method = "POST", data = {}) {
  const response = await fetch(url, {
    method, credentials: "same-origin",
    headers: {"Content-Type": "application/json", "X-CSRFToken": document.querySelector('meta[name="csrf-token"]').content},
    body: JSON.stringify(data),
  });
  let payload;
  try { payload = await response.json(); }
  catch { throw new Error("The server could not complete this request. Refresh the page and try again."); }
  if (!response.ok) throw new Error(payload.error || "The change could not be saved.");
  return payload;
}
async function withButton(button, action) {
  button.disabled = true;
  const label = button.textContent;
  button.textContent = "Saving…";
  feedback.hidden = true;
  try { await action(); }
  catch (error) { showError(error.message || "Connection lost. Refresh to check your status before retrying."); }
  finally { button.disabled = false; button.textContent = label; }
}
document.querySelectorAll("[data-api]").forEach(button => {
  button.addEventListener("click", () => {
    if (button.dataset.confirm && !window.confirm(button.dataset.confirm)) return;
    withButton(button, async () => { await api(button.dataset.api); window.location.reload(); });
  });
});
document.querySelectorAll("[data-attendance]").forEach(button => {
  button.addEventListener("click", () => withButton(button, async () => {
    await api(`/api/registrations/${button.dataset.attendance}/attendance/`, "PATCH", {attended: button.dataset.attended === "true"});
    window.location.reload();
  }));
});
const eventForm = document.getElementById("event-form");
if (eventForm) eventForm.addEventListener("submit", event => {
  event.preventDefault();
  withButton(eventForm.querySelector('[type="submit"]'), async () => {
    const data = Object.fromEntries(new FormData(eventForm));
    if (eventForm.dataset.published !== "true") {
      data.capacity = Number(data.capacity);
      // Input labels explicitly require KST, independent of the browser's timezone.
      for (const key of ["start_at", "end_at", "registration_closes_at"]) {
        data[key] = new Date(data[key] + "+09:00").toISOString();
      }
    }
    const id = eventForm.dataset.eventId;
    const result = await api(id ? `/api/events/${id}/` : "/api/events/", id ? "PATCH" : "POST", data);
    window.location.assign(`/events/${result.id}/`);
  });
});
document.querySelectorAll("[data-cancel-event]").forEach(form => {
  form.addEventListener("submit", event => {
    event.preventDefault();
    if (!window.confirm("Cancel this event and every active registration? Participants will see your reason.")) return;
    withButton(form.querySelector("button"), async () => {
      await api(`/api/events/${form.dataset.cancelEvent}/cancel/`, "POST", {reason: new FormData(form).get("reason")});
      window.location.reload();
    });
  });
});
