// Simplification volontaire: pas d'appel LLM externe.
// On segmente la durée en 5–8 blocs, génère titres + texte courts.

export function expandPromptToSegments({ prompt, language, totalDurationSec }) {
  const minSeg = 5, maxSeg = 8;
  const segCount = Math.max(minSeg, Math.min(maxSeg, Math.round(totalDurationSec / 15)));
  const base = [
    { title: lang(language, 'Introduction'), body: prompt },
    { title: lang(language, 'Contexte'), body: keyPoints(prompt, 1) },
    { title: lang(language, 'Point clé 1'), body: keyPoints(prompt, 2) },
    { title: lang(language, 'Point clé 2'), body: keyPoints(prompt, 3) },
    { title: lang(language, 'Conseils'), body: lang(language, 'Conseils rapides liés au sujet.') },
    { title: lang(language, 'Résumé'), body: lang(language, 'Récapitulatif des idées essentielles.') },
    { title: lang(language, 'Conclusion'), body: lang(language, 'Conclusion brève et appel à l’action.') }
  ];
  const picked = base.slice(0, segCount);
  const segDur = Math.floor(totalDurationSec / picked.length);
  let t = 0;
  return picked.map((s, i) => {
    const d = i === picked.length - 1 ? (totalDurationSec - t) : segDur;
    const text = `${s.title}: ${s.body}`;
    const seg = { index: i + 1, start: t, end: t + d, duration: d, text, title: s.title };
    t += d;
    return seg;
  });
}

function keyPoints(prompt, n) {
  return `Aspect ${n} de « ${prompt} ».`;
}

function lang(l, str) {
  const map = {
    fr: {
      'Introduction': 'Introduction',
      'Contexte': 'Contexte',
      'Point clé 1': 'Point clé 1',
      'Point clé 2': 'Point clé 2',
      'Conseils': 'Conseils',
      'Résumé': 'Résumé',
      'Conclusion': 'Conclusion',
      'Conseils rapides liés au sujet.': 'Conseils rapides liés au sujet.',
      'Récapitulatif des idées essentielles.': 'Récapitulatif des idées essentielles.',
      'Conclusion brève et appel à l’action.': 'Conclusion brève et appel à l’action.'
    },
    en: {
      'Introduction': 'Introduction',
      'Contexte': 'Background',
      'Point clé 1': 'Key point 1',
      'Point clé 2': 'Key point 2',
      'Conseils': 'Tips',
      'Résumé': 'Summary',
      'Conclusion': 'Conclusion',
      'Conseils rapides liés au sujet.': 'Quick tips related to the topic.',
      'Récapitulatif des idées essentielles.': 'Recap of the essentials.',
      'Conclusion brève et appel à l’action.': 'Brief conclusion and call to action.'
    },
    es: {
      'Introduction': 'Introducción',
      'Contexte': 'Contexto',
      'Point clé 1': 'Punto clave 1',
      'Point clé 2': 'Punto clave 2',
      'Conseils': 'Consejos',
      'Résumé': 'Resumen',
      'Conclusion': 'Conclusión',
      'Conseils rapides liés au sujet.': 'Consejos rápidos relacionados con el tema.',
      'Récapitulatif des idées essentielles.': 'Resumen de lo esencial.',
      'Conclusion brève et appel à l’action.': 'Conclusión breve y llamado a la acción.'
    },
    de: {
      'Introduction': 'Einleitung',
      'Contexte': 'Kontext',
      'Point clé 1': 'Schlüsselpunkt 1',
      'Point clé 2': 'Schlüsselpunkt 2',
      'Conseils': 'Tipps',
      'Résumé': 'Zusammenfassung',
      'Conclusion': 'Fazit',
      'Conseils rapides liés au sujet.': 'Schnelle Tipps zum Thema.',
      'Récapitulatif des idées essentielles.': 'Zusammenfassung der wichtigsten Punkte.',
      'Conclusion brève et appel à l’action.': 'Kurzes Fazit und Handlungsaufforderung.'
    }
  };
  return (map[l]?.[str]) ?? str;
}
