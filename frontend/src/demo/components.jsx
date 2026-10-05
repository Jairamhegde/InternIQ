// Small building blocks used by more than one page.
// Their styles live in DemoApp.css.
import { formatNumber } from './helpers.js';

const ICON_PATHS = {
    overview: 'M3 13h8V3H3v10Zm0 8h8v-6H3v6Zm10 0h8V11h-8v10Zm0-18v6h8V3h-8Z',
    compare: 'M4 20V10m6 10V4m6 16v-7m4 7H2',
    trend: 'M3 17l6-6 4 4 8-8m0 0h-6m6 0v6',
    gap: 'M9 12l2 2 4-4m6 2a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z',
    ai: 'M12 3v2m0 14v2M5 12H3m18 0h-2M7 7 5.6 5.6m12.8 12.8L17 17M7 17l-1.4 1.4M18.4 5.6 17 7M12 8a4 4 0 1 0 0 8 4 4 0 0 0 0-8Z',
    send: 'M5 12h14m-6-6 6 6-6 6',
    upload: 'M12 16V4m0 0-4 4m4-4 4 4M4 16v3a1 1 0 0 0 1 1h14a1 1 0 0 0 1-1v-3',
    file: 'M14 3H6a1 1 0 0 0-1 1v16a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1V8l-5-5Zm0 0v5h5',
    external: 'M14 4h6v6m0-6L10 14M18 14v5a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1V7a1 1 0 0 1 1-1h5',
    check: 'M5 12l5 5L20 7',
    close: 'M6 6l12 12M18 6 6 18',
    up: 'M12 19V5m0 0-6 6m6-6 6 6',
    down: 'M12 5v14m0 0-6-6m6 6 6-6',
    menu: 'M4 6h16M4 12h16M4 18h16',
};

export function Icon({ name, size = 18 }) {
    return (
        <svg
            className="icon"
            width={size}
            height={size}
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="1.7"
            strokeLinecap="round"
            strokeLinejoin="round"
            aria-hidden="true"
        >
            <path d={ICON_PATHS[name]} />
        </svg>
    );
}

export function PageHeader({ title, description, children }) {
    return (
        <div className="page-header">
            <div>
                <h1 className="page-title">{title}</h1>
                <p className="page-description">{description}</p>
            </div>
            <div className="page-controls">{children}</div>
        </div>
    );
}

export function Card({ title, subtitle, action, children, className = '' }) {
    return (
        <section className={`card ${className}`}>
            <header className="card-header">
                <div>
                    <h3 className="card-title">{title}</h3>
                    {subtitle && <p className="card-subtitle">{subtitle}</p>}
                </div>
                {action}
            </header>
            {children}
        </section>
    );
}

export function StatTile({ label, value, meta, change, badge = false }) {
    return (
        <div className="stat-tile">
            <span className="stat-tile-label">{label}</span>
            <span className="stat-tile-value" title={value}>{value}</span>
            <div className="stat-tile-meta">
                {change !== undefined && <Change value={change} />}
                {meta && <span className={badge ? 'stat-tile-badge' : undefined}>{meta}</span>}
            </div>
        </div>
    );
}

// Green badge for growth, red badge for decline.
function Change({ value }) {
    let direction = 'flat';
    if (value > 0) {
        direction = 'up';
    }
    if (value < 0) {
        direction = 'down';
    }

    return (
        <span className={`change change-${direction}`}>
            {direction !== 'flat' && <Icon name={direction} size={12} />}
            {Math.abs(value)}%
        </span>
    );
}

export function Loader() {
    return (
        <div className="status-box">
            <span className="spinner" />
            Loading...
        </div>
    );
}

export function ErrorMessage({ text = 'Could not load this data. Please try again later.' }) {
    return <div className="status-box status-error">{text}</div>;
}

export function EmptyMessage({ text = 'No data available.' }) {
    return <div className="status-box">{text}</div>;
}

// Tooltip shared by all charts. labelFormatter turns raw API text into readable text.
export function ChartTooltip({ active, payload, label, labelFormatter, valueSuffix = '' }) {
    if (!active || !payload || payload.length === 0) {
        return null;
    }

    let title = label;
    if (labelFormatter) {
        title = labelFormatter(label);
    }

    return (
        <div className="chart-tooltip">
            {title && <div className="chart-tooltip-label">{title}</div>}
            {payload.map((item) => (
                <div className="chart-tooltip-row" key={item.dataKey}>
                    <span className="chart-tooltip-name">
                        <span className="swatch" style={{ background: item.color || item.payload.fill }} />
                        {item.name}
                    </span>
                    <span className="chart-tooltip-value">
                        {formatNumber(item.value)}{valueSuffix}
                    </span>
                </div>
            ))}
        </div>
    );
}
