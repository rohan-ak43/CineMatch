import React from 'react';

const SentimentChart = ({ counts }) => {
    const colors = { positive: '#5cad7f', neutral: '#d4875a', negative: '#e05c5c', none: '#3a3840' };
    const labels = { positive: 'Positive', neutral: 'Neutral', negative: 'Negative', none: 'Unreviewed' };

    const total = Object.values(counts).reduce((a, b) => a + b, 0);
    if (!total) return null;

    const r = 48, cx = 60, cy = 60, stroke = 20;
    const circum = 2 * Math.PI * r;
    let offset = 0;

    const legendItems = [];
    const circles = [];

    Object.entries(counts).forEach(([key, val]) => {
        if (!val) return;
        const pct = val / total;
        const dash = pct * circum;
        const gap = circum - dash;

        circles.push(
            <circle
                key={key}
                cx={cx}
                cy={cy}
                r={r}
                fill="none"
                stroke={colors[key]}
                strokeWidth={stroke}
                strokeDasharray={`${dash} ${gap}`}
                strokeDashoffset={-offset * circum}
                transform={`rotate(-90 ${cx} ${cy})`}
            />
        );

        legendItems.push(
            <div key={key} className="legend-item">
                <div className="legend-dot" style={{ background: colors[key] }}></div>
                <span className="legend-label">{labels[key]}</span>
                <span className="legend-val">{val} ({(pct * 100).toFixed(0)}%)</span>
            </div>
        );

        offset += pct;
    });

    return (
        <div className="sentiment-chart">
            <div className="chart-title">Review Sentiment Breakdown</div>
            <div className="donut-wrap">
                <svg className="donut-svg" width="120" height="120" viewBox="0 0 120 120">
                    <circle cx="60" cy="60" r="48" fill="none" stroke="#1a1a2e" strokeWidth="20" />
                    {circles}
                </svg>
                <div className="donut-legend">{legendItems}</div>
            </div>
        </div>
    );
};

export default SentimentChart;
