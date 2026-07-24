import type { SourceCard } from "./run-engine";

type OrganicResult = {
  link?: unknown;
  title?: unknown;
  description?: unknown;
  global_rank?: unknown;
};

type BrightDataResponse = { organic?: OrganicResult[] };

export type BrightDataConfig = {
  token: string;
  zone: string;
  country?: string;
  language?: string;
};

export class BrightDataConfigurationError extends Error {}

function parsePayload(payload: unknown): BrightDataResponse {
  return typeof payload === "string"
    ? (JSON.parse(payload) as BrightDataResponse)
    : ((payload ?? {}) as BrightDataResponse);
}

export function brightDataConfigFromEnv(
  env: NodeJS.ProcessEnv = process.env,
): BrightDataConfig {
  const token = env.BRIGHT_DATA_API_TOKEN?.trim() ?? "";
  const zone = env.BRIGHT_DATA_SERP_ZONE?.trim() ?? "";
  if (!token || !zone) {
    throw new BrightDataConfigurationError(
      "Set BRIGHT_DATA_API_TOKEN and BRIGHT_DATA_SERP_ZONE.",
    );
  }
  return {
    token,
    zone,
    country: env.BRIGHT_DATA_COUNTRY?.trim() || "us",
    language: env.BRIGHT_DATA_LANGUAGE?.trim() || "en",
  };
}

export async function searchBrightData(
  objective: string,
  config: BrightDataConfig,
  fetchImpl: typeof fetch = fetch,
): Promise<SourceCard[]> {
  const query = objective.replace(/\s+/g, " ").trim();
  if (!query) throw new Error("A search objective is required.");

  const searchUrl = new URL("https://www.google.com/search");
  searchUrl.searchParams.set("q", query);
  searchUrl.searchParams.set("hl", config.language ?? "en");
  searchUrl.searchParams.set("gl", config.country ?? "us");

  const response = await fetchImpl("https://api.brightdata.com/request", {
    method: "POST",
    headers: {
      authorization: `Bearer ${config.token}`,
      "content-type": "application/json",
    },
    body: JSON.stringify({
      zone: config.zone,
      url: searchUrl.toString(),
      format: "raw",
      data_format: "parsed_light",
    }),
    signal: AbortSignal.timeout(25_000),
  });

  if (!response.ok) {
    const detail = (await response.text()).slice(0, 240);
    throw new Error(`Bright Data request failed (${response.status}): ${detail}`);
  }

  const payload = parsePayload(await response.json());
  const seen = new Set<string>();

  return (payload.organic ?? [])
    .flatMap((item): SourceCard[] => {
      if (typeof item.link !== "string" || typeof item.title !== "string") return [];
      let url: URL;
      try {
        url = new URL(item.link);
      } catch {
        return [];
      }
      if (url.protocol !== "https:" || seen.has(url.href)) return [];
      seen.add(url.href);

      return [{
        domain: url.hostname.replace(/^www\./, ""),
        age: "live",
        title: item.title.slice(0, 220),
        kind: "LIVE",
        url: url.href,
        snippet:
          typeof item.description === "string" ? item.description.slice(0, 360) : undefined,
        rank: typeof item.global_rank === "number" ? item.global_rank : undefined,
      }];
    })
    .slice(0, 8);
}
