"use client";

import React, { useState } from "react";

type MatchData = {
  match_date: string;
  draw: string;
  round_name: string;
  p1_first_name: string;
  p1_last_name: string;
  p1_country: string;
  p2_first_name: string;
  p2_last_name: string;
  p2_country: string;
  tt_p1: number | "";
  tt_p2: number | "";
  bd_p1: number | "";
  bd_p2: number | "";
  sq_p1: number | "";
  sq_p2: number | "";
  tn_p1: number | "";
  tn_p2: number | "";
  winner_side: number | "";
};

const defaultMatch: MatchData = {
  match_date: new Date().toISOString().split("T")[0],
  draw: "Men A - Elite",
  round_name: "",
  p1_first_name: "",
  p1_last_name: "",
  p1_country: "",
  p2_first_name: "",
  p2_last_name: "",
  p2_country: "",
  tt_p1: "",
  tt_p2: "",
  bd_p1: "",
  bd_p2: "",
  sq_p1: "",
  sq_p2: "",
  tn_p1: "",
  tn_p2: "",
  winner_side: "",
};

export default function BulkAddMatchesPage() {
  const [password, setPassword] = useState("");
  const [tournamentName, setTournamentName] = useState("");
  const [matches, setMatches] = useState<MatchData[]>([{ ...defaultMatch }]);
  const [status, setStatus] = useState<{
    type: "idle" | "loading" | "success" | "error";
    message: string;
  }>({
    type: "idle",
    message: "",
  });

  const handleMatchChange = (
    index: number,
    field: keyof MatchData,
    value: string | number,
  ) => {
    const updatedMatches = [...matches];
    updatedMatches[index] = { ...updatedMatches[index], [field]: value };
    setMatches(updatedMatches);
  };

  const addMatch = () => {
    setMatches([...matches, { ...defaultMatch }]);
  };

  const removeMatch = (index: number) => {
    const updated = matches.filter((_, i) => i !== index);
    setMatches(updated);
  };

  const autoCalculateWinner = (index: number) => {
    const m = matches[index];
    const p1Total =
      (Number(m.tt_p1) || 0) +
      (Number(m.bd_p1) || 0) +
      (Number(m.sq_p1) || 0) +
      (Number(m.tn_p1) || 0);
    const p2Total =
      (Number(m.tt_p2) || 0) +
      (Number(m.bd_p2) || 0) +
      (Number(m.sq_p2) || 0) +
      (Number(m.tn_p2) || 0);

    if (p1Total > p2Total) handleMatchChange(index, "winner_side", 1.0);
    else if (p2Total > p1Total) handleMatchChange(index, "winner_side", 2.0);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setStatus({
      type: "loading",
      message: "Uploading matches and triggering pipeline...",
    });

    // Clean up empty strings to nulls where required by backend
    const cleanedMatches = matches.map((m) => ({
      ...m,
      tt_p1: m.tt_p1 === "" ? null : m.tt_p1,
      tt_p2: m.tt_p2 === "" ? null : m.tt_p2,
      bd_p1: m.bd_p1 === "" ? null : m.bd_p1,
      bd_p2: m.bd_p2 === "" ? null : m.bd_p2,
      sq_p1: m.sq_p1 === "" ? null : m.sq_p1,
      sq_p2: m.sq_p2 === "" ? null : m.sq_p2,
      tn_p1: m.tn_p1 === "" ? null : m.tn_p1,
      tn_p2: m.tn_p2 === "" ? null : m.tn_p2,
    }));

    const payload = {
      tournament_name: tournamentName,
      matches: cleanedMatches,
    };

    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
      const res = await fetch(`${apiUrl}/admin/matches/bulk`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "x-admin-secret": password,
          "x-upload-password": password,
        },
        body: JSON.stringify(payload),
      });

      const data = await res.json();

      if (!res.ok) {
        throw new Error(data.detail || "Failed to upload matches.");
      }

      setStatus({
        type: "success",
        message: `Successfully added ${data.matches_added} matches! ML Pipeline started in the background.`,
      });

      // Optionally clear the form after success
      // setMatches([{ ...defaultMatch }]);
      // setTournamentName("");
    } catch (err: any) {
      setStatus({ type: "error", message: err.message });
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 py-10 px-4 sm:px-6 lg:px-8 text-gray-900">
      <div className="max-w-5xl mx-auto">
        <div className="bg-white shadow sm:rounded-lg mb-8">
          <div className="px-4 py-5 border-b border-gray-200 sm:px-6">
            <h3 className="text-lg leading-6 font-medium text-gray-900">
              Bulk Add Matches
            </h3>
            <p className="mt-1 text-sm text-gray-500">
              Add multiple matches under a single tournament. Uploads to R2 and
              auto-retrains the model.
            </p>
          </div>

          <form onSubmit={handleSubmit} className="px-4 py-5 sm:px-6 space-y-6">
            {/* Global Settings */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 pb-6 border-b border-gray-200">
              <div>
                <label className="block text-sm font-medium text-gray-700">
                  Password (Upload or Admin)
                </label>
                <input
                  type="password"
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">
                  Tournament Name
                </label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Summer Open 2024"
                  value={tournamentName}
                  onChange={(e) => setTournamentName(e.target.value)}
                  className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                />
              </div>
            </div>

            {/* Matches List */}
            <div className="space-y-8">
              {matches.map((match, index) => (
                <div
                  key={index}
                  className="bg-gray-50 p-6 rounded-lg border border-gray-200 relative shadow-sm"
                >
                  <div className="absolute top-4 right-4 flex space-x-2">
                    <button
                      type="button"
                      onClick={() => autoCalculateWinner(index)}
                      className="text-xs text-blue-600 bg-blue-100 hover:bg-blue-200 px-2 py-1 rounded"
                    >
                      Auto-Calc Winner
                    </button>
                    {matches.length > 1 && (
                      <button
                        type="button"
                        onClick={() => removeMatch(index)}
                        className="text-xs text-red-600 bg-red-100 hover:bg-red-200 px-2 py-1 rounded"
                      >
                        Remove
                      </button>
                    )}
                  </div>

                  <h4 className="text-md font-semibold mb-4 text-gray-700">
                    Match #{index + 1}
                  </h4>

                  {/* Details Row */}
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
                    <div>
                      <label className="block text-xs font-medium text-gray-700">
                        Date (YYYY-MM-DD)
                      </label>
                      <input
                        type="date"
                        required
                        value={match.match_date}
                        onChange={(e) =>
                          handleMatchChange(index, "match_date", e.target.value)
                        }
                        className="mt-1 block w-full border border-gray-300 rounded shadow-sm py-1.5 px-2 text-sm"
                      />
                    </div>
                    <div>
                      <label className="block text-xs font-medium text-gray-700">
                        Draw
                      </label>
                      <input
                        type="text"
                        required
                        value={match.draw}
                        onChange={(e) =>
                          handleMatchChange(index, "draw", e.target.value)
                        }
                        className="mt-1 block w-full border border-gray-300 rounded shadow-sm py-1.5 px-2 text-sm"
                      />
                    </div>
                    <div>
                      <label className="block text-xs font-medium text-gray-700">
                        Round (Optional)
                      </label>
                      <input
                        type="text"
                        value={match.round_name}
                        onChange={(e) =>
                          handleMatchChange(index, "round_name", e.target.value)
                        }
                        className="mt-1 block w-full border border-gray-300 rounded shadow-sm py-1.5 px-2 text-sm"
                      />
                    </div>
                  </div>

                  {/* Players Row */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-4 border-t border-gray-200 pt-4">
                    {/* Player 1 */}
                    <div className="space-y-3">
                      <h5 className="text-sm font-semibold text-gray-600">
                        Player 1
                      </h5>
                      <div className="grid grid-cols-3 gap-2">
                        <input
                          type="text"
                          placeholder="First Name"
                          required
                          value={match.p1_first_name}
                          onChange={(e) =>
                            handleMatchChange(
                              index,
                              "p1_first_name",
                              e.target.value,
                            )
                          }
                          className="block w-full border border-gray-300 rounded shadow-sm py-1.5 px-2 text-sm"
                        />
                        <input
                          type="text"
                          placeholder="Last Name"
                          required
                          value={match.p1_last_name}
                          onChange={(e) =>
                            handleMatchChange(
                              index,
                              "p1_last_name",
                              e.target.value,
                            )
                          }
                          className="block w-full border border-gray-300 rounded shadow-sm py-1.5 px-2 text-sm"
                        />
                        <input
                          type="text"
                          placeholder="Country (SWE)"
                          required
                          value={match.p1_country}
                          onChange={(e) =>
                            handleMatchChange(
                              index,
                              "p1_country",
                              e.target.value,
                            )
                          }
                          className="block w-full border border-gray-300 rounded shadow-sm py-1.5 px-2 text-sm uppercase"
                        />
                      </div>
                    </div>
                    {/* Player 2 */}
                    <div className="space-y-3">
                      <h5 className="text-sm font-semibold text-gray-600">
                        Player 2
                      </h5>
                      <div className="grid grid-cols-3 gap-2">
                        <input
                          type="text"
                          placeholder="First Name"
                          required
                          value={match.p2_first_name}
                          onChange={(e) =>
                            handleMatchChange(
                              index,
                              "p2_first_name",
                              e.target.value,
                            )
                          }
                          className="block w-full border border-gray-300 rounded shadow-sm py-1.5 px-2 text-sm"
                        />
                        <input
                          type="text"
                          placeholder="Last Name"
                          required
                          value={match.p2_last_name}
                          onChange={(e) =>
                            handleMatchChange(
                              index,
                              "p2_last_name",
                              e.target.value,
                            )
                          }
                          className="block w-full border border-gray-300 rounded shadow-sm py-1.5 px-2 text-sm"
                        />
                        <input
                          type="text"
                          placeholder="Country (USA)"
                          required
                          value={match.p2_country}
                          onChange={(e) =>
                            handleMatchChange(
                              index,
                              "p2_country",
                              e.target.value,
                            )
                          }
                          className="block w-full border border-gray-300 rounded shadow-sm py-1.5 px-2 text-sm uppercase"
                        />
                      </div>
                    </div>
                  </div>

                  {/* Scores Row */}
                  <div className="border-t border-gray-200 pt-4 mb-4">
                    <h5 className="text-sm font-semibold text-gray-600 mb-3">
                      Scores (P1 - P2)
                    </h5>
                    <div className="grid grid-cols-2 md:grid-cols-5 gap-4 items-end">
                      {["tt", "bd", "sq", "tn"].map((sport) => (
                        <div
                          key={sport}
                          className="flex items-center space-x-1"
                        >
                          <span className="text-xs font-bold uppercase w-6">
                            {sport}
                          </span>
                          <input
                            type="number"
                            className="w-16 border border-gray-300 rounded py-1 text-center text-sm"
                            value={match[`${sport}_p1` as keyof MatchData]}
                            onChange={(e) =>
                              handleMatchChange(
                                index,
                                `${sport}_p1` as keyof MatchData,
                                e.target.value,
                              )
                            }
                          />
                          <span className="text-gray-500">-</span>
                          <input
                            type="number"
                            className="w-16 border border-gray-300 rounded py-1 text-center text-sm"
                            value={match[`${sport}_p2` as keyof MatchData]}
                            onChange={(e) =>
                              handleMatchChange(
                                index,
                                `${sport}_p2` as keyof MatchData,
                                e.target.value,
                              )
                            }
                          />
                        </div>
                      ))}

                      <div>
                        <label className="block text-xs font-bold text-gray-700 mb-1">
                          Winner
                        </label>
                        <select
                          required
                          value={match.winner_side}
                          onChange={(e) =>
                            handleMatchChange(
                              index,
                              "winner_side",
                              parseFloat(e.target.value),
                            )
                          }
                          className="w-full border border-gray-300 rounded shadow-sm py-1.5 px-2 text-sm bg-white"
                        >
                          <option value="" disabled>
                            Select
                          </option>
                          <option value={1.0}>P1</option>
                          <option value={2.0}>P2</option>
                        </select>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>

            {/* Controls */}
            <div className="flex items-center justify-between pt-4">
              <button
                type="button"
                onClick={addMatch}
                className="inline-flex items-center px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
              >
                + Add Another Match
              </button>

              <button
                type="submit"
                disabled={status.type === "loading"}
                className="inline-flex items-center px-6 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 disabled:opacity-50"
              >
                {status.type === "loading"
                  ? "Processing..."
                  : "Submit Tournament"}
              </button>
            </div>

            {/* Status Messages */}
            {status.message && (
              <div
                className={`p-4 rounded-md mt-4 ${
                  status.type === "error"
                    ? "bg-red-50 text-red-800 border border-red-200"
                    : status.type === "success"
                      ? "bg-green-50 text-green-800 border border-green-200"
                      : "bg-blue-50 text-blue-800 border border-blue-200"
                }`}
              >
                {status.message}
              </div>
            )}
          </form>
        </div>
      </div>
    </div>
  );
}
