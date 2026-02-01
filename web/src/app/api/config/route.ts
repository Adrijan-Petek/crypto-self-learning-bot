import { NextResponse } from "next/server";
import { getConfig } from "@/lib/repo-data";

export async function GET() {
  const config = await getConfig();
  return NextResponse.json(config);
}
