import { readFileSync } from "fs";
import path from "path";
import { fileURLToPath } from "url";
import { satisfies } from "semver";

// Get the current file's directory (__dirname in ESM)
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Build full path to .nvmrc from current file
const nvmrcPath = path.resolve(__dirname, "../..", ".nvmrc");
let requiredNodeRange;

try {
    requiredNodeRange = readFileSync(nvmrcPath, "utf8").trim();
} catch (err) {
    console.error(`❌ Failed to read required Node version from ${nvmrcPath}`);
    console.error(`Reason: ${err.message}`);
    process.exit(1);
}

const currentNodeVersion = process.versions.node;

if (!satisfies(currentNodeVersion, requiredNodeRange)) {
    console.error(
        `❌ Error: The current Node.js version ${currentNodeVersion} does not satisfy the required version ${requiredNodeRange}.`
    );
    process.exit(1);
}
