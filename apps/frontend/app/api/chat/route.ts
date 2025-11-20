import { NextRequest } from "next/server";

export async function POST(req: NextRequest) {
  try {
    const body = await req.json();
    const { query } = body;

    if (!query) {
      throw new Error('No query provided');
    }

    const apiBaseUrl = process.env.API_BASE_URL || "http://localhost:8000";

    const queryResponse = await fetch(`${apiBaseUrl}/query`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ query }),
      signal: req.signal,
    });

    if (!queryResponse.ok) {
      throw new Error(`Backend API error: ${queryResponse.statusText}`);
    }

    const data = await queryResponse.json();

    return Response.json({ answer: data.answer });
  } catch (error) {
    console.error("Error in chat API:", error);
    return Response.json({ error: error instanceof Error ? error.message : "Unknown error" });
  }
}
