const API = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

export async function searchPlayers(q: string) {
  const res = await fetch(`${API}/players/search?q=${encodeURIComponent(q)}`);
  const data = await res.json().catch(() => ({}));

  if (!res.ok) {
    console.error("Player search failed:", data);
    return [];
  }

  return Array.isArray(data) ? data : [];
}

export async function predictMatch(player1Key: string, player2Key: string) {
  const res = await fetch(`${API}/predict`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      player1_key: player1Key,
      player2_key: player2Key,
    }),
  });

  const data = await res.json().catch(() => ({}));

  if (!res.ok) {
    throw new Error(data.detail || "Prediction failed");
  }

  return data;
}

export async function getPlayerRatings(playerKey: string) {
  const res = await fetch(
    `${API}/players/${encodeURIComponent(playerKey)}/ratings`,
  );

  const data = await res.json().catch(() => ({}));

  if (!res.ok) {
    throw new Error(data.detail || "Failed to load ratings");
  }

  return data;
}

export async function getPlayerMatches(playerKey: string) {
  const res = await fetch(
    `${API}/players/${encodeURIComponent(playerKey)}/matches`,
  );

  const data = await res.json().catch(() => []);

  if (!res.ok) {
    console.error("Failed to load matches:", data);
    return [];
  }

  return Array.isArray(data) ? data : [];
}

export async function getLeaderboard(
  sport: string = "overall",
  gender: string = "male",
  limit = 10000,
) {
  const res = await fetch(
    `${API}/players/leaderboard?sport=${encodeURIComponent(
      sport,
    )}&gender=${encodeURIComponent(gender)}&limit=${limit}`,
  );

  const data = await res.json().catch(() => []);

  if (!res.ok) {
    console.error("Failed to load leaderboard:", data);
    return [];
  }

  return Array.isArray(data) ? data : [];
}
