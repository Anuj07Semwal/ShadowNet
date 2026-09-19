import type { Language } from "../i18n/LanguageContext";
export function recordLabel(id:string,name:string|null|undefined,language:Language):string {
 if(name && !/^(FIR record|Unknown entity)/i.test(name)) return name;
 const isPerson=/_P_/i.test(id);
 const prefix=isPerson?{en:"Person record",hi:"व्यक्ति रिकॉर्ड",mr:"व्यक्ती नोंद"}:{en:"Case record",hi:"केस रिकॉर्ड",mr:"प्रकरण नोंद"};
 const number=id.match(/(\d+)$/)?.[1];
 return prefix[language]+" "+(number?String(Number(number)):id);
}
export function readableText(text:string,language:Language):string {
 return text.replace(/\b(?:FIR|SYN)_P_\d+\b|\bFIR_\d+\b/g,id=>recordLabel(id,null,language));
}
