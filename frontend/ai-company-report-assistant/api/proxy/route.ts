import { NextResponse } from "next/server";

export async function POST(req: Request) {
  // forward the request body as-is
  const response = await fetch(process.env.API_URL!, {
    method: "POST",
    body: req.body, // stream FormData directly
    headers: req.headers, // forward headers if needed
  });

  const data = await response.json(); // parse backend response
  return NextResponse.json(data);
}
