import fs from "node:fs";
import path from "node:path";

export function publicPathToAbsolute(filePath: string): string {
  return path.join(process.cwd(), "public", filePath.replace(/^\//, "").replace(/\//g, path.sep));
}

export function assertPublicAssetExists(filePath: string): void {
  const absolutePath = publicPathToAbsolute(filePath);

  if (!fs.existsSync(absolutePath)) {
    throw new Error(`素材缺失: ${filePath}`);
  }
}
