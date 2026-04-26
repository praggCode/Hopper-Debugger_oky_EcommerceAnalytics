const API_BASE_URL = ""; // Relative to the domain serving the frontend

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
