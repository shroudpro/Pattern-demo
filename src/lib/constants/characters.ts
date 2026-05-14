import { DEMO_CHARACTER_KEYS } from "@/lib/demo/static-demo-data";

export const S_GRADE_CHARACTERS = DEMO_CHARACTER_KEYS;
export const RECOMMENDED_CHARACTERS = DEMO_CHARACTER_KEYS;

export function isSingleCharacter(input: string): boolean {
  return input.trim().length === 1;
}
