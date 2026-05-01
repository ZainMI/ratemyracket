"use client";

import { useRouter } from "next/navigation";
import PlayerSearch from "@/components/PlayerSearch";
import type { Player } from "@/lib/types";

export default function PlayersPage() {
  const router = useRouter();

  function goToPlayer(player: Player) {
    router.push(`/players/${encodeURIComponent(player.player_key)}`);
  }

  return (
    <div className="space-y-8">
      <header>
        <h1 className="text-4xl font-bold text-gray-950">Players</h1>
        <p className="mt-2 text-gray-600">
          Search players by name and country.
        </p>
      </header>

      <PlayerSearch label="Find a player" onSelect={goToPlayer} />
    </div>
  );
}
