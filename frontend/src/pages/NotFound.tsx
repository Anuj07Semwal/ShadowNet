import {Link} from "react-router-dom";
import {useLanguage} from "../i18n/LanguageContext";
export default function NotFound(){const {t}=useLanguage();return <section className="workspace-page"><h1>404</h1><p>{t("notFound")}</p><Link className="primary-action" to="/">{t("dashboard")}</Link></section>;}
