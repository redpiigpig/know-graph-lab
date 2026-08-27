import HEBREW_ORIGINAL_READER from "./hebrew";
import GREEK_ORIGINAL_READER from "./greek";
import { LATIN_ORIGINAL_READER } from "./latin";
import type {
  OriginalReaderLanguage,
  OriginalReaderSelection,
  OriginalReaderVolume,
} from "./types";

export const ORIGINAL_READER_VOLUMES: OriginalReaderVolume[] = [
  HEBREW_ORIGINAL_READER,
  GREEK_ORIGINAL_READER,
  LATIN_ORIGINAL_READER,
];

export function getOriginalReaderVolume(
  language: string,
): OriginalReaderVolume | undefined {
  return ORIGINAL_READER_VOLUMES.find((volume) => volume.slug === language);
}

export function getOriginalReaderSelection(
  language: string,
  selectionId: string,
): { volume: OriginalReaderVolume; selection: OriginalReaderSelection } | undefined {
  const volume = getOriginalReaderVolume(language);
  if (!volume) return undefined;
  const selection = volume.selections.find((item) => item.id === selectionId);
  return selection ? { volume, selection } : undefined;
}

export function isOriginalReaderLanguage(
  language: string,
): language is OriginalReaderLanguage {
  return language === "hbo" || language === "grc" || language === "la";
}
