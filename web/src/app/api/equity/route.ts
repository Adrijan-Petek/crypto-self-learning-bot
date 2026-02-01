import { NextResponse } from "next/server";
import { getEquityCurve } from "@/lib/repo-data";

export async function GET() {
  const equity = await getEquityCurve(1200);
  return NextResponse.json(equity);
}
