export default function BarViz({ items, maxValue = null, formatter = (value) => value }) {
  const computedMax = maxValue ?? Math.max(...items.map((item) => Math.abs(item.value)), 1);

  return (
    <div className="bar-viz">
      {items.map((item) => {
        const width = `${(Math.abs(item.value) / computedMax) * 100}%`;
        return (
          <div className="bar-row" key={item.label}>
            <div className="bar-label">{item.label}</div>
            <div className="bar-track">
              <div
                className={`bar-fill ${item.value >= 0 ? "positive" : "negative"}`}
                style={{ width }}
              />
            </div>
            <div className="bar-value">{formatter(item.value)}</div>
          </div>
        );
      })}
    </div>
  );
}
