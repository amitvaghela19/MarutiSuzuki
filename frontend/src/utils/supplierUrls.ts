/** Map supplier id → public reference_url from snapshot/catalog. */
export function buildSupplierUrlMap(
  suppliers?: Array<{ id: string; reference_url?: string | null }> | null
): Record<string, string> {
  const map: Record<string, string> = {};
  for (const s of suppliers ?? []) {
    if (s.id && s.reference_url) {
      map[s.id] = s.reference_url;
    }
  }
  return map;
}

export function supplierReferenceUrl(
  id: string,
  urlMap: Record<string, string>,
  entity?: { reference_url?: string | null }
): string | undefined {
  return entity?.reference_url || urlMap[id] || undefined;
}
