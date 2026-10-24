// shared ui components
import { formatNumber } from './helpers.js';

// page layout with an optional sidebar
export function PageLayout({ title, description, aside, sidebar, sidebarTitle, children }) {
    let body;
    if (sidebar) {
        body = (
            <div className="page-grid">
                <aside className="filters" aria-label={sidebarTitle}>
                    <h2 className="filters-title">{sidebarTitle}</h2>
                    {sidebar}
                </aside>
                <div className="page-content">{children}</div>
            </div>
        );
    } else {
        body = (
            <div className="page-grid page-grid-full">
                <div className="page-content">{children}</div>
            </div>
        );
    }

    return (
        <>
            <div className="page-head">
                <div>
                    <h1 className="page-title">{title}</h1>
                    <p className="page-description">{description}</p>
                </div>
                {aside && <div className="page-aside">{aside}</div>}
            </div>
            {body}
        </>
    );
}

export function Panel({ title, subtitle, action, className, children }) {
    let panelClass = 'panel';
    if (className) {
        panelClass = `panel ${className}`;
    }

    return (
        <section className={panelClass}>
            {title && (
                <header className="panel-head">
                    <div>
                        <h2 className="panel-title">{title}</h2>
                        {subtitle && <p className="panel-sub">{subtitle}</p>}
                    </div>
                    {action}
                </header>
            )}
            {children}
        </section>
    );
}

// stat tile
export function Stat({ label, value, meta, tone }) {
    let metaClass = 'stat-meta';
    if (tone) {
        metaClass = `stat-meta tone-${tone}`;
    }

    return (
        <div className="stat">
            <span className="stat-label">{label}</span>
            <span className="stat-value" title={String(value)}>{value}</span>
            {meta && <span className={metaClass}>{meta}</span>}
        </div>
    );
}

// single choice chips
export function ChipGroup({ label, options, value, onChange }) {
    return (
        <fieldset className="filter-group">
            <legend className="filter-label">{label}</legend>
            <div className="chips">
                {options.map((option) => (
                    <button
                        key={option.value}
                        type="button"
                        className="chip"
                        aria-pressed={option.value === value}
                        onClick={() => onChange(option.value)}
                    >
                        {option.label}
                    </button>
                ))}
            </div>
        </fieldset>
    );
}

// multiple choice chips
export function MultiChipGroup({ label, hint, options, values, max, colors, onChange }) {
    function toggle(value) {
        const isSelected = values.includes(value);

        if (isSelected) {
            const remaining = values.filter((item) => item !== value);
            onChange(remaining);
            return;
        }

        if (values.length < max) {
            onChange([...values, value]);
        }
    }

    return (
        <fieldset className="filter-group">
            <legend className="filter-label">{label}</legend>
            <p className="filter-hint">{hint}</p>
            <div className="chips">
                {options.map((option) => {
                    const isSelected = values.includes(option.value);
                    const isFull = values.length >= max;

                    return (
                        <button
                            key={option.value}
                            type="button"
                            className="chip"
                            aria-pressed={isSelected}
                            disabled={!isSelected && isFull}
                            onClick={() => toggle(option.value)}
                        >
                            {isSelected && <span className="chip-dot" style={{ background: colors[option.value] }} />}
                            {option.label}
                        </button>
                    );
                })}
            </div>
        </fieldset>
    );
}

export function Loader() {
    return (
        <div className="status">
            <span className="spinner" />
            Loading
        </div>
    );
}

export function ErrorMessage({ text = 'Could not load this data. Please try again later.' }) {
    return <div className="status status-error">{text}</div>;
}

export function EmptyMessage({ title, text }) {
    return (
        <div className="status status-empty">
            <strong>{title}</strong>
            {text && <span>{text}</span>}
        </div>
    );
}

// chart tooltip
export function ChartTooltip({ active, payload, label, labelFormatter, valueFormatter }) {
    if (!active || !payload || payload.length === 0) {
        return null;
    }

    let title = label;
    if (labelFormatter) {
        title = labelFormatter(label);
    }

    let formatValue = formatNumber;
    if (valueFormatter) {
        formatValue = valueFormatter;
    }

    return (
        <div className="tooltip">
            {title && <div className="tooltip-title">{title}</div>}
            {payload.map((item) => (
                <div className="tooltip-row" key={item.dataKey}>
                    <span className="tooltip-name">
                        <span className="dot" style={{ background: item.color || item.payload.fill }} />
                        {item.name}
                    </span>
                    <span className="tooltip-value">{formatValue(item.value)}</span>
                </div>
            ))}
        </div>
    );
}

// job source tag
export function SourceTag() {
    return <span className="tag">Internshala</span>;
}
