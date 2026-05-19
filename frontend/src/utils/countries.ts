/** ISO 3166-1 alpha-2 codes used in demo config → display names */
const COUNTRY_NAMES: Record<string, string> = {
  IN: "India",
  TH: "Thailand",
  MY: "Malaysia",
  JP: "Japan",
  DE: "Germany",
  KR: "South Korea",
  US: "United States",
  CN: "China",
  GB: "United Kingdom",
};

export function countryName(
  code: string | undefined | null,
  resolvedName?: string | null
): string {
  if (resolvedName?.trim()) return resolvedName.trim();
  if (!code) return "—";
  const key = code.trim().toUpperCase();
  return COUNTRY_NAMES[key] ?? code;
}
