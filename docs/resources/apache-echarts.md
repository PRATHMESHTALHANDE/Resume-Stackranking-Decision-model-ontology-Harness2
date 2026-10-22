# Resource: Apache ECharts (Model Benchmark & Pareto Visualizations)

## 1. Overview & Purpose
**Apache ECharts** is a powerful, free, open-source data visualization charting library written in TypeScript/JavaScript, incubated and graduated by the Apache Software Foundation.

In the **Resume Intelligence, Ranking & Fairness Lab**, Apache ECharts renders the **Model Research Lab** charts:
- **Pareto Frontier Plot:** Visualizes Ranking Quality ($\text{nDCG}@10$) vs. Inference Latency (ms) vs. Peak Memory Footprint (MB) across BM25, MiniLM, RRF, TOPSIS, and LambdaMART.
- **Metric Breakdown Radar Charts:** Compares models across Precision, Recall, MRR, Calibration, and Robustness.
- **Fairness Shift Scatter Plots:** Visualizes rank alterations under controlled counterfactual identity perturbations.

## 2. Upstream Provenance & License
- **Official Documentation:** https://echarts.apache.org/
- **GitHub Repository:** https://github.com/apache/echarts
- **License:** Apache License 2.0 (Permissive open source).
- **Governance:** Apache Software Foundation.

## 3. Local Installation & Setup
Installed into `apps/web/`:
```powershell
npm install echarts echarts-for-react
```

## 4. Hardware Footprint & Resource Impact
- **Canvas / SVG Dual-Engine:** Highly optimized vector charts; smooth tooltip hover animations.
- **Bundle Size:** ~85 KB for core chart modules (scatter, line, bar, radar).

## 5. Architecture & Code Integration
Implemented in `apps/web/src/components/ParetoChart.tsx`:

```tsx
/**
 * Apache ECharts Pareto Frontier visualization plotting Ranking Quality (nDCG@10)
 * against Latency and Memory footprint.
 */
import React from 'react';
import ReactECharts from 'echarts-for-react';

interface ModelMetricPoint {
  model_name: string;
  ndcg10: number;
  latency_ms: number;
  ram_mb: number;
}

export const ParetoChart: React.FC<{ data: ModelMetricPoint[] }> = ({ data }) => {
  const option = {
    title: {
      text: 'Ranking Quality vs. Latency Trade-Off (Pareto Frontier)',
      textStyle: { fontSize: 14, color: '#475569' },
    },
    tooltip: {
      trigger: 'item',
      formatter: (params: any) => {
        const d = params.data;
        return `<strong>${d[3]}</strong><br/>nDCG@10: ${d[1]}<br/>Latency: ${d[0]} ms<br/>RAM: ${d[2]} MB`;
      },
    },
    xAxis: {
      type: 'value',
      name: 'Latency (ms)',
      splitLine: { lineStyle: { type: 'dashed', color: '#cbd5e1' } },
    },
    yAxis: {
      type: 'value',
      name: 'nDCG@10',
      min: 0.5,
      max: 1.0,
      splitLine: { lineStyle: { type: 'dashed', color: '#cbd5e1' } },
    },
    series: [
      {
        name: 'Models',
        type: 'scatter',
        symbolSize: (val: any) => Math.max(val[2] / 10, 12), // Bubble size proportional to RAM
        data: data.map(d => [d.latency_ms, d.ndcg10, d.ram_mb, d.model_name]),
        itemStyle: {
          color: '#3B82F6',
          shadowBlur: 8,
          shadowColor: 'rgba(59, 130, 246, 0.4)',
        },
      },
    ],
  };

  return (
    <div className="p-4 rounded-neu shadow-neu-raised dark:shadow-neu-dark-raised bg-neu-base-light dark:bg-neu-base-dark">
      <ReactECharts option={option} style={{ height: '380px', width: '100%' }} />
    </div>
  );
};
```

## 6. Failure Modes, Fallbacks & Edge Cases
- **Accessible Table Alternative:** Every ECharts chart is accompanied by an accessible markdown/HTML data table containing the exact numeric values to ensure complete accessibility for screen readers and exportable reports.
