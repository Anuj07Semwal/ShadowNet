export default function BrandLogo({ className = "" }: { className?: string }) {
  return (
    <span className={`theme-brand-logo ${className}`} aria-hidden="true">
      <img className="logo-for-light" src="/shadownet-logo-light.png" alt="" />
      <img className="logo-for-dark" src="/shadownet-logo-dark.png" alt="" />
    </span>
  );
}
