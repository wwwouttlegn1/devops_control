import type { Medicine } from "../types";

interface MedicineListProps {
  medicines: Medicine[];
  loading: boolean;
  error: string | null;
  onRetry: () => void;
}

const moneyFormatter = new Intl.NumberFormat("kk-KZ", {
  minimumFractionDigits: 2,
  maximumFractionDigits: 2,
});

export function MedicineList({
  medicines,
  loading,
  error,
  onRetry,
}: MedicineListProps) {
  return (
    <section
      aria-labelledby="medicines-title"
      className="rounded-3xl border border-emerald-950/10 bg-white p-5 shadow-[0_20px_60px_rgba(6,78,59,0.08)] sm:p-7"
    >
      <div className="mb-5 flex flex-wrap items-center justify-between gap-3">
        <div>
          <p className="mb-1 text-sm font-bold uppercase tracking-[0.18em] text-emerald-700">
            Қойма
          </p>
          <h2
            id="medicines-title"
            className="text-2xl font-extrabold tracking-tight text-slate-900"
          >
            Дәрілер тізімі
          </h2>
        </div>
        {!loading && !error && (
          <span className="rounded-full bg-emerald-50 px-3 py-1.5 text-sm font-bold text-emerald-800">
            {medicines.length} атау
          </span>
        )}
      </div>

      {loading && (
        <div className="grid gap-3" aria-live="polite" aria-label="Жүктелуде">
          {[0, 1, 2].map((item) => (
            <div
              key={item}
              className="h-24 animate-pulse rounded-2xl bg-slate-100"
            />
          ))}
        </div>
      )}

      {!loading && error && (
        <div
          role="alert"
          className="rounded-2xl border border-red-200 bg-red-50 p-5 text-red-900"
        >
          <p className="font-bold">Дәрілерді жүктеу мүмкін болмады.</p>
          <p className="mt-1 break-words text-sm text-red-700">{error}</p>
          <button
            type="button"
            onClick={onRetry}
            className="mt-4 min-h-11 rounded-xl bg-red-700 px-4 py-2 font-bold text-white transition hover:bg-red-800 focus:outline-none focus:ring-4 focus:ring-red-200"
          >
            Қайталап көру
          </button>
        </div>
      )}

      {!loading && !error && medicines.length === 0 && (
        <div className="rounded-2xl border border-dashed border-slate-300 p-8 text-center text-slate-600">
          Дәрілер тізімі әзірге бос.
        </div>
      )}

      {!loading && !error && medicines.length > 0 && (
        <div className="grid gap-3">
          {medicines.map((medicine) => (
            <article
              key={medicine.id}
              className="grid gap-3 rounded-2xl border border-slate-200 p-4 transition hover:border-emerald-300 hover:bg-emerald-50/40 sm:grid-cols-[minmax(0,1fr)_auto] sm:items-center"
            >
              <div className="min-w-0">
                <h3 className="break-words text-lg font-extrabold text-slate-900">
                  {medicine.name}
                </h3>
                <div className="mt-2 flex flex-wrap items-center gap-2 text-sm text-slate-600">
                  <span>Қалдық: {medicine.quantity}</span>
                  {medicine.prescription && (
                    <span className="rounded-full bg-amber-100 px-2.5 py-1 font-bold text-amber-900">
                      Рецепт қажет
                    </span>
                  )}
                </div>
              </div>
              <p className="whitespace-nowrap text-lg font-black text-emerald-800">
                {moneyFormatter.format(Number(medicine.price))} ₸
              </p>
            </article>
          ))}
        </div>
      )}
    </section>
  );
}

