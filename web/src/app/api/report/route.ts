import { NextResponse } from "next/server";
import { getReport } from "@/lib/repo-data";

export async function GET() {
  const report = await getReport();
  return NextResponse.json(report);
}
