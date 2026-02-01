import { NextResponse } from "next/server";
import { getHistory } from "@/lib/repo-data";

export async function GET() {
  const history = await getHistory(200);
  return NextResponse.json(history);
}
