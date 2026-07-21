import React, { useState, useEffect } from 'react';
import { BookOpen, FileText, CheckCircle2 } from 'lucide-react';

export default function DocsView() {
  const docs = [
    {
      title: 'WHO mhGAP',
      desc: 'Programa de Ação para Lacunas em Saúde Mental da Organização Mundial da Saúde.',
      tag: 'Global / OMS'
    },
    {
      title: 'NICE — Depressão & Ansiedade',
      desc: 'Diretrizes clínicas do National Institute for Health and Care Excellence.',
      tag: 'Internacional'
    },
    {
      title: 'Ministério da Saúde (RAPS)',
      desc: 'Rede de Atenção Psicossocial e diretrizes brasileiras de atenção básica.',
      tag: 'Brasil'
    },
    {
      title: 'Material do CVV',
      desc: 'Diretrizes de escuta ativa e prevenção ao suicídio do Centro de Valorização da Vida.',
      tag: 'Escuta Ativa'
    },
    {
      title: 'DSM-5-TR Autorizado',
      desc: 'Manual Diagnóstico e Estatístico de Transtornos Mentais para embasamento técnico.',
      tag: 'Acadêmico'
    }
  ];

  return (
    <div className="max-w-4xl mx-auto p-6 space-y-6">
      <div className="space-y-1">
        <h2 className="font-heading font-extrabold text-2xl text-zophia-purple flex items-center gap-2">
          <BookOpen className="text-zophia-pink" />
          Base Documental
        </h2>
        <p className="text-sm text-gray-600">
          Documentos e protocolos de saúde mental que fundamentam as respostas e diretrizes da Zophia.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {docs.map((doc, idx) => (
          <div key={idx} className="bg-white p-5 rounded-2xl border border-zophia-border shadow-xs space-y-2 hover:border-zophia-pink/30 transition-all">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold text-zophia-purple bg-zophia-purple/10 px-2.5 py-0.5 rounded-full">
                {doc.tag}
              </span>
              <CheckCircle2 size={16} className="text-emerald-500" />
            </div>
            <h3 className="font-heading font-bold text-base text-gray-800">{doc.title}</h3>
            <p className="text-xs text-gray-500 leading-relaxed">{doc.desc}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
