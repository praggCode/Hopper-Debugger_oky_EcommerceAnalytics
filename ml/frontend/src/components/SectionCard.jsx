export default function SectionCard({ title, eyebrow, children, className = "" }) {
  return (
    <section className={`section-card ${className}`.trim()}>
      {eyebrow ? <div className="section-eyebrow">{eyebrow}</div> : null}
      <h2>{title}</h2>
      <div className="section-body">{children}</div>
    </section>
  );
}
