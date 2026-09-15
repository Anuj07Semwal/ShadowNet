import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { motion, type Variants } from "framer-motion";

import {
  getNetworkStats,
  getTopPersons,
  type NetworkPerson,
  type NetworkStatsResponse,
} from "../api/network";

const containerVariants: Variants = {
  hidden: { opacity: 0 },
  show: {
    opacity: 1,
    transition: { staggerChildren: 0.1 }
  }
};

const itemVariants: Variants = {
  hidden: { opacity: 0, y: 20 },
  show: { opacity: 1, y: 0, transition: { type: "spring", stiffness: 300, damping: 24 } }
};

export default function Dashboard() {
  const navigate = useNavigate();

  const [stats, setStats] = useState<NetworkStatsResponse | null>(null);
  const [topPersons, setTopPersons] = useState<NetworkPerson[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadDashboard() {
      try {
        const network = await getNetworkStats();
        const top = await getTopPersons("pagerank", 10);
        setStats(network);
        setTopPersons(top.persons ?? []);
      } catch (err) {
        console.error("Dashboard error:", err);
        setError("Unable to load CNAS backend");
      }
    }
    void loadDashboard();
  }, []);

  if (error) {
    return (
      <div className="flex h-full items-center justify-center p-10">
        <div className="border border-[var(--color-destructive)]/30 bg-[var(--color-destructive)]/10 p-6 rounded-xl text-[var(--color-destructive)] backdrop-blur-sm max-w-lg w-full text-center shadow-sm">
          <h2 className="text-xl font-bold">CNAS Backend Error</h2>
          <p className="mt-2 text-[var(--color-destructive)]/80">{error}</p>
          <p className="mt-4 text-sm text-[var(--color-destructive)]/60">Make sure the FastAPI backend is running.</p>
        </div>
      </div>
    );
  }

  if (!stats) {
    return (
      <div className="flex min-h-[60vh] items-center justify-center">
        <div className="text-xl font-semibold text-[var(--color-muted-foreground)] flex items-center gap-3">
          <div className="h-5 w-5 rounded-full border-2 border-[var(--color-primary)] border-t-transparent animate-spin" />
          Loading CNAS...
        </div>
      </div>
    );
  }

  return (
    <div className="pb-10">
      <div className="mb-8">
        <h1 className="text-3xl font-bold tracking-tight text-[var(--color-foreground)]">
          CNAS Command Center
        </h1>
        <p className="mt-2 text-[var(--color-muted-foreground)]">
          Criminal Network Intelligence Platform
        </p>
      </div>

      <motion.div 
        variants={containerVariants}
        initial="hidden"
        animate="show"
        className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-4"
      >
        <StatCard title="Total Nodes" value={stats.total_nodes} />
        <StatCard title="Persons" value={stats.entities?.Person} />
        <StatCard title="FIRs" value={stats.entities?.FIR} />
        <StatCard title="Transactions" value={stats.relationships?.TRANSFERRED_MONEY} />
      </motion.div>

      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4, duration: 0.4 }}
        className="mt-10"
      >
        <div className="mb-4 flex items-center justify-between">
          <div>
            <h2 className="text-xl font-bold text-[var(--color-foreground)]">Top Network Actors</h2>
            <p className="text-sm text-[var(--color-muted-foreground)]">Ranked by PageRank</p>
          </div>
          <button
            onClick={() => navigate("/network")}
            className="bg-[var(--color-primary)]/10 border border-[var(--color-primary)]/20 px-4 py-2 text-sm font-medium text-[var(--color-primary)] hover:bg-[var(--color-primary)] hover:text-white rounded-lg transition-all duration-300 shadow-sm"
          >
            Open Network Explorer
          </button>
        </div>

        <div className="overflow-hidden rounded-xl border border-[var(--color-border)] bg-[var(--color-card)] shadow-sm">
          <table className="w-full text-left text-sm">
            <thead className="bg-[var(--color-muted)] text-[var(--color-muted-foreground)] border-b border-[var(--color-border)]">
              <tr>
                <th className="p-4 font-medium border-b border-[var(--color-border)]">Person ID</th>
                <th className="p-4 font-medium border-b border-[var(--color-border)]">Degree</th>
                <th className="p-4 font-medium border-b border-[var(--color-border)]">PageRank</th>
                <th className="p-4 font-medium border-b border-[var(--color-border)]">Community</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[var(--color-border)]">
              {topPersons.length === 0 ? (
                <tr>
                  <td colSpan={4} className="p-8 text-center text-[var(--color-muted-foreground)]">
                    No persons found.
                  </td>
                </tr>
              ) : (
                topPersons.map((person) => (
                  <tr
                    key={person.person_id}
                    onClick={() => navigate(`/persons/${person.person_id}`)}
                    className="cursor-pointer transition-colors hover:bg-[var(--color-muted)]"
                  >
                    <td className="p-4 font-medium text-[var(--color-foreground)]">{person.person_id}</td>
                    <td className="p-4 text-[var(--color-foreground)]">{person.degree ?? 0}</td>
                    <td className="p-4 text-[var(--color-muted-foreground)] font-mono text-xs">
                      {typeof person.pagerank === "number" ? person.pagerank.toFixed(6) : "0.000000"}
                    </td>
                    <td className="p-4">
                       <span className="rounded-lg border border-[var(--color-primary)]/30 bg-[var(--color-primary)]/10 px-3 py-1 text-xs font-medium text-[var(--color-primary)]">
                         {person.community_id ?? "N/A"}
                       </span>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </motion.div>
    </div>
  );
}

function StatCard({ title, value }: { title: string; value?: number | string | null }) {
  return (
    <motion.div 
      variants={itemVariants}
      className="rounded-xl border border-[var(--color-border)] bg-[var(--color-card)] p-6 hover:border-[var(--color-primary)]/30 transition-all duration-300 relative overflow-hidden group shadow-sm hover:shadow-md"
    >
      <div className="absolute -right-10 -top-10 h-32 w-32 rounded-full bg-[var(--color-primary)]/5 blur-3xl group-hover:bg-[var(--color-primary)]/15 transition-colors duration-500" />
      <p className="text-sm font-medium text-[var(--color-muted-foreground)]">{title}</p>
      <h2 className="mt-3 text-4xl font-bold tracking-tight text-[var(--color-foreground)]">{value ?? 0}</h2>
    </motion.div>
  );
}
