import type { DeliveryEstimate, Medicine } from "./types";

const pharmacyApiUrl =
  import.meta.env.VITE_PHARMACY_API_URL ?? "/api/pharmacy";
const deliveryApiUrl =
  import.meta.env.VITE_DELIVERY_API_URL ?? "/api/delivery";

async function requestJson<T>(url: string, signal?: AbortSignal): Promise<T> {
  const response = await fetch(url, { signal });
  if (!response.ok) {
    let message = `HTTP ${response.status}`;
    try {
      const body = (await response.json()) as { detail?: string };
      if (body.detail) message = body.detail;
    } catch {
      // The status code remains a useful fallback for a non-JSON response.
    }
    throw new Error(message);
  }
  return response.json() as Promise<T>;
}

export function getMedicines(signal?: AbortSignal): Promise<Medicine[]> {
  return requestJson<Medicine[]>(`${pharmacyApiUrl}/medicines`, signal);
}

export function getDeliveryEstimate(
  district: string,
  signal?: AbortSignal,
): Promise<DeliveryEstimate> {
  const query = new URLSearchParams({ district });
  return requestJson<DeliveryEstimate>(
    `${deliveryApiUrl}/estimate?${query.toString()}`,
    signal,
  );
}

