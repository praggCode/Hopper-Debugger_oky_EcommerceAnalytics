const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || ""; // Use env var for cross-domain (Vercel), else relative (Render)

async function postJson(path, payload) {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify(payload)
  });

  if (!response.ok) {
    throw new Error(`Request failed with status ${response.status}`);
  }

  return response.json();
}

export function fetchLateDeliveryPrediction(payload) {
  return postJson("/predict/late-delivery", payload);
}

export function fetchCustomerSegment(payload) {
  return postJson("/predict/customer-segment", payload);
}
