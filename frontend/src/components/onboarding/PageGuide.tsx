import { AnimatePresence, motion } from "motion/react";
import { CircleHelp, X } from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import { useLocation } from "react-router-dom";
import { useLanguage, type Language } from "../../i18n/LanguageContext";

type Guide = { title: string; steps: string[] };
const copy: Record<Language, Record<string, Guide>> = {
  en: {
    "/documents": {title:"Section guide",steps:["Choose a file under 10 MB.","Validate it and check the result.","Upload metadata appears on your command desk."]},
    "/cases": {title:"Section guide",steps:["Choose a case from the list.","Read the source evidence beside it.","Keep original source wording unchanged."]},
    "/settings": {title:"Section guide",steps:["Choose a theme and language.","Change your password or replay the tutorial.","Confirm before deleting saved searches."]},
    "/": { title: "Using the command desk", steps: ["Review activity attached to your account.", "Start a focused investigation.", "Open a record to inspect its evidence."] },
    "/network": { title: "Generating a network map", steps: ["Choose a person record.", "Select Generate network map.", "Open a node to inspect its evidence."] },
    "/persons": { title: "Finding a person", steps: ["Search by name or visible record number.", "Choose a result to view its connections.", "Technical database IDs remain hidden."] },
    "/investigation": { title: "Asking an investigation question", steps: ["Write a plain-language question.", "Run the investigation.", "Verify graph and document evidence before action."] },
    default: { title: "How to use this section", steps: ["Use the page controls to narrow the evidence.", "Open a result to inspect its source.", "Return to the command desk at any time."] },
  },
  hi: {
    "/documents": {title:"भाग मार्गदर्शिका",steps:["10 MB से छोटी फाइल चुनें।","सत्यापित करें और परिणाम देखें।","अपलोड मेटाडेटा नियंत्रण कक्ष में दिखता है।"]},
    "/cases": {title:"भाग मार्गदर्शिका",steps:["सूची से केस चुनें।","साथ में मूल साक्ष्य पढ़ें।","मूल स्रोत पाठ अपरिवर्तित रखें।"]},
    "/settings": {title:"भाग मार्गदर्शिका",steps:["रूप और भाषा चुनें।","पासवर्ड बदलें या प्रशिक्षण फिर देखें।","खोज हटाने से पहले पुष्टि करें।"]},
    "/": { title: "नियंत्रण कक्ष का उपयोग", steps: ["अपने खाते से जुड़ी गतिविधि देखें।", "केंद्रित जांच शुरू करें।", "साक्ष्य देखने के लिए रिकॉर्ड खोलें।"] },
    "/network": { title: "नेटवर्क मानचित्र बनाएं", steps: ["व्यक्ति रिकॉर्ड चुनें।", "नेटवर्क मानचित्र बनाएं चुनें।", "साक्ष्य देखने के लिए नोड खोलें।"] },
    "/persons": { title: "व्यक्ति खोजें", steps: ["नाम या दिख रहे रिकॉर्ड क्रमांक से खोजें।", "संबंध देखने के लिए परिणाम चुनें।", "तकनीकी आईडी छिपी रहती हैं।"] },
    "/investigation": { title: "जांच प्रश्न पूछें", steps: ["सामान्य भाषा में प्रश्न लिखें।", "जांच चलाएं।", "कार्रवाई से पहले साक्ष्य जांचें।"] },
    default: { title: "इस भाग का उपयोग", steps: ["साक्ष्य सीमित करने के लिए नियंत्रण का उपयोग करें।", "स्रोत देखने के लिए परिणाम खोलें।", "नियंत्रण कक्ष पर लौटें।"] },
  },
};

export default function PageGuide() {
  const { pathname } = useLocation();
  const { language, t } = useLanguage();
  const [open, setOpen] = useState(() => sessionStorage.getItem(`shadownet-guide:${language}:${pathname}`) !== "seen");
  const guide = useMemo(() => copy[language][pathname] ?? copy[language].default, [language, pathname]);
  useEffect(() => {
    const key = `shadownet-guide:${language}:${pathname}`;
    sessionStorage.setItem(key, "seen");
  }, [language, pathname]);
  useEffect(() => {
    const show = () => setOpen(true);
    window.addEventListener("shadownet:open-page-guide", show);
    return () => window.removeEventListener("shadownet:open-page-guide", show);
  }, []);
  return <AnimatePresence>{open && <motion.aside className="page-guide" initial={{ opacity: 0, y: -8 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -8 }}>
    <CircleHelp size={21} /><div><strong>{guide.title}</strong><ol>{guide.steps.map((step) => <li key={step}>{step}</li>)}</ol></div>
    <button type="button" onClick={() => setOpen(false)} aria-label={t("close")}><X size={18} /></button>
  </motion.aside>}</AnimatePresence>;
}
