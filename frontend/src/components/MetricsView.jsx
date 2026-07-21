import React, { useEffect, useState } from 'react';
import { BarChart2, FileText, Tag, AlertCircle, Ruler } from 'lucide-react';

export default function MetricsView() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch('/api/dataset/stats')
      .then(res => res.json())
      .then(data => {
        setStats(data);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, []);

  return (
    <div className="max-w-4xl mx-auto p-6 space-y-6">
      <div className="space-y-1">
        <h2 className="font-heading font-extrabold text-2xl text-zophia-purple flex items-center gap-2">
          <BarChart2 className="text-zophia-pink" />
          Dataset e Métricas
        </h2>
        <p className="text-sm text-gray-600">
          Visão geral do conjunto de dados de publicações sobre saúde mental utilizado pelo sistema.
        </p>
      </div>

      {loading ? (
        <div className="p-8 text-center text-gray-400">Carregando métricas...</div>
      ) : (
        <>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
            <div className="bg-white p-4 rounded-2xl border border-zophia-border shadow-xs text-center space-y-1">
              <FileText className="w-5 h-5 mx-auto text-zophia-purple" />
              <div className="text-2xl font-extrabold text-zophia-purple">{stats?.records || 1000}</div>
              <div className="text-[11px] text-gray-500 font-medium uppercase">Relatos</div>
            </div>

            <div className="bg-white p-4 rounded-2xl border border-zophia-border shadow-xs text-center space-y-1">
              <Tag className="w-5 h-5 mx-auto text-zophia-pink" />
              <div className="text-2xl font-extrabold text-zophia-purple">{stats?.categories_count || 3}</div>
              <div className="text-[11px] text-gray-500 font-medium uppercase">Categorias</div>
            </div>

            <div className="bg-white p-4 rounded-2xl border border-zophia-border shadow-xs text-center space-y-1">
              <AlertCircle className="w-5 h-5 mx-auto text-emerald-500" />
              <div className="text-2xl font-extrabold text-zophia-purple">{stats?.missing_values || 0}</div>
              <div className="text-[11px] text-gray-500 font-medium uppercase">Ausentes</div>
            </div>

            <div className="bg-white p-4 rounded-2xl border border-zophia-border shadow-xs text-center space-y-1">
              <Ruler className="w-5 h-5 mx-auto text-zophia-purple" />
              <div className="text-2xl font-extrabold text-zophia-purple">{stats?.average_length || 73.45}</div>
              <div className="text-[11px] text-gray-500 font-medium uppercase">Tam. Médio</div>
            </div>
          </div>

          {stats?.categories && (
            <div className="bg-white p-5 rounded-2xl border border-zophia-border shadow-xs space-y-3">
              <h3 className="font-heading font-bold text-sm text-gray-700">Distribuição por Categoria</h3>
              <div className="space-y-2">
                {Object.entries(stats.categories).map(([cat, count]) => {
                  const pct = ((count / stats.records) * 100).toFixed(1);
                  return (
                    <div key={cat} className="space-y-1">
                      <div className="flex justify-between text-xs font-semibold text-gray-700">
                        <span>{cat}</span>
                        <span>{count} ({pct}%)</span>
                      </div>
                      <div className="w-full bg-gray-100 rounded-full h-2 overflow-hidden">
                        <div className="bg-gradient-to-r from-zophia-purple to-zophia-pink h-full rounded-full" style={{ width: `${pct}%` }}></div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
}
