import { type FormEvent, useRef, useState } from "react";

import { getDeliveryEstimate } from "../api";
import type { DeliveryEstimate } from "../types";

export function DeliveryForm() {
  const requestController = useRef<AbortController | null>(null);
  const [district, setDistrict] = useState("");
  const [estimate, setEstimate] = useState<DeliveryEstimate | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const normalizedDistrict = district.trim();
    if (normalizedDistrict.length < 2) {
      setError("Аудан атауы кемінде 2 таңбадан тұруы керек.");
      setEstimate(null);
      return;
    }

    requestController.current?.abort();
    const controller = new AbortController();
    requestController.current = controller;
    setLoading(true);
    setError(null);
    setEstimate(null);

    try {
      const result = await getDeliveryEstimate(
        normalizedDistrict,
        controller.signal,
      );
      setEstimate(result);
    } catch (requestError) {
      if (requestError instanceof DOMException && requestError.name === "AbortError") {
        return;
      }
      setError(
        requestError instanceof Error
          ? requestError.message
          : "Белгісіз қате орын алды.",
      );
    } finally {
      if (requestController.current === controller) setLoading(false);
    }
  }

  return (
    <section
      aria-labelledby="delivery-title"
      className="self-start rounded-3xl bg-emerald-950 p-5 text-white shadow-[0_24px_70px_rgba(6,78,59,0.2)] sm:p-7 lg:sticky lg:top-6"
    >
      <p className="mb-1 text-sm font-bold uppercase tracking-[0.18em] text-emerald-300">
        Жеткізу
      </p>
      <h2 id="delivery-title" className="text-2xl font-extrabold tracking-tight">
        Мерзімді есептеу
      </h2>
      <p className="mt-2 text-sm leading-6 text-emerald-100">
        Аудан атауын енгізіңіз, сервис болжамды жеткізу уақытын көрсетеді.
      </p>

      <form className="mt-6 grid gap-3" onSubmit={handleSubmit}>
        <label htmlFor="district" className="font-bold text-emerald-50">
          Аудан атауы
        </label>
        <input
          id="district"
          name="district"
          value={district}
          onChange={(event) => setDistrict(event.target.value)}
          minLength={2}
          maxLength={80}
          placeholder="Мысалы: Есіл"
          autoComplete="address-level-2"
          required
          className="min-h-12 w-full rounded-xl border border-white/20 bg-white px-4 text-base text-slate-950 outline-none transition placeholder:text-slate-400 focus:border-emerald-300 focus:ring-4 focus:ring-emerald-300/25"
        />
        <p className="text-sm leading-5 text-emerald-100">
          Алматы, Байқоңыр, Есіл, Нұра, Сарайшық немесе Сарыарқа.
        </p>
        <button
          type="submit"
          disabled={loading}
          className="min-h-12 rounded-xl bg-emerald-400 px-4 font-extrabold text-emerald-950 transition hover:bg-emerald-300 focus:outline-none focus:ring-4 focus:ring-emerald-300/30 disabled:cursor-wait disabled:opacity-70"
        >
          {loading ? "Есептелуде..." : "Есептеу"}
        </button>
      </form>

      <div aria-live="polite" className="mt-4">
        {estimate && (
          <div className="rounded-2xl border border-emerald-300/30 bg-emerald-400/15 p-4">
            <p className="break-words font-bold text-emerald-50">
              {estimate.district}
            </p>
            <p className="mt-1 text-emerald-100">
              Жеткізу мерзімі — {estimate.days} күн.
            </p>
          </div>
        )}
        {error && (
          <div
            role="alert"
            className="break-words rounded-2xl border border-red-300/30 bg-red-400/15 p-4 text-red-100"
          >
            {error}
          </div>
        )}
      </div>
    </section>
  );
}

