export function isImage(mime: string): boolean {
  if (mime === null || mime === undefined || typeof mime !== "string") {
    return false;
  }
  return mime.trim().toLowerCase().startsWith("image/");
}

export function isVideo(mime: string): boolean {
  if (mime === null || mime === undefined || typeof mime !== "string") {
    return false;
  }
  return mime.trim().toLowerCase().startsWith("video/");
}
