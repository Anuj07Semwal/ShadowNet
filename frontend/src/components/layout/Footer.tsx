import { Link } from "react-router-dom";
import { useLanguage } from "../../i18n/LanguageContext";

export default function Footer() {
  const { t } = useLanguage();
  return (
    <footer className="site-footer">
      <nav aria-label="Legal links">
        <Link to="/privacy">{t("privacy")}</Link>
        <Link to="/terms">{t("terms")}</Link>
        <Link to="/cookies">{t("cookies")}</Link>
      </nav>
    </footer>
  );
}
