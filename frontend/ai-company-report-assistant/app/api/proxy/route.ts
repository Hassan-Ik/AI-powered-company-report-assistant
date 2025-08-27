import { NextResponse } from "next/server";

export async function POST(req: Request) {
  // Convert incoming request to FormData if needed
  const formData = await req.formData(); // works if request is FormData

  // Forward to backend API
  const response = await fetch(process.env.API_URL!, {
    method: "POST",
    body: formData,
  });

  const data = await response.json(); // parse backend JSON response
  return NextResponse.json(data);
}
