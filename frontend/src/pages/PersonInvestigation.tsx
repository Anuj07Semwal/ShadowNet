import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { User, AlertTriangle, ArrowLeftRight, Activity, Network } from "lucide-react";
import { motion, type Variants } from "framer-motion";
import { getPersonNetwork } from "../api/persons";
import type { PersonNetwork } from "../types/person";

const containerVariants: Variants = {
  hidden: { opacity: 0 },
  show: { opacity: 1, transition: { staggerChildren: 0.1 } }
};

const itemVariants: Variants = {
  hidden: { opacity: 0, y: 20 },
  show: { opacity: 1, y: 0, transition: { type: "spring", stiffness: 300, damping: 24 } }
};

export default function PersonInvestigation() {
 const params = useParams<{ personId?: string; id?: string }>();
 const id = params.personId ?? params.id;
  const navigate = useNavigate();

  const [details, setDetails] = useState<PersonNetwork | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!id) return;
    getPersonNetwork(id)
      .then((data) => setDetails(data))
      .catch((err) => {
        console.error(err);
        setError("Unable to retrieve person details.");
      });
  }, [id]);

  if (error) {
    return (
      <div className="flex h-full items-center justify-center">
        <div className="border border-[var(--color-destructive)]/30 bg-[var(--color-destructive)]/10 p-8 rounded-xl text-center shadow-sm">
          <AlertTriangle className="mx-auto mb-4 text-[var(--color-destructive)]" size={32} />
          <p className="font-semibold text-[var(--color-destructive)]">{error}</p>
          <button
            onClick={() => navigate("/persons")}
            className="mt-6 rounded-lg bg-[var(--color-destructive)]/20 px-4 py-2 text-sm font-medium text-[var(--color-destructive)] hover:bg-[var(--color-destructive)]/30 transition-colors"
          >
            Back to Persons
          </button>
        </div>
      </div>
    );
  }

  if (!details) {
    return (
      <div className="flex min-h-[60vh] items-center justify-center">
        <div className="text-xl font-semibold text-[var(--color-muted-foreground)] flex items-center gap-3">
          <div className="h-5 w-5 rounded-full border-2 border-[var(--color-primary)] border-t-transparent animate-spin" />
          Retrieving profile...
        </div>
      </div>
    );
  }

  const { connections } = details;

  return (
    <div className="mx-auto max-w-6xl space-y-8 pb-10">
      <div className="flex items-start justify-between">
        <div>
          <div className="flex items-center gap-3 text-sm font-medium text-[var(--color-primary)] mb-3">
            <button onClick={() => navigate("/persons")} className="hover:underline">Persons</button>
            <span>/</span>
            <span className="text-[var(--color-muted-foreground)] uppercase tracking-wide">{id}</span>
          </div>
          <h1 className="text-3xl font-bold tracking-tight text-[var(--color-foreground)]">
            {details.name || "Unknown Entity"}
          </h1>
          <p className="mt-2 font-mono text-sm text-[var(--color-muted-foreground)]">ID: {details.person_id}</p>
        </div>
      </div>

      <motion.div 
        variants={containerVariants}
        initial="hidden"
        animate="show"
        className="grid gap-6 md:grid-cols-3"
      >
        <motion.div variants={itemVariants} className="rounded-xl border border-[var(--color-border)] bg-[var(--color-card)] p-6 shadow-sm">
          <div className="flex items-center gap-3 text-[var(--color-primary)] mb-4">
            <Network size={20} />
            <h2 className="font-semibold text-[var(--color-foreground)]">Graph Metrics</h2>
          </div>
          <div className="space-y-4 text-sm mt-6">
            <div className="flex justify-between border-b border-[var(--color-border)] pb-2">
              <span className="text-[var(--color-muted-foreground)]">Degree</span>
              <span className="font-medium text-[var(--color-foreground)]">{details.degree ?? "—"}</span>
            </div>
            <div className="flex justify-between border-b border-[var(--color-border)] pb-2">
              <span className="text-[var(--color-muted-foreground)]">PageRank</span>
              <span className="font-mono text-[var(--color-foreground)]">{details.pagerank?.toFixed(6) ?? "—"}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-[var(--color-muted-foreground)]">Community</span>
              <span className="rounded-lg border border-[var(--color-primary)]/30 bg-[var(--color-primary)]/10 px-2 py-0.5 text-xs font-medium text-[var(--color-primary)]">
                {details.community ?? "—"}
              </span>
            </div>
          </div>
        </motion.div>

        <motion.div variants={itemVariants} className="md:col-span-2 rounded-xl border border-[var(--color-border)] bg-[var(--color-card)] p-6 shadow-sm">
          <div className="flex items-center gap-3 text-[var(--color-foreground)] border-b border-[var(--color-border)] pb-4 mb-4">
            <ArrowLeftRight size={20} className="text-emerald-500" />
            <h2 className="font-semibold text-[var(--color-foreground)]">Known Relationships ({connections.length})</h2>
          </div>

          <div className="mt-4 max-h-[300px] overflow-y-auto pr-2">
            {connections.length === 0 ? (
              <p className="py-8 text-center text-sm text-[var(--color-muted-foreground)]">
                No relationships recorded in the graph.
              </p>
            ) : (
              <div className="space-y-3">
                {connections.map((conn, index) => {
                  const isTransaction = conn.type.includes("TRANSACTED") || conn.relationship.toLowerCase().includes("transact");

                  return (
                    <div
                      key={index}
                      className="flex items-center justify-between rounded-xl border border-[var(--color-border)] bg-[var(--color-muted)] p-4 transition-colors hover:border-[var(--color-primary)]/40 hover:bg-[var(--color-card)] shadow-sm"
                    >
                      <div className="flex items-center gap-4">
                        <div className="rounded-lg border border-[var(--color-primary)]/20 bg-[var(--color-primary)]/10 p-2 text-[var(--color-primary)]">
                          {isTransaction ? <Activity size={16} /> : <User size={16} />}
                        </div>
                        <div>
                          <p className="text-sm font-semibold text-[var(--color-foreground)]">
                            {conn.type.join(", ") || "Related"}
                          </p>
                          <button 
                            onClick={() => navigate(`/persons/${encodeURIComponent(conn.id)}`)}
                            className="text-xs font-mono text-[var(--color-primary)] hover:underline mt-0.5 inline-block"
                          >
                            {conn.id} {conn.name ? `(${conn.name})` : ""}
                          </button>
                        </div>
                      </div>

                      <div className="text-right">
                        <span className="rounded-md border border-[var(--color-border)] bg-white px-2.5 py-1 text-[10px] font-medium uppercase tracking-wide text-[var(--color-muted-foreground)]">
                          {conn.relationship || "Connection"}
                        </span>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        </motion.div>
      </motion.div>
    </div>
  );
}