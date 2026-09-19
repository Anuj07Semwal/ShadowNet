import { useEffect, useState, lazy, Suspense } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { getPersonProfile, type PersonProfile, type ProfileEntity } from "../api/persons";
import { useLanguage } from "../i18n/LanguageContext";
import { recordLabel } from "../utils/displayLabels";

const ProfileGraph = lazy(() => import("../components/person/ProfileGraph"));
const RiskProfile = lazy(() => import("../components/person/RiskProfile"));

function EntityList({ items, empty }: { items: ProfileEntity[]; empty: string }) {
	if (!items.length) return <p className="profile-empty">{empty}</p>;
	return <div className="profile-entity-list">{items.map((item) => <article className="profile-entity" key={item.id}><strong>{item.name || item.id}</strong><small>{item.type} · {item.id}</small>{Object.entries(item.properties).filter(([key]) => !["name", "person_id", "organization_id", "vehicle_id", "location_id", "phone_id", "account_id"].includes(key)).slice(0, 5).map(([key, itemValue]) => <span key={key}>{key.replaceAll("_", " ")}: {String(itemValue)}</span>)}</article>)}</div>;
}

export default function PersonInvestigation() {
	const { personId } = useParams();
	const navigate = useNavigate();
	const { t, language } = useLanguage();
	const [profile, setProfile] = useState<PersonProfile | null>(null);
	const [error, setError] = useState(false);

	useEffect(() => {
		let active = true;
		if (personId) getPersonProfile(personId).then((data) => { if (active) setProfile(data); }).catch(() => { if (active) setError(true); });
		return () => { active = false; };
	}, [personId]);

	if (error) return <div className="workspace-page"><Link to="/persons">{t("back")}</Link><p role="alert">{t("noResults")}</p></div>;
	if (!profile) return <div className="workspace-page"><p role="status">{t("working")}</p></div>;

	const basic = profile.basic;
	return <div className="workspace-page profile-page">
		<nav className="profile-breadcrumbs" aria-label="Breadcrumb"><Link to="/">Dashboard</Link><span>/</span><Link to="/persons">People</Link><span>/</span><strong>{recordLabel(profile.id, profile.name, language)}</strong></nav>
		<Link className="profile-back-link" to="/persons">← Back to People</Link>
		<header className="profile-header"><div><p className="eyebrow">Person profile</p><h1>{recordLabel(profile.id, profile.name, language)}</h1><p className="profile-id">Person ID: {profile.id}</p></div><div className="profile-summary"><strong>{profile.relationships.length}</strong><span>relationships</span><strong>{profile.transactions.length}</strong><span>transactions</span></div></header>
		<nav className="profile-section-nav" aria-label="Person profile sections"><a href="#overview">Overview</a><a href="#risk-profile">Risk &amp; anomalies</a><a href="#relationship-graph">Relationships</a><a href="#details">Details</a><a href="#transactions">Transactions</a><a href="#verified-cases">Verified cases</a></nav>
		<section className="profile-basic-grid" id="overview"><article className="data-panel"><h2>Basic information</h2><dl className="profile-fields">{["gender", "date_of_birth", "age", "city", "state", "country"].map((key) => basic[key] !== undefined && basic[key] !== null && <div key={key}><dt>{key.replaceAll("_", " ")}</dt><dd>{String(basic[key])}</dd></div>)}</dl></article><article className="data-panel"><h2>Data provenance</h2><dl className="profile-fields"><div><dt>Source</dt><dd>{String(basic.source ?? "Unknown")}</dd></div><div><dt>Confidence</dt><dd>{String(basic.confidence ?? "Not recorded")}</dd></div><div><dt>Community</dt><dd>{String(basic.community_id ?? "Unassigned")}</dd></div></dl></article></section>
		<Suspense fallback={<p className="state-panel" role="status">{t("working")}</p>}><RiskProfile risk={profile.risk} /></Suspense>
		<Suspense fallback={<p className="state-panel" role="status">{t("working")}</p>}><ProfileGraph profile={profile} onPersonSelect={(id) => navigate(`/persons/${encodeURIComponent(id)}`)} /></Suspense>
		<section className="profile-section-grid" id="details"><article className="data-panel"><h2>Contact information</h2><h3>Phone numbers</h3><EntityList items={profile.phones} empty="No phone records available." /><h3>Email activity</h3>{profile.emails.length ? <div className="profile-event-list">{profile.emails.map((email) => <div key={String(email.email_id)}><strong>{String(email.other_person_name ?? email.other_person_id)}</strong><span>{String(email.email_id)} · {String(email.timestamp ?? "")}</span></div>)}</div> : <p className="profile-empty">No email events available. Email addresses are not present in the source data.</p>}</article><article className="data-panel"><h2>Location</h2><EntityList items={profile.locations} empty="No location history available." /></article><article className="data-panel"><h2>Vehicles</h2><EntityList items={profile.vehicles} empty="No vehicle records available." /></article><article className="data-panel"><h2>Organizations</h2><EntityList items={profile.organizations} empty="No organization relationships available." /></article></section>
		<section className="data-panel" id="transactions"><h2>Transactions</h2>{profile.transactions.length ? <div className="profile-table-wrap"><table className="profile-table"><thead><tr><th>ID</th><th>Date/time</th><th>Amount</th><th>Type</th><th>Sender</th><th>Receiver</th></tr></thead><tbody>{profile.transactions.map((item) => <tr key={String(item.transaction_id)}><td>{String(item.transaction_id)}</td><td>{String(item.timestamp ?? "")}</td><td>{String(item.amount ?? "")}</td><td>{String(item.transaction_type ?? "")}</td><td>{String(item.sender_person_id ?? item.sender_account_id ?? "")}</td><td>{String(item.receiver_person_id ?? item.receiver_account_id ?? "")}</td></tr>)}</tbody></table></div> : <p className="profile-empty">No transactions available for this person.</p>}</section>
		<section className="data-panel" id="verified-cases"><h2>Relationships and verified cases</h2>{profile.relationships.length ? <div className="profile-relationship-list">{profile.relationships.map((item) => <div key={`${item.id}-${item.relationship}`}><strong>{item.name || item.id}</strong><span>{item.relationship} · {item.direction ?? "unknown direction"}{item.confidence !== null && item.confidence !== undefined ? ` · confidence ${item.confidence}` : ""}</span></div>)}</div> : <p className="profile-empty">No relationships available.</p>}</section>
	</div>;
}
