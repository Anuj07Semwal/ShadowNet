import { useEffect, useState } from "react";
import { Search, User } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { motion } from "framer-motion";

import { getPersons } from "../api/persons";
import type { Person } from "../types/person";

const containerVariants = {
  hidden: { opacity: 0 },
  show: { opacity: 1, transition: { staggerChildren: 0.05 } }
};

const rowVariants = {
  hidden: { opacity: 0, y: 10 },
  show: { opacity: 1, y: 0 }
};

export default function Persons() {
  const navigate = useNavigate();
  const [persons, setPersons] = useState<Person[]>([]);
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getPersons(200)
      .then((data) => {
        setPersons(data.persons);
        setLoading(false);
      })
      .catch((err) => {
        console.error(err);
        setLoading(false);
      });
  }, []);

  const filtered = persons.filter((person) => {
  const value = `${person.person_id} ${person.name || ""}`.toLowerCase();
    return value.includes(search.toLowerCase());
  });

  return (
    <div className="space-y-8 pb-10">
      <div>
        <h1 className="text-3xl font-bold tracking-tight text-[var(--color-foreground)]">Persons</h1>
        <p className="mt-2 text-[var(--color-muted-foreground)]">Search and investigate graph entities</p>
      </div>

      <div className="relative">
        <Search size={18} className="absolute left-4 top-1/2 -translate-y-1/2 text-[var(--color-muted-foreground)]" />
        <input
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Search by person ID or name..."
          className="w-full rounded-xl border border-[var(--color-border)] bg-[var(--color-card)] py-3.5 pl-12 pr-4 text-sm text-[var(--color-foreground)] outline-none placeholder:text-[var(--color-muted-foreground)] focus:border-[var(--color-primary)] focus:ring-2 focus:ring-[var(--color-primary)]/20 transition-all duration-300 shadow-sm"
        />
      </div>

      <div className="overflow-hidden rounded-xl border border-[var(--color-border)] bg-[var(--color-card)] shadow-sm">
        <table className="w-full text-left text-sm">
          <thead className="bg-[var(--color-muted)] text-[var(--color-muted-foreground)] border-b border-[var(--color-border)]">
            <tr className="uppercase tracking-wider text-xs">
              <th className="px-6 py-4 font-medium">Person</th>
              <th className="px-6 py-4 font-medium">Source</th>
              <th className="px-6 py-4 font-medium">Degree</th>
              <th className="px-6 py-4 font-medium">PageRank</th>
              <th className="px-6 py-4 font-medium">Community</th>
            </tr>
          </thead>
          
          <motion.tbody 
            variants={containerVariants}
            initial="hidden"
            animate="show"
            className="divide-y divide-[var(--color-border)]"
          >
            {loading ? (
              <tr>
                <td colSpan={5} className="p-8 text-center text-[var(--color-muted-foreground)]">
                  <div className="flex justify-center items-center gap-3">
                    <div className="h-4 w-4 rounded-full border-2 border-[var(--color-primary)] border-t-transparent animate-spin" />
                    Loading entities...
                  </div>
                </td>
              </tr>
            ) : filtered.length === 0 ? (
              <tr>
                <td colSpan={5} className="p-8 text-center text-[var(--color-muted-foreground)]">
                  No persons found matching your search.
                </td>
              </tr>
            ) : (
              filtered.map((person) => (
                <motion.tr
                  variants={rowVariants}
                  key={person.person_id}
                  onClick={() => navigate(`/persons/${encodeURIComponent(person.person_id)}`)}
                  className="cursor-pointer transition-colors hover:bg-[var(--color-muted)]"
                >
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-3">
                      <div className="rounded-lg border border-[var(--color-primary)]/30 bg-[var(--color-primary)]/10 p-2 text-[var(--color-primary)]">
                        <User size={16} />
                      </div>
                      <div>
                        <p className="text-sm font-medium text-[var(--color-foreground)]">{person.name || "Unknown entity"}</p>
                        <p className="font-mono text-xs text-[var(--color-muted-foreground)]">{person.person_id}</p>
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 text-[var(--color-muted-foreground)]">{person.source || "—"}</td>
                  <td className="px-6 py-4 text-[var(--color-foreground)] font-medium">{person.degree ?? "—"}</td>
                  <td className="px-6 py-4 font-mono text-xs text-[var(--color-muted-foreground)]">
                    {person.pagerank?.toFixed(6) || "—"}
                  </td>
                  <td className="px-6 py-4">
                    <span className="rounded-lg border border-[var(--color-primary)]/30 bg-[var(--color-primary)]/10 px-3 py-1 text-xs font-medium text-[var(--color-primary)]">
                      {person.community_id ?? "—"}
                    </span>
                  </td>
                </motion.tr>
              ))
            )}
          </motion.tbody>
        </table>
      </div>
    </div>
  );
}