import '../styles/theme.css';

export default function AuthCard({ title, subtitle, children }) {
  return (
    <div className="container">
      <div className="card">
        <div className="brand">
          <span className="dot" />
          <h1>CARE-U</h1>
        </div>
        <h2>{title}</h2>
        {subtitle && <p>{subtitle}</p>}
        {children}
      </div>
    </div>
  );
}
