import { useMemo } from 'react';
import type { JTBDResult } from '../types';

export interface JTBDCategoryData {
  title: string;
  icon: string;
  color: string;
  items: Array<{
    primary: string;
    secondary?: string;
    context?: string;
    quote?: string;
  }>;
}

export const useJTBD = (jtbd: JTBDResult | undefined) => {
  const categories = useMemo((): JTBDCategoryData[] => {
    if (!jtbd) return [];

    const result: JTBDCategoryData[] = [];

    // Jobs category
    if (jtbd.jobs && jtbd.jobs.length > 0) {
      result.push({
        title: 'Jobs (Работы)',
        icon: '💼',
        color: '#3b82f6',
        items: jtbd.jobs.map((job) => ({
          primary: job.job,
          secondary: job.outcome,
          context: job.context,
          quote: job.quote,
        })),
      });
    }

    // Pains category
    if (jtbd.pains && jtbd.pains.length > 0) {
      result.push({
        title: 'Pains (Боли)',
        icon: '😰',
        color: '#ef4444',
        items: jtbd.pains.map((pain) => ({
          primary: pain.pain,
          secondary: pain.severity,
          context: pain.context,
          quote: pain.quote,
        })),
      });
    }

    // Gains category
    if (jtbd.gains && jtbd.gains.length > 0) {
      result.push({
        title: 'Gains (Выгоды)',
        icon: '✨',
        color: '#10b981',
        items: jtbd.gains.map((gain) => ({
          primary: gain.gain,
          secondary: gain.value,
          context: gain.context,
          quote: gain.quote,
        })),
      });
    }

    return result;
  }, [jtbd]);

  const totalElements = useMemo(() => {
    return categories.reduce((sum, cat) => sum + cat.items.length, 0);
  }, [categories]);

  const hasData = categories.length > 0;

  return {
    categories,
    totalElements,
    hasData,
  };
};
