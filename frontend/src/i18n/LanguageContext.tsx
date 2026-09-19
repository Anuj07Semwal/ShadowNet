import { createContext, useContext, useEffect, useMemo, useState, type ReactNode } from "react";
import { messages } from "./messages";
export type Language = "en" | "hi";
// eslint-disable-next-line react-refresh/only-export-components
export const LANGUAGE_OPTIONS: {code: Language; label: string}[] = [{code:"en",label:"English"},{code:"hi",label:"हिन्दी"}];
export type MessageKey = string;
const LanguageContext = createContext<{language:Language;setLanguage:(value:Language)=>void;t:(key:MessageKey)=>string}|null>(null);
export function LanguageProvider({children}:{children:ReactNode}) {
 const [language,setLanguage]=useState<Language>(()=>{const saved=localStorage.getItem("shadownet-language"); return saved==="hi" ? saved : "en";});
 useEffect(()=>{localStorage.setItem("shadownet-language",language);document.documentElement.lang=language;document.title="ShadowNet";},[language]);
 const value=useMemo(()=>({language,setLanguage,t:(key:string)=>messages[key]?.[language==="en"?0:1] ?? key}),[language]);
 return <LanguageContext.Provider value={value}>{children}</LanguageContext.Provider>;
}
// eslint-disable-next-line react-refresh/only-export-components
export function useLanguage(){const value=useContext(LanguageContext);if(!value)throw new Error("LanguageProvider required");return value;}
