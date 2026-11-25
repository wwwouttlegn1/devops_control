import { useCallback, useEffect, useState } from "react";

import { getMedicines } from "./api";
import { DeliveryForm } from "./components/DeliveryForm";
import { MedicineList } from "./components/MedicineList";
import type { Medicine } from "./types";

export default function App() {
  const [medicines, setMedicines] = useState<Medicine[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [requestVersion, setRequestVersion] = useState(0);

  const retry = useCallback(() => {
    setRequestVersion((version) => version + 1);
  }, []);

  useEffect(() => {
    const controller = new AbortController();
    setLoading(true);
    setError(null);

    getMedicines(controller.signal)
      .then(setMedicines)
      .catch((requestError: unknown) => {
        if (requestError instanceof DOMException && requestError.name === "AbortError") {
          return;
        }
        setError(
          requestError instanceof Error
            ? requestError.message
            : "Белгісіз қате орын алды.",
        );
      })
      .finally(() => {
        if (!controller.signal.aborted) setLoading(false);
      });

    return () => controller.abort();
  }, [requestVersion]);

  return (
    <div className="min-h-screen bg-[#f3f8f6] text-slate-900">
      <header className="overflow-hidden bg-emerald-900 text-white">
        <div className="mx-auto grid w-full max-w-7xl gap-8 px-4 py-12 sm:px-6 sm:py-16 lg:grid-cols-[minmax(0,1fr)_auto] lg:items-end lg:px-8">
          <div>
            <p className="mb-3 text-sm font-bold uppercase tracking-[0.2em] text-emerald-300">
              DevOps бақылау · 5-нұсқа
            </p>
            <h1 className="text-4xl font-black tracking-[-0.04em] sm:text-5xl lg:text-6xl">
              Дәріхана
            </h1>
            <p className="mt-4 max-w-2xl text-base leading-7 text-emerald-50 sm:text-lg">
              Қоймадағы дәрілерді қарап, ауданыңыз бойынша жеткізу мерзімін есептеңіз.
            </p>
          </div>
          <div className="w-fit rounded-2xl border border-white/15 bg-white/10 px-4 py-3 backdrop-blur">
            <p className="text-sm text-emerald-100">Жүйе күйі</p>
            <p className="mt-1 font-extrabold text-white">API арқылы онлайн</p>
          </div>
        </div>
      </header>

      <main className="mx-auto grid w-full max-w-7xl gap-6 px-4 py-6 sm:px-6 sm:py-8 lg:grid-cols-[minmax(0,1.55fr)_minmax(320px,0.8fr)] lg:px-8">
        <MedicineList
          medicines={medicines}
          loading={loading}
          error={error}
          onRetry={retry}
        />
        <DeliveryForm />
      </main>
    </div>
  );
}

